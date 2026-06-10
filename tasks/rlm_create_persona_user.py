"""
CumulusCI task to create a persona user from a definition file.

On scratch orgs this wraps `sf org create user --definition-file <path>
--set-alias <alias> --set-unique-username --target-org <username>`.

On non-scratch orgs (production, developer edition, sandbox) the scratch-only
`sf org create user` CLI command raises NonScratchOrgError, so this task falls
back to inserting a standard ``User`` sObject via the REST API (resolving
``ProfileId`` from the definition's ``profileName``) and then setting a password
via the REST User password sub-resource. The password value is never logged
(audit-safe).
"""
import json
import os
import secrets
import string
import subprocess
import uuid
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception


class CreatePersonaUser(BaseTask):
    """Create a persona user from a JSON definition file.

    Scratch orgs use the ``sf org create user`` CLI; non-scratch orgs insert a
    ``User`` sObject via REST + set a password via the REST password resource.
    The password value is never written to the log.
    """

    task_options = {
        "definition_file": {
            "description": "Path to the user definition JSON file (relative to repo root).",
            "required": True,
        },
        "alias": {
            "description": "SF CLI alias to assign to the new user.",
            "required": True,
        },
        "set_unique_username": {
            "description": "Append a unique suffix to the username to avoid conflicts. Defaults to True.",
            "required": False,
            "type": bool,
        },
        "password": {
            "description": (
                "Optional password to set for a user created on a non-scratch "
                "org. If omitted, falls back to the RLM_PERSONA_USER_PASSWORD "
                "environment variable, then to a randomly generated value. The "
                "password is never written to the log (audit-safe)."
            ),
            "required": False,
        },
    }

    # Environment variable consulted for the non-scratch user password when the
    # 'password' option is not supplied. Keeps secrets out of cumulusci.yml.
    PASSWORD_ENV_VAR = "RLM_PERSONA_USER_PASSWORD"

    # Timeout (seconds) for REST calls so a stalled Salesforce endpoint cannot
    # hang a CI/build flow indefinitely.
    REQUEST_TIMEOUT_SECONDS = 30

    def _run_task(self):
        definition_file = self.options.get("definition_file")
        alias = self.options.get("alias")
        set_unique = self.options.get("set_unique_username", True)

        if not definition_file:
            raise TaskOptionsError("definition_file is required.")
        if not alias:
            raise TaskOptionsError("alias is required.")

        repo_root = Path(self.project_config.repo_root)
        definition_file = str(repo_root / definition_file)

        user_def = self._load_user_definition(definition_file)
        existing_user = self._find_existing_user(user_def)
        if existing_user:
            self.logger.info(
                "User already exists (Id=%s, Username=%s). Skipping create.",
                existing_user["Id"],
                existing_user["Username"],
            )
            # On non-scratch orgs the user is created and its password set in two
            # separate REST calls. If a prior run created the user but the
            # password step failed (e.g. the org policy rejected the value), a
            # plain skip would leave the user without a usable password and no
            # way to recover short of deleting it. When an explicit password is
            # supplied (option or env var), retry setting it on the existing
            # user so a corrected rerun can recover. The value is never logged.
            if not getattr(self.org_config, "scratch", False):
                supplied_password = self.options.get("password") or os.environ.get(
                    self.PASSWORD_ENV_VAR
                )
                if supplied_password:
                    self._set_password(existing_user["Id"], supplied_password)
                    self.logger.info(
                        "Reset the configured password for existing user %s "
                        "(value not logged).",
                        existing_user["Username"],
                    )
            return

        # `sf org create user` is scratch-only and raises NonScratchOrgError on
        # any other org type. Branch so non-scratch builds (production, DE,
        # sandbox) create the user via the standard User sObject instead.
        if getattr(self.org_config, "scratch", False):
            self._create_scratch_user(definition_file, alias, set_unique)
        else:
            self._create_production_user(user_def, alias, set_unique)

    def _create_scratch_user(self, definition_file, alias, set_unique):
        """Create a user on a scratch org via `sf org create user`."""
        cmd = [
            "sf", "org", "create", "user",
            "--definition-file", definition_file,
            "--set-alias", alias,
            "--target-org", self.org_config.username,
        ]
        if set_unique:
            cmd.append("--set-unique-username")

        self.logger.info(f"Creating user from {definition_file} with alias '{alias}' ...")
        self.logger.info(f"  Target org: {self.org_config.username}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            self.logger.info(result.stdout.strip())
        if result.stderr:
            (self.logger.warning if result.returncode == 0 else self.logger.error)(
                result.stderr.strip()
            )

        if result.returncode != 0:
            raise TaskOptionsError(
                f"sf org create user failed (exit {result.returncode}).\n{result.stderr}"
            )

        self.logger.info(f"User created successfully with alias '{alias}'.")

    def _create_production_user(self, user_def, alias, set_unique):
        """Create a standard User sObject on a non-scratch org via REST, then
        set a password via the REST User password sub-resource (value not logged).

        Requires a free user license matching the target profile (the
        RLM Sales Representative profile uses the Salesforce user license).
        """
        if requests is None:
            raise CommandException(
                "The 'requests' library is required to create a user on a "
                "non-scratch org but is not available."
            )

        profile_name = user_def.get("profileName")
        if not profile_name:
            raise TaskOptionsError(
                "definition_file must include 'profileName' to create a user "
                "on a non-scratch org (used to resolve ProfileId)."
            )
        profile_id = self._resolve_profile_id(profile_name)

        # Validate the fields accessed directly below so a missing field yields a
        # clear TaskOptionsError instead of an unhelpful KeyError stack trace.
        missing = [f for f in ("LastName", "Email") if not user_def.get(f)]
        if missing:
            raise TaskOptionsError(
                "definition_file is missing required field(s) for non-scratch "
                f"user creation: {', '.join(missing)}."
            )

        # Production usernames must be globally unique across all Salesforce
        # orgs. Mirror the scratch --set-unique-username behavior by appending
        # a unique ".<suffix>" so re-runs still match via _find_existing_user's
        # "Username LIKE 'base.%'" check.
        base_username = user_def.get("Username") or user_def.get("Email")
        if not base_username:
            raise TaskOptionsError(
                "definition_file must include 'Username' or 'Email' to create a user."
            )
        suffix = uuid.uuid4().hex[:8]
        username = f"{base_username}.{suffix}" if set_unique else base_username

        user_alias = (user_def.get("Alias") or alias)[:8]
        nickname = f"{user_alias}{suffix}"[:40]

        record = {
            "Username": username,
            "LastName": user_def["LastName"],
            "Email": user_def["Email"],
            "Alias": user_alias,
            "CommunityNickname": nickname,
            "ProfileId": profile_id,
            "TimeZoneSidKey": user_def.get("TimeZoneSidKey", "America/Los_Angeles"),
            "LocaleSidKey": user_def.get("LocaleSidKey", "en_US"),
            "EmailEncodingKey": user_def.get("EmailEncodingKey", "UTF-8"),
            "LanguageLocaleKey": user_def.get("LanguageLocaleKey", "en_US"),
        }
        if user_def.get("FirstName"):
            record["FirstName"] = user_def["FirstName"]

        self.logger.info(
            "Creating User '%s' (profile '%s', Id %s) on non-scratch org %s ...",
            username, profile_name, profile_id, self.org_config.username,
        )

        url = (
            f"{self.org_config.instance_url}"
            f"/services/data/v{self._api_version()}/sobjects/User"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            url, headers=headers, json=record, timeout=self.REQUEST_TIMEOUT_SECONDS
        )
        if not resp.ok:
            raise CommandException(
                f"Failed to create User (HTTP {resp.status_code}): {resp.text}"
            )
        user_id = (resp.json() or {}).get("id")
        if not user_id:
            raise CommandException(f"User create returned no Id: {resp.text}")

        self.logger.info("User created successfully: Id=%s, Username=%s", user_id, username)

        if user_def.get("generatePassword", True):
            # Resolve the password without ever logging its value (audit-safe):
            #   1. explicit 'password' option, else
            #   2. RLM_PERSONA_USER_PASSWORD env var, else
            #   3. a randomly generated value (not recorded anywhere).
            supplied_password = self.options.get("password") or os.environ.get(
                self.PASSWORD_ENV_VAR
            )
            password = supplied_password or self._generate_password()
            self._set_password(user_id, password)
            if supplied_password:
                self.logger.info(
                    "Set the configured password for %s (value not logged).", username
                )
            else:
                self.logger.info(
                    "Set a randomly generated password for %s (value not logged). "
                    "It is not recorded anywhere — supply the 'password' option or "
                    "the %s environment variable to use a known value, or reset the "
                    "password from Setup to log in as this user.",
                    username, self.PASSWORD_ENV_VAR,
                )

    def _api_version(self):
        """Return the project's package API version (e.g. '67.0'), default 67.0."""
        version = getattr(self.project_config, "project__package__api_version", None)
        return str(version) if version else "67.0"

    def _resolve_profile_id(self, profile_name):
        """Resolve a Profile Id by Name via the sf CLI. Raises if not found."""
        escaped = self._soql_escape(profile_name)
        soql = f"SELECT Id FROM Profile WHERE Name = '{escaped}' LIMIT 1"
        cmd = [
            "sf", "data", "query",
            "--query", soql,
            "--json",
            "--target-org", self.org_config.username,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise CommandException(
                f"Failed to resolve ProfileId for '{profile_name}'.\n{result.stderr}"
            )
        try:
            output = json.loads(result.stdout or "{}")
            records = (((output.get("result") or {}).get("records")) or [])
        except json.JSONDecodeError as exc:
            raise CommandException(
                f"Unable to parse Profile query output as JSON: {exc}"
            ) from exc
        if not records:
            raise TaskOptionsError(
                f"Profile '{profile_name}' not found in org "
                f"{self.org_config.username}. Deploy the profile before creating the user."
            )
        return records[0]["Id"]

    def _set_password(self, user_id, password):
        """Set a user's password via the REST User password sub-resource.

        Using the REST sub-resource (rather than anonymous Apex) keeps the
        password value out of any Apex source and server-side debug/Apex log,
        which matters for audit compliance — the value only ever travels in the
        request body and is never written to a log or temp file.
        """
        if requests is None:
            raise CommandException(
                "The 'requests' library is required to set a user password but "
                "is not available."
            )
        url = (
            f"{self.org_config.instance_url}"
            f"/services/data/v{self._api_version()}/sobjects/User/{user_id}/password"
        )
        headers = {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            url,
            headers=headers,
            json={"NewPassword": password},
            timeout=self.REQUEST_TIMEOUT_SECONDS,
        )
        if not resp.ok:
            # Surface only the status and error code(s) — never the response body
            # verbatim, which can echo the submitted password.
            codes = self._safe_error_codes(resp)
            raise CommandException(
                f"Failed to set user password (HTTP {resp.status_code}{codes}). "
                "Check the org password policy / complexity requirements."
            )

    @staticmethod
    def _safe_error_codes(resp):
        """Extract Salesforce errorCode(s) from a response without exposing the body."""
        try:
            body = resp.json()
        except ValueError:
            return ""
        if isinstance(body, list):
            codes = [e.get("errorCode") for e in body if isinstance(e, dict) and e.get("errorCode")]
            if codes:
                return f"; {', '.join(codes)}"
        return ""

    @staticmethod
    def _generate_password():
        """Generate a strong password meeting Salesforce complexity requirements."""
        special = "!@#$%^&*-_"
        alphabet = string.ascii_letters + string.digits + special
        while True:
            pwd = "".join(secrets.choice(alphabet) for _ in range(14))
            if (
                any(c.islower() for c in pwd)
                and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd)
                and any(c in special for c in pwd)
            ):
                return pwd

    def _load_user_definition(self, definition_file):
        """Load and validate the sf org user definition JSON."""
        try:
            with open(definition_file, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise TaskOptionsError(
                f"definition_file not found: {definition_file}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise TaskOptionsError(
                f"definition_file is not valid JSON: {definition_file}: {exc}"
            ) from exc

        username = data.get("Username")
        email = data.get("Email")
        user_alias = data.get("Alias")
        if not username and not (email and user_alias):
            raise TaskOptionsError(
                "definition_file must include Username, or both Email and Alias "
                "to support idempotent existence checks."
            )
        return data

    def _find_existing_user(self, user_def):
        """
        Return the first matching existing user record, or None.

        For unique usernames, match on:
        - exact Username from the definition OR
        - generated Username prefix from set-unique-username OR
        - (Email + Alias) to catch previously created persona users.
        """
        where_clauses = []

        username = user_def.get("Username")
        if username:
            escaped_username = self._soql_escape(username)
            where_clauses.append(f"Username = '{escaped_username}'")
            where_clauses.append(f"Username LIKE '{escaped_username}.%'")

        email = user_def.get("Email")
        user_alias = user_def.get("Alias")
        if email and user_alias:
            escaped_email = self._soql_escape(email)
            escaped_alias = self._soql_escape(user_alias)
            where_clauses.append(
                f"(Email = '{escaped_email}' AND Alias = '{escaped_alias}')"
            )

        soql = (
            "SELECT Id, Username FROM User "
            f"WHERE {' OR '.join(where_clauses)} "
            "ORDER BY LastModifiedDate DESC LIMIT 1"
        )

        cmd = [
            "sf",
            "data",
            "query",
            "--query",
            soql,
            "--json",
            "--target-org",
            self.org_config.username,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise TaskOptionsError(
                "Failed checking for existing user before create.\n"
                f"exit={result.returncode}\n{result.stderr}"
            )

        try:
            output = json.loads(result.stdout or "{}")
            records = (((output.get("result") or {}).get("records")) or [])
        except json.JSONDecodeError as exc:
            raise TaskOptionsError(
                f"Unable to parse sf data query output as JSON: {exc}"
            ) from exc

        return records[0] if records else None

    @staticmethod
    def _soql_escape(value):
        """Escape single quotes for safe SOQL string literals."""
        return value.replace("\\", "\\\\").replace("'", "\\'")
