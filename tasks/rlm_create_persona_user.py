"""
CumulusCI task to create a scratch org user from a definition file.

Wraps `sf org create user --definition-file <path> --set-alias <alias>
--set-unique-username --target-org <username>`.
"""
import json
import subprocess

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception


class CreatePersonaUser(BaseTask):
    """Create a scratch org user from a JSON definition file via the sf CLI."""

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
    }

    def _run_task(self):
        definition_file = self.options.get("definition_file")
        alias = self.options.get("alias")
        set_unique = self.options.get("set_unique_username", True)

        if not definition_file:
            raise TaskOptionsError("definition_file is required.")
        if not alias:
            raise TaskOptionsError("alias is required.")

        user_def = self._load_user_definition(definition_file)
        existing_user = self._find_existing_user(user_def)
        if existing_user:
            self.logger.info(
                "User already exists (Id=%s, Username=%s). Skipping create.",
                existing_user["Id"],
                existing_user["Username"],
            )
            return

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
