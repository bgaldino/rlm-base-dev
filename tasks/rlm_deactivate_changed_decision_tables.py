"""
Let a repo-owned decision table change reach an org where that table is already Active.

Replaces ``exclude_active_decision_tables`` / ``restore_decision_tables``, which moved
every active table's XML into ``.skip/`` before the deploy and back afterwards. That
skipped deploys the platform would have accepted and silently dropped the ones that
mattered, so an edit to ``unpackaged/pre/5_decisiontables`` never reached a prepared
org (todo 096).

Measured on a 264 scratch org (2026-10-02), redeploying over an ACTIVE table:

- unchanged XML                      -> succeeds
- non-structural change (description) -> succeeds and applies
- structural change (a parameter's isRequired) -> fails: "Can't edit an active Decision Table"
- the same structural change after deactivating the table -> succeeds, and because the
  XML carries ``<status>Active</status>`` the deploy itself reactivates the table and
  syncs it (LastSyncDate = deploy time)

So this task check-only deploys the repo files of the tables that are Active in the org.
When the only failures are the active-edit restriction, it deactivates exactly those
tables and deploys their files itself, straight away — the deploy reactivates them. Doing
that here rather than leaving it to ``deploy_pre`` matters: ``deploy_pre`` deploys the
earlier numbered bundles first, so a failure there would strand the tables Inactive. If
deactivation or the deploy fails, the task tries to reactivate every table it
deactivated and fails; any it cannot reactivate is named, with the manual command. The
later bundle deploy then sees unchanged XML on an Active table, which the platform
accepts.

Every other check-only failure is left for the bundle deploy to report — this task never
hides one — and while any remains it changes no lifecycle state.

Only the few tables the repo creates are in scope: the candidates are the
``*.decisionTable-meta.xml`` files in ``path``. System-created tables are never touched.
"""
import re
import shutil
import tempfile
from pathlib import Path
from typing import Iterable, List, Set

try:
    from cumulusci.tasks.salesforce import Deploy
    from cumulusci.salesforce_api.exceptions import MetadataApiError
    from simple_salesforce import Salesforce
except ImportError:
    Deploy = object
    Salesforce = None

    class MetadataApiError(Exception):
        # Same (message, response) signature as CumulusCI's, so str(e) is the message.
        def __init__(self, message, response=None):
            super().__init__(message)
            self.response = response


DECISION_TABLE_SUFFIX = ".decisionTable-meta.xml"
MDAPI_WRAPPER_PREFIX = "Could not process MDAPI response: "

# ⚠ Match loosely. The platform text is "Can't edit an active Decision Table"; the
# apostrophe has not been seen curly, but nothing guarantees it.
ACTIVE_EDIT_PATTERN = re.compile(r"can.?t edit an active decision table", re.IGNORECASE)

# CCI formats each component failure as "<Action> of DecisionTable <fullName>: ...".
FAILURE_NAME_PATTERN = re.compile(r"\bof DecisionTable (\S+?):")


def repo_table_names(path: Path) -> List[str]:
    """Developer names of the decision tables the repo deploys from ``path`` (top level only)."""
    if not path.is_dir():
        return []
    return sorted(
        f.name[: -len(DECISION_TABLE_SUFFIX)]
        for f in path.glob(f"*{DECISION_TABLE_SUFFIX}")
        if f.is_file()
    )


def tables_blocked_by_active_edit(failure_text: str, candidates: Iterable[str]) -> Set[str]:
    """
    The candidate tables a check-only deploy rejected for being Active.

    ⚠ If an active-edit failure cannot be attributed to a table, every candidate is
    returned. Deactivating a table the deploy then reactivates costs a sync; leaving a
    blocked one Active fails the build.
    """
    candidates = set(candidates)
    blocked: Set[str] = set()
    unattributed = False
    for message in failure_text.split("\n\n"):
        if not ACTIVE_EDIT_PATTERN.search(message):
            continue
        match = FAILURE_NAME_PATTERN.search(message)
        name = match.group(1) if match else None
        if name in candidates:
            blocked.add(name)
        else:
            unattributed = True
    return candidates if unattributed else blocked


