#!/usr/bin/env python3
"""Decision Table lifecycle operations over an injectable transport.

SObject-backed tables use Tooling status updates. CSV-backed tables use Connect
file-import versions. Activation and CSV import are asynchronous; metadata
deploys run from a temporary SFDX project. Dry-run transports preserve reads and
skip writes and state polling.
"""

import copy
import json
import os
import shutil
import subprocess
import tempfile
import time
from typing import Any, Callable, Dict, List, Optional

from ._client import (
    DEFINITIONS_PATH,
    soql_literal,
)

# A metadata deploy / activation can take minutes server-side; mirror the client.
_DEPLOY_TIMEOUT = 600  # seconds

# The refreshDecisionTable standard action (relative to /services/data/vXX.0/).
REFRESH_ACTION_PATH = "actions/standard/refreshDecisionTable"

# The transient Status reported while an activation is in flight.
_ACTIVATION_IN_PROGRESS = "ActivationInProgress"
_STATUS_ACTIVE = "Active"
_STATUS_INACTIVE = "Inactive"

class LifecycleError(RuntimeError):
    """Raised on any lifecycle failure in the Decision Table toolkit."""


class LifecycleEngine:
    """Decision Table lifecycle engine over a :class:`_client.Transport`.

    ``transport`` is the only dependency: all Tooling/Connect/SOQL calls route
    through it, so its ``dry_run``/``logger`` govern the whole engine and a test
    can inject a fake.
    """

    def __init__(
        self,
        transport,
        *,
        logger: Callable[..., None] = None,
        max_wait_seconds: int = 90,
        poll_interval_seconds: int = 3,
    ):
        self.t = transport
        self.log = logger or transport.logger
        self.dry_run = transport.dry_run
        self.max_wait = max(0, max_wait_seconds)
        self.poll = max(1, poll_interval_seconds)

    # -- Status reads --------------------------------------------------

    def get_status(self, record_id: str) -> Optional[str]:
        """Current ``DecisionTable.Status`` (Tooling), or ``None`` if not found."""
        rows = self.t.tooling_query(
            "SELECT Id, Status FROM DecisionTable "
            f"WHERE Id = '{soql_literal(record_id)}'"
        )
        if not rows:
            return None
        return rows[0].get("Status")

    def _is_csv_upload(self, record_id: str) -> bool:
        """Whether ``record_id``'s ``dataSourceType`` is ``CsvUpload`` (Tooling GET)."""
        return self._current_metadata(record_id).get("dataSourceType") == "CsvUpload"

    def _current_metadata(self, record_id: str) -> Dict[str, Any]:
        """Tooling GET of the record's ``Metadata`` complexvalue (reads always run).

        A status change must PATCH the **whole** ``Metadata`` (a complexvalue is
        replaced wholesale — sending only ``status`` would wipe the columns), so
        every transition GET-modifies-PATCHes the full Metadata.
        """
        record = self.t.tooling_sobject("GET", "DecisionTable", record_id)
        if not isinstance(record, dict) or not isinstance(record.get("Metadata"), dict):
            raise LifecycleError(
                f"Tooling GET of DecisionTable/{record_id} returned no Metadata "
                f"complexvalue; cannot transition its status."
            )
        return record["Metadata"]

    # -- Status transitions --------------------------------------------

    def _set_status(self, record_id: str, status: str) -> None:
        """PATCH ``Metadata.status`` to ``status`` (full-Metadata replace).

        Skipped+logged under dry-run (the GET still runs so the sequence is real).
        """
        metadata = copy.deepcopy(self._current_metadata(record_id))
        metadata["status"] = status
        self.t.tooling_sobject(
            "PATCH", "DecisionTable", record_id, body={"Metadata": metadata}
        )
        verb = "Would set" if self.dry_run else "Set"
        self.log(f"{verb} DecisionTable {record_id} Metadata.status = {status}.")

    def wait_for_status(self, record_id: str, target: str) -> None:
        """Poll until ``Status == target`` (no-op under dry-run).

        For activation this waits past the transient ``ActivationInProgress``;
        for deactivation the terminal ``Inactive`` is usually immediate. Raises on
        timeout with the last-seen status.
        """
        if self.dry_run:
            return
        waited = 0
        last: Optional[str] = None
        while waited <= self.max_wait:
            last = self.get_status(record_id)
            if last == target:
                self.log(
                    f"Confirmed DecisionTable {record_id} Status={target} "
                    f"after {waited}s."
                )
                return
            time.sleep(self.poll)
            waited += self.poll
        raise LifecycleError(
            f"DecisionTable {record_id} did not reach Status={target} within "
            f"{self.max_wait}s (last seen: {last!r})."
        )

    def _file_import_versions(self, record_id: str) -> List[Dict[str, Any]]:
        """Return validated file-import version entries from Tooling Metadata."""
        versions = self._current_metadata(record_id).get(
            "decisionTableFileImportVersions"
        ) or []
        if not isinstance(versions, list):
            raise LifecycleError(
                f"DecisionTable {record_id} returned a malformed "
                "decisionTableFileImportVersions value."
            )
        return [v for v in versions if isinstance(v, dict)]

    def _resolve_lifecycle_version(self, record_id: str, target_status: str) -> int:
        """Resolve the safe CsvUpload version for an activate/deactivate transition.

        A sole version is unambiguous. For deactivation, an already-active version
        is also unambiguous. Other multi-version shapes are rejected.
        """
        versions = self._file_import_versions(record_id)
        numbered = [v for v in versions if isinstance(v.get("versionNumber"), int)]
        if len(numbered) == 1:
            return int(numbered[0]["versionNumber"])
        if target_status == _STATUS_INACTIVE:
            active = [
                v for v in numbered
                if v.get("versionStatus") in (_STATUS_ACTIVE, _ACTIVATION_IN_PROGRESS)
            ]
            if len(active) == 1:
                return int(active[0]["versionNumber"])
        detail = [
            {"versionNumber": v.get("versionNumber"), "versionStatus": v.get("versionStatus")}
            for v in versions
        ]
        raise LifecycleError(
            f"DecisionTable {record_id} does not have one unambiguous file-import "
            f"version for {target_status}: {detail!r}. The table-level lifecycle "
            "commands intentionally refuse ambiguous multi-version tables."
        )

    def _set_version_status(self, record_id: str, status: str,
                             version_number: int) -> None:
        """PATCH a CsvUpload table's file-import version's ``versionStatus`` (Connect).

        The table's own ``Status`` is a platform-derived mirror of this — see the
        module docstring. The caller must resolve an unambiguous version first.
        """
        vpath = f"{DEFINITIONS_PATH}/{record_id}/versions/{int(version_number)}"
        self.t.connect("PATCH", vpath, {"versionStatus": status})
        verb = "Would set" if self.dry_run else "Set"
        self.log(f"{verb} DecisionTable {record_id} version {version_number} "
                 f"versionStatus = {status}.")

    def activate(self, record_id: str) -> None:
        """Set Status → Active and poll past ``ActivationInProgress`` (async).

        CsvUpload tables are version-first (see module docstring): PATCHes a
        file-import version instead of the table's ``Metadata.status`` — the
        table's Status cascades from it. The sole/active version is resolved from
        the platform; ambiguous multi-version tables are refused.
        """
        if self._is_csv_upload(record_id):
            version_number = self._resolve_lifecycle_version(record_id, _STATUS_ACTIVE)
            self._set_version_status(record_id, _STATUS_ACTIVE, version_number)
        else:
            self._set_status(record_id, _STATUS_ACTIVE)
        self.wait_for_status(record_id, _STATUS_ACTIVE)

    def deactivate(self, record_id: str) -> None:
        """Set Status → Inactive (synchronous) and confirm.

        CsvUpload tables are version-first — see :meth:`activate`. The sole/active
        version is resolved from the platform. A confirmation failure is returned
        to the caller; this command never performs a second lifecycle transition.
        """
        if self._is_csv_upload(record_id):
            version_number = self._resolve_lifecycle_version(record_id, _STATUS_INACTIVE)
            self._set_version_status(record_id, _STATUS_INACTIVE, version_number)
        else:
            self._set_status(record_id, _STATUS_INACTIVE)
        self.wait_for_status(record_id, _STATUS_INACTIVE)

    # -- Refresh -------------------------------------------------------

    def refresh(self, developer_name: str, *, incremental: bool = False,
                version_number: Optional[int] = None) -> Dict[str, Any]:
        """Invoke the asynchronous ``refreshDecisionTable`` standard action.

        Uses the platform ``isDecisionTableIncremental`` flag. Returns the
        normalized action result
        (``{"isSuccess", "status", "raw"}``); ``status`` is typically ``Queued``.
        The refresh is asynchronous. ``DecisionTable.LastSyncDate`` is the full
        refresh completion signal; incremental refresh advances
        ``LastIncrementalSyncDate`` only.
        """
        inputs: Dict[str, Any] = {
            "DecisionTableApiName": developer_name,
            "isDecisionTableIncremental": bool(incremental),
        }
        if version_number is not None:
            inputs["VersionNumber"] = int(version_number)
        resp = self.t.connect("POST", REFRESH_ACTION_PATH, {"inputs": [inputs]})
        if self.dry_run:
            return {"isSuccess": None, "status": "dry-run", "raw": resp}
        result = resp[0] if isinstance(resp, list) and resp else resp
        status = None
        if isinstance(result, dict):
            output = result.get("outputValues")
            if isinstance(output, dict):
                status = output.get("Status")
        return {
            "isSuccess": result.get("isSuccess") if isinstance(result, dict) else None,
            "status": status,
            "raw": resp,
        }

    # -- Metadata deploy (--path metadata) -----------------------------

    def deploy_metadata_xml(self, api_name: str, xml: str) -> Dict[str, Any]:
        """Deploy a ``.decisionTable-meta.xml`` via a temp SFDX project outside the repo.

        The temp project is created with ``tempfile.mkdtemp()`` (an OS temp dir, NOT
        under the repo), the XML is written under ``force-app/main/default/
        decisionTables/``, and ``sf project deploy start --source-dir force-app
        --ignore-conflicts`` runs **with cwd = the temp project root** (an absolute
        ``--source-dir`` from the repo trips ``UnsafeFilepathError``). The temp tree
        is always removed afterward, so no generated metadata lands in ``git
        status``. Under dry-run the deploy is logged and skipped.
        """
        if self.dry_run:
            self.log(
                f"[dry-run] would deploy DecisionTable '{api_name}' via a temp "
                f"SFDX project (sf project deploy start --ignore-conflicts) to org "
                f"'{self.t.target_org}'."
            )
            return {"deployed": False, "dryRun": True, "apiName": api_name}

        tmp = tempfile.mkdtemp(prefix="dt_deploy_")
        try:
            pkg_dir = os.path.join(tmp, "force-app", "main", "default", "decisionTables")
            os.makedirs(pkg_dir)
            with open(os.path.join(tmp, "sfdx-project.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "packageDirectories": [{"path": "force-app", "default": True}],
                        "namespace": "",
                        "sfdcLoginUrl": "https://login.salesforce.com",
                        "sourceApiVersion": self.t.api_version,
                    },
                    fh,
                )
            xml_path = os.path.join(pkg_dir, f"{api_name}.decisionTable-meta.xml")
            with open(xml_path, "w", encoding="utf-8") as fh:
                fh.write(xml)

            try:
                proc = subprocess.run(
                    [
                        "sf", "project", "deploy", "start",
                        "--source-dir", "force-app",
                        "--ignore-conflicts",
                        "--target-org", self.t.target_org,
                        "--json",
                    ],
                    cwd=tmp,
                    capture_output=True,
                    text=True,
                    timeout=_DEPLOY_TIMEOUT,
                )
            except FileNotFoundError as exc:
                raise LifecycleError(
                    "The 'sf' CLI was not found on PATH; cannot deploy the "
                    "DecisionTable metadata."
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise LifecycleError(
                    f"'sf project deploy start' timed out after {_DEPLOY_TIMEOUT}s "
                    f"deploying DecisionTable '{api_name}'."
                ) from exc

            stdout = (proc.stdout or "").strip()
            if proc.returncode != 0:
                detail = stdout or (proc.stderr or "").strip()
                raise LifecycleError(
                    f"Metadata deploy of DecisionTable '{api_name}' failed for org "
                    f"'{self.t.target_org}':\n{detail}"
                )
            self.log(f"Deployed DecisionTable '{api_name}' to org '{self.t.target_org}'.")
            try:
                parsed = json.loads(stdout) if stdout else {}
            except json.JSONDecodeError:
                parsed = {}
            return {"deployed": True, "dryRun": False, "apiName": api_name, "raw": parsed}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
