"""
Recalculate Permission Set Groups and wait until they are Updated.

Why PSGs show "Outdated": After deploy_pre or assign_permission_set_licenses, Salesforce
marks PSGs as Outdated when their effective permissions need to be recalculated. The normal
transition is Outdated → Updating (platform recalculating) → Updated. We trigger recalc by
updating the PSG (e.g. Description); using the Tooling API for the update is required in
many orgs for the platform to actually start recalc and move status to Updating.

⚠ "Updated" can be STALE (todo 292). A PSG's aggregate is computed when its components
change, not when a component's own permissions grow. RLM_RCB is deployed in `pre`; the
managed Billing Admin set it contains only gains the Dispute/DisputeItem billing fields
once `post_billing` turns on dispute management, so RLM_RCB stays "Updated" without them
and the admin can't read DisputeItem.ApprovedAmount. A Description edit does NOT recalculate
an Updated group (measured on 264, 2026-10-28); a component change does. `force_recalc`
adds and removes an empty probe permission set as a component to force it, without
withdrawing any permission.
"""
import time
from typing import List
import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    TaskOptionsError = Exception


class RecalculatePermissionSetGroups(BaseSalesforceTask):
    """Ensure PSGs are in Updated status before assignment."""

    task_options = {
        "api_names": {
            "description": "List or comma-separated PSG DeveloperName values.",
            "required": True,
        },
        "timeout_seconds": {
            "description": "Max time to wait for all PSGs to become Updated (per attempt).",
            "required": False,
        },
        "poll_seconds": {
            "description": "Polling interval in seconds.",
            "required": False,
        },
        "trigger_recalc": {
            "description": "Update Description on Outdated PSGs to trigger recalculation.",
            "required": False,
        },
        "initial_delay_seconds": {
            "description": "Seconds to wait before starting to poll (gives platform time after PSL assign/deploy).",
            "required": False,
        },
        "retry_count": {
            "description": "Number of retries after a timeout (sleep then poll again).",
            "required": False,
        },
        "retry_delay_seconds": {
            "description": "Seconds to wait before retrying after a timeout.",
            "required": False,
        },
        "post_trigger_delay_seconds": {
            "description": "After triggering recalc on Outdated groups, wait this long before next poll (gives platform time to transition to Updating).",
            "required": False,
        },
        "use_tooling_api": {
            "description": "Use Tooling API for PSG updates (can be required in some orgs to trigger recalculation).",
            "required": False,
        },
        "force_recalc": {
            "description": "Recompute even a group that reads Updated: add an empty probe permission set (RLM_PSG_Recalc_Probe, created if absent) as a component, wait, then remove it. No permission is withdrawn. Use after a step that grows a member permission set's permissions (e.g. a setting that adds fields), where Updated is stale. Ignores the initial-delay, retry and Tooling options.",
            "required": False,
        },
        "verify_fields": {
            "description": "With force_recalc: Object.Field names the group must grant afterwards. A group already granting them is skipped (a refresh rebuild is a no-op); a group still lacking them after the recompute FAILS rather than passing on a no-op.",
            "required": False,
        },
    }

    def _run_task(self):
        names = self._parse_names(self.options.get("api_names"))
        timeout_seconds = int(self.options.get("timeout_seconds", 300))
        poll_seconds = int(self.options.get("poll_seconds", 10))
        trigger_recalc = str(self.options.get("trigger_recalc", "true")).lower() == "true"
        initial_delay_seconds = int(self.options.get("initial_delay_seconds", 0))
        retry_count = int(self.options.get("retry_count", 2))
        retry_delay_seconds = int(self.options.get("retry_delay_seconds", 120))
        post_trigger_delay_seconds = int(self.options.get("post_trigger_delay_seconds", 90))
        use_tooling_api = str(self.options.get("use_tooling_api", "false")).lower() == "true"
        self._use_tooling_api = use_tooling_api

        if str(self.options.get("force_recalc", "false")).lower() == "true":
            self._run_force(names, timeout_seconds, poll_seconds)
            return

        # Check once up front: if all PSGs are already Updated, skip delay and wait loop
        rows = self._query_groups(names)
        status_by_name = {row["DeveloperName"]: row["Status"] for row in rows}
        missing = [name for name in names if name not in status_by_name]
        if missing:
            raise TaskOptionsError(
                f"PermissionSetGroup records not found: {', '.join(missing)}"
            )
        outdated = [n for n, s in status_by_name.items() if s == "Outdated"]
        updating = [n for n, s in status_by_name.items() if s == "Updating"]
        failed = [n for n, s in status_by_name.items() if s == "Failed"]
        if failed:
            raise TaskOptionsError(
                f"PermissionSetGroup recalculation failed: {', '.join(failed)}"
            )
        if not outdated and not updating:
            self.logger.info(
                "All target Permission Set Groups are already Updated; skipping recalc and wait."
            )
            return

        if initial_delay_seconds > 0:
            self.logger.info(
                f"Waiting {initial_delay_seconds}s for permission set groups to perform operations before polling."
            )
            time.sleep(initial_delay_seconds)

        last_error = None
        for attempt in range(retry_count + 1):
            try:
                self._wait_until_updated(
                    names=names,
                    timeout_seconds=timeout_seconds,
                    poll_seconds=poll_seconds,
                    trigger_recalc=trigger_recalc,
                    post_trigger_delay_seconds=post_trigger_delay_seconds,
                    use_tooling_api=use_tooling_api,
                )
                return
            except TaskOptionsError as e:
                last_error = e
                if attempt < retry_count:
                    self.logger.warning(
                        f"Permission set groups not yet Updated (attempt {attempt + 1}/{retry_count + 1}). "
                        f"Waiting {retry_delay_seconds}s before retry."
                    )
                    time.sleep(retry_delay_seconds)
                else:
                    raise
        if last_error is not None:
            raise last_error

    def _wait_until_updated(
        self,
        names,
        timeout_seconds,
        poll_seconds,
        trigger_recalc,
        post_trigger_delay_seconds=0,
        use_tooling_api=False,
    ):
        deadline = time.time() + timeout_seconds
        recalc_attempted = set()
        self._use_tooling_api = use_tooling_api

        while True:
            rows = self._query_groups(names)
            status_by_name = {row["DeveloperName"]: row["Status"] for row in rows}

            missing = [name for name in names if name not in status_by_name]
            if missing:
                raise TaskOptionsError(
                    f"PermissionSetGroup records not found: {', '.join(missing)}"
                )

            outdated = [name for name, status in status_by_name.items() if status == "Outdated"]
            failed = [name for name, status in status_by_name.items() if status == "Failed"]
            updating = [name for name, status in status_by_name.items() if status == "Updating"]

            if failed:
                raise TaskOptionsError(
                    f"PermissionSetGroup recalculation failed: {', '.join(failed)}"
                )

            if not outdated and not updating:
                self.logger.info("All target Permission Set Groups are Updated.")
                return

            triggered_this_round = False
            if trigger_recalc:
                api_note = " (via Tooling API)" if getattr(self, "_use_tooling_api", False) else ""
                for name in outdated:
                    if name in recalc_attempted:
                        continue
                    self._touch_group_description(name)
                    recalc_attempted.add(name)
                    triggered_this_round = True
                    self.logger.info(
                        f"Triggered recalculation for Permission Set Group '{name}'{api_note}; "
                        "status should transition Outdated → Updating → Updated."
                    )

            if triggered_this_round and post_trigger_delay_seconds > 0:
                self.logger.info(
                    f"Waiting {post_trigger_delay_seconds}s for platform to start recalc before next poll."
                )
                time.sleep(post_trigger_delay_seconds)

            if time.time() >= deadline:
                statuses = ", ".join(
                    f"{n}:{status_by_name.get(n, 'Missing')}" for n in names
                )
                raise TaskOptionsError(
                    f"Timed out waiting for Permission Set Groups to become Updated. Statuses: {statuses}"
                )

            self.logger.info(
                "Waiting for Permission Set Groups to reach Updated. "
                f"Outdated: {len(outdated)}, Updating: {len(updating)}"
            )
            time.sleep(poll_seconds)

    PROBE_PERMISSION_SET = "RLM_PSG_Recalc_Probe"

    def _run_force(self, names, timeout_seconds, poll_seconds):
        """force_recalc: recompute each group even if it reads Updated, then prove it worked."""
        found = {r["DeveloperName"] for r in self._query_groups(names)}
        missing = [n for n in names if n not in found]
        if missing:
            raise TaskOptionsError(f"PermissionSetGroup records not found: {', '.join(missing)}")
        verify = self._parse_optional_names(self.options.get("verify_fields"))
        targets = names
        if verify:
            # Already complete (e.g. a refresh rebuild): nothing to force.
            want = {f.lower() for f in verify}
            targets = [n for n in names if not want <= self._aggregate_fields(n, verify)]
            for n in sorted(set(names) - set(targets)):
                self.logger.info(f"'{n}' already grants {', '.join(verify)}; not forcing it.")
        for name in targets:
            self._force_recalc(name, timeout_seconds, poll_seconds)
        if targets:
            self._wait_after_force(targets, timeout_seconds, poll_seconds)
        if verify:
            short = {n: sorted(f for f in verify if f.lower() not in self._aggregate_fields(n, verify))
                     for n in targets}
            short = {n: f for n, f in short.items() if f}
            if short:
                # Not a pass: the recompute ran but the grants this exists for are still absent.
                raise TaskOptionsError("Recalculated, but the group still lacks: "
                                       + "; ".join(f"{n}: {', '.join(f)}" for n, f in short.items()))

    def _parse_optional_names(self, value) -> List[str]:
        if not value:
            return []
        return self._parse_names(value)

    def _force_recalc(self, name: str, timeout_seconds: int, poll_seconds: int):
        """Make the platform recompute `name`'s aggregate WITHOUT withdrawing any permission:
        add an empty probe permission set as a component (the component change triggers the
        recompute), wait for it to settle, then remove the probe. If the removal fails, the
        group carries a harmless empty component rather than missing a real one."""
        group = self._query(
            f"SELECT Id FROM PermissionSetGroup WHERE DeveloperName = '{self._escape_soql(name)}' LIMIT 1"
        )[0]["Id"]
        base = f"{self.org_config.instance_url}/services/data/v{self._api_version()}/sobjects"
        probe = self._probe_permission_set_id(base)
        # Component edits are refused while the group is Updating ("... permission set group is
        # updating", FIELD_INTEGRITY_EXCEPTION, measured on 264), so each edit waits for it.
        def edit(method, url, payload=None):
            deadline = time.time() + timeout_seconds  # per edit: the removal must not inherit the add's wait
            while True:
                if self._query_groups([name])[0]["Status"] != "Updating":
                    response = requests.request(method, url, headers=self._headers(), json=payload, timeout=60)
                    if response.status_code in (200, 201, 204):
                        return response
                    refused = ("FIELD_INTEGRITY_EXCEPTION" in response.text
                               and "is updating" in response.text.lower())
                    if not refused:
                        return response
                if time.time() >= deadline:
                    raise TaskOptionsError(f"force_recalc: '{name}' stayed Updating past {timeout_seconds}s.")
                time.sleep(poll_seconds)

        existing = self._query(
            "SELECT Id FROM PermissionSetGroupComponent "
            f"WHERE PermissionSetGroupId = '{group}' AND PermissionSetId = '{probe}' LIMIT 1")
        if existing:
            # Left behind by an earlier interrupted run: remove it, which is itself a component change.
            response = edit("DELETE", f"{base}/PermissionSetGroupComponent/{existing[0]['Id']}")
            action = "removed a leftover probe"
        else:
            response = edit("POST", f"{base}/PermissionSetGroupComponent",
                            {"PermissionSetGroupId": group, "PermissionSetId": probe})
            action = "added the probe"
            if response.status_code in (200, 201):
                component_id = response.json()["id"]
                try:
                    removal = edit("DELETE", f"{base}/PermissionSetGroupComponent/{component_id}")
                    problem = None if removal.status_code in (200, 204) else f"{removal.status_code} {removal.text}"
                except (TaskOptionsError, requests.RequestException) as exc:
                    problem = str(exc)
                if problem:
                    # The recompute already happened; the probe grants nothing.
                    self.logger.warning(
                        f"force_recalc: '{name}' was recalculated, but removing the empty probe "
                        f"{self.PROBE_PERMISSION_SET} failed ({problem}); it grants nothing, and the "
                        "next run removes it.")
        if response.status_code not in (200, 201, 204):
            raise TaskOptionsError(f"force_recalc: could not change a component of '{name}' "
                                   f"({response.status_code} {response.text}).")
        self.logger.info(f"Forced recalculation of '{name}' ({action}).")

    def _probe_permission_set_id(self, base: str) -> str:
        rows = self._query(
            f"SELECT Id FROM PermissionSet WHERE Name = '{self.PROBE_PERMISSION_SET}' LIMIT 1")
        if rows:
            return rows[0]["Id"]
        response = requests.post(f"{base}/PermissionSet", headers=self._headers(), timeout=60, json={
            "Name": self.PROBE_PERMISSION_SET, "Label": "RLM PSG Recalc Probe",
            "Description": "Empty on purpose. Added to and removed from a permission set group to "
                           "force its recalculation (recalculate_permission_set_groups force_recalc)."})
        if response.status_code not in (200, 201):
            raise TaskOptionsError(f"force_recalc: could not create {self.PROBE_PERMISSION_SET}: "
                                   f"{response.status_code} {response.text}")
        return response.json()["id"]

    def _aggregate_fields(self, name: str, fields: List[str]) -> set:
        """Which of `fields` the group's aggregate grants read on. Filtered to those fields so the
        result can't spill onto a second page, and to Type = 'Group' so a muting set can't count."""
        wanted = ", ".join(f"'{self._escape_soql(f)}'" for f in fields)
        rows = self._query(
            f"SELECT Field FROM FieldPermissions WHERE PermissionsRead = true AND Field IN ({wanted}) "
            "AND ParentId IN (SELECT Id FROM PermissionSet WHERE Type = 'Group' AND "
            f"PermissionSetGroup.DeveloperName = '{self._escape_soql(name)}')")
        # Lower-cased: SOQL IN matches case-insensitively, so the comparison must too.
        return {r["Field"].lower() for r in rows}

    def _wait_after_force(self, names, timeout_seconds, poll_seconds):
        """Wait until every forced group is Updated again."""
        deadline = time.time() + timeout_seconds
        time.sleep(poll_seconds)
        while True:
            status = {r["DeveloperName"]: r["Status"] for r in self._query_groups(names)}
            failed = [n for n, s in status.items() if s == "Failed"]
            if failed:
                raise TaskOptionsError(f"PermissionSetGroup recalculation failed: {', '.join(failed)}")
            if all(status.get(n) == "Updated" for n in names):
                self.logger.info("Forced Permission Set Groups are Updated.")
                return
            if time.time() >= deadline:
                raise TaskOptionsError("Timed out waiting for forced Permission Set Groups: "
                                       + ", ".join(f"{n}:{status.get(n, 'Missing')}" for n in names))
            time.sleep(poll_seconds)

    def _parse_names(self, value) -> List[str]:
        if isinstance(value, list):
            names = [str(v).strip() for v in value if str(v).strip()]
        elif isinstance(value, str):
            names = [v.strip() for v in value.split(",") if v.strip()]
        else:
            raise TaskOptionsError("api_names must be a list or comma-separated string")

        if not names:
            raise TaskOptionsError("api_names cannot be empty")
        return names

    def _query_groups(self, names: List[str]):
        quoted = ", ".join(f"'{self._escape_soql(name)}'" for name in names)
        soql = (
            "SELECT Id, DeveloperName, Status, Description "
            f"FROM PermissionSetGroup WHERE DeveloperName IN ({quoted})"
        )
        return self._query(soql)

    def _touch_group_description(self, name: str):
        rows = self._query(
            "SELECT Id, Description FROM PermissionSetGroup "
            f"WHERE DeveloperName = '{self._escape_soql(name)}' LIMIT 1"
        )
        if not rows:
            raise TaskOptionsError(f"PermissionSetGroup not found: {name}")

        row = rows[0]
        description = (row.get("Description") or "").strip()
        marker = "[cci-recalc]"
        if marker in description:
            new_description = description.replace(marker, "").strip()
        else:
            new_description = f"{description} {marker}".strip()

        self._update_permission_set_group(row["Id"], {"Description": new_description})

    def _escape_soql(self, value: str) -> str:
        return value.replace("'", "\\'")

    def _api_version(self) -> str:
        return (
            getattr(self.org_config, "api_version", None)
            or getattr(self.project_config, "project__package__api_version", "68.0")
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    def _query(self, soql: str):
        url = f"{self.org_config.instance_url}/services/data/v{self._api_version()}/query"
        response = requests.get(url, headers=self._headers(), params={"q": soql}, timeout=60)
        if not response.ok:
            raise TaskOptionsError(f"SOQL query failed: {response.status_code} {response.text}")
        return response.json().get("records", [])

    def _update_permission_set_group(self, record_id: str, payload: dict):
        base = "tooling" if getattr(self, "_use_tooling_api", False) else "sobjects"
        url = (
            f"{self.org_config.instance_url}/services/data/"
            f"v{self._api_version()}/{base}/PermissionSetGroup/{record_id}"
        )
        response = requests.patch(url, headers=self._headers(), json=payload, timeout=60)
        if response.status_code not in (200, 204):
            raise TaskOptionsError(
                f"PermissionSetGroup update failed: {response.status_code} {response.text}"
            )