def other_failures(failure_text: str) -> List[str]:
    """Check-only failures that are NOT the active-edit restriction."""
    return [
        message.strip()
        for message in failure_text.split("\n\n")
        if message.strip() and not ACTIVE_EDIT_PATTERN.search(message)
    ]


class DeactivateChangedDecisionTables(Deploy):
    """Deploy pending changes to active repo decision tables that the platform refuses to edit in place."""

    task_options = {
        **getattr(Deploy, "task_options", {}),
        "path": {
            "description": "Directory holding the repo's *.decisionTable-meta.xml files",
            "required": True,
        },
        "skip_dir": {
            "description": (
                "Legacy directory name the retired exclude task parked files in; any left "
                "there by an aborted run are moved back first. Default: .skip"
            ),
            "required": False,
        },
    }

    def _run_task(self):
        path = Path(self.options["path"])
        self._restore_leftover_skipped_files(path, path / (self.options.get("skip_dir") or ".skip"))

        names = repo_table_names(path)
        if not names:
            self.logger.info(f"No decision table files in {path}; nothing to check.")
            return

        active = self._active_tables(names)
        if not active:
            self.logger.info("None of the repo's decision tables is Active in the org; the deploy can create or update them as-is.")
            return

        failure_text = self._check_only_deploy(path, sorted(active))
        if failure_text is None:
            self.logger.info(
                f"Check-only deploy accepted {len(active)} active table(s) as-is; no deactivation needed."
            )
            return

        others = other_failures(failure_text)
        if others:
            # ⚠ Change no lifecycle state. The deploy that follows will fail on these,
            # and a failed deploy rolls back — so it would not reactivate anything this
            # task deactivated, leaving those tables Inactive. Fix these first; the rerun
            # deactivates whatever the active-edit restriction still blocks.
            for message in others:
                self.logger.warning(f"Check-only deploy reported a failure the deploy will also hit: {message}")
            self.logger.warning(
                "Deactivating nothing while other check-only failures remain: the deploy would fail "
                "and leave deactivated tables Inactive."
            )
            return

        blocked = tables_blocked_by_active_edit(failure_text, active)
        if not blocked:
            return
        self._deactivate_and_deploy(path, active, blocked)

    def _restore_leftover_skipped_files(self, decision_tables_path: Path, skip_dir: Path):
        """
        Move files a previous aborted run left in ``.skip/`` back before anything else.

        Kept from the retired exclude task: a checkout an older build aborted mid-way
        still has tables parked there, and deploying without them would drop them.
        """
        if not skip_dir.is_dir():
            return
        for file in skip_dir.glob(f"*{DECISION_TABLE_SUFFIX}"):
            target = decision_tables_path / file.name
            if not target.exists():
                file.replace(target)
                self.logger.info(f"Pre-flight restore: moved {file.name} back from {skip_dir.name}/")

    def _active_tables(self, names: List[str]) -> dict:
        """DeveloperName -> Id for the given tables that are Active in the org."""
        escaped = "', '".join(name.replace("'", "\\'") for name in names)
        soql = (
            "SELECT Id, DeveloperName FROM DecisionTable "
            f"WHERE DeveloperName IN ('{escaped}') AND Status = 'Active'"
        )
        try:
            records = self._sf.query(soql).get("records", [])
        except Exception as e:
            if "invalid_type" in str(e).lower() or "invalid type" in str(e).lower():
                # Fresh build: the DecisionTable entity is not queryable until the
                # first table exists, so nothing can be Active.
                self.logger.info(f"DecisionTable not queryable yet ({e}); treating the org as having no active tables.")
            else:
                # ⚠ Do not guess. The retired task excluded every table here, which
                # silently dropped the change. Proceeding lets the deploy succeed when
                # it can and fail loudly when it cannot.
                self.logger.warning(
                    f"Could not query decision table status ({e}); deactivating nothing. "
                    "If a structural change is pending, the deploy will fail with "
                    "\"Can't edit an active Decision Table\" — deactivate with "
                    "manage_decision_tables -o operation deactivate and rerun."
                )
            return {}
        return {rec["DeveloperName"]: rec["Id"] for rec in records if rec.get("DeveloperName")}

    def _check_only_deploy(self, path: Path, names: List[str]):
        """Validate the active tables' repo files against the org. Returns failure text, or None on success."""
        self.logger.info(f"Check-only deploy of {len(names)} active decision table(s): {', '.join(names)}")
        return self._deploy_tables(path, names, check_only=True)

    def _deploy_tables(self, path: Path, names: List[str], check_only: bool):
        """Deploy just ``names``' files from ``path``. Returns failure text, or None on success."""
        with tempfile.TemporaryDirectory(prefix="rlm_dt_deploy_") as tmp:
            staged = Path(tmp) / "decisionTables"
            staged.mkdir()
            for name in names:
                shutil.copy2(path / f"{name}{DECISION_TABLE_SUFFIX}", staged)
            # ⚠ Point options["path"] at the staging dir rather than passing
            # _get_api(path=...): not every CumulusCI release accepts the argument,
            # and every one reads options["path"].
            original_path = self.options["path"]
            self.options["path"] = str(staged)
            self.check_only = check_only
            try:
                api = self._get_api()
                if api is None:
                    return None
                api()
            except MetadataApiError as e:
                # ⚠ Not MetadataComponentFailure. ApiDeploy.__call__ re-raises whatever
                # _process_response raised as MetadataParseError("Could not process MDAPI
                # response: <text>"), so the component failure arrives as its base class —
                # measured on 264. The per-component text survives inside the message.
                return str(e).replace(MDAPI_WRAPPER_PREFIX, "", 1)
            finally:
                self.options["path"] = original_path
                self.check_only = False
        return None

    def _deactivate_and_deploy(self, path: Path, active: dict, blocked: Set[str]):
        """
        Deactivate the blocked tables and deploy them now; on any failure try to reactivate them and raise.

        The deploy reactivates them itself (the XML carries Active). Nothing is left
        Inactive for a later step to fix.
        """
        sf = self._sf
        deactivated: List[str] = []
        try:
            for name in sorted(blocked):
                sf.DecisionTable.update(active[name], {"Status": "Inactive"})
                deactivated.append(name)
                self.logger.info(f"Deactivated {name}: its pending change cannot be applied to an Active table.")
            failure_text = self._deploy_tables(path, deactivated, check_only=False)
        except Exception:
            self._reactivate(active, deactivated)
            raise
        if failure_text is not None:
            still_inactive = self._reactivate(active, deactivated)
            if still_inactive:
                outcome = (
                    f"{', '.join(still_inactive)} could NOT be reactivated and remain Inactive — "
                    "see the errors above"
                )
            else:
                outcome = "they were reactivated unchanged"
            raise MetadataApiError(
                f"Deploying the deactivated decision table(s) {', '.join(deactivated)} failed; "
                f"{outcome}. {failure_text}",
                None,
            )
        self.logger.info(f"Deployed and reactivated {len(deactivated)} decision table(s): {', '.join(deactivated)}")

    def _reactivate(self, active: dict, names: List[str]) -> List[str]:
        """Best effort: one table failing to reactivate must not stop the rest. Returns those left Inactive."""
        sf = self._sf
        still_inactive: List[str] = []
        for name in names:
            try:
                sf.DecisionTable.update(active[name], {"Status": "Active"})
                self.logger.info(f"Reactivated {name}.")
            except Exception as e:
                self.logger.error(
                    f"Could not reactivate {name} ({e}); it is Inactive. Reactivate it with "
                    f"manage_decision_tables -o operation activate."
                )
                still_inactive.append(name)
        return still_inactive

    @property
    def _sf(self):
        """
        A Salesforce client on the PROJECT's API version, built once per run.

        Same rationale as ManageDecisionTables._pinned_salesforce_client:
        ``org_config.salesforce_client`` follows the org's newest API version, which
        drifts the moment an org is upgraded ahead of the project.
        """
        if getattr(self, "_sf_client", None) is None:
            api_version = self.project_config.project__package__api_version
            if not api_version or Salesforce is None:
                self.logger.warning(
                    "No project api_version pin available; decision-table calls use the org's latest API version."
                )
                self._sf_client = self.org_config.salesforce_client
            else:
                self._sf_client = Salesforce(
                    instance=self.org_config.instance_url.replace("https://", ""),
                    session_id=self.org_config.access_token,
                    version=api_version,
                )
        return self._sf_client
