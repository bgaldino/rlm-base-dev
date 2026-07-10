#!/usr/bin/env python3
"""Safety-critical lifecycle for BRE Decision Table mutations.

Part of the self-contained ``scripts/decision_tables/`` toolkit (imports only
``_client`` from the package; nothing from ``tasks/``). :class:`LifecycleEngine`
wraps a :class:`_client.Transport` and encapsulates the Decision Table
lifecycle transitions the mutator CLIs need:

  * **activate** — set ``Metadata.status = Active`` (Tooling PATCH), then **poll**
    past the transient ``ActivationInProgress`` until ``Status = Active``.
    Activation is **asynchronous** (verified 262 / v67.0).
  * **deactivate** — set ``Metadata.status = Inactive``. Deactivation is
    **synchronous** (no ``InactivationInProgress`` transient), but the engine
    still confirms the terminal state.
  * **the active-edit guard** — an Active table's definition cannot be modified
    or deleted in place (``FIELD_NOT_UPDATABLE`` / "Can't edit an active Decision
    Table"). :meth:`assert_editable` refuses up front; :meth:`run_guarded_update`
    runs the deactivate → mutate → reactivate sequence for callers that opt in.
  * **refresh** — invoke the ``refreshDecisionTable`` standard action with the
    **live-verified** ``isDecisionTableIncremental`` flag (NOT the ``isIncremental``
    the CCI tasks send). Async + ~100/hr; returns ``Queued``.
  * **metadata deploy** — generate a ``.decisionTable-meta.xml`` into an **OS temp
    SFDX project outside the repo**, ``sf project deploy start`` it with
    ``--ignore-conflicts`` (temp project has no source tracking), and remove the
    temp tree — so no generated metadata churn lands in ``git status``.
  * **delete** — Tooling DELETE (setup object) or Connect DELETE (definition).

Two safety rules mirror the Expression Set engine
(``scripts/expression_sets/_lifecycle.py``):

  * A guarded update reactivates only when ``activate_after`` AND the mutate
    succeeded (or under dry-run). A **failed Connect full-body PATCH** can leave a
    half-mutated definition, so it is left DEACTIVATED by default rather than
    re-enabled. ``reactivate_on_failure`` relaxes this for the **Tooling
    ``Metadata`` PATCH**, which is atomic (a failed PATCH leaves the record
    byte-identical) — a failed Tooling edit then never knocks a live table offline.
  * The engine only reactivates a table that **was active** before the edit; a
    Draft/Inactive table is left as-is.

Dry-run is driven by the injected ``Transport`` (``Transport(dry_run=True)``):
mutating verbs are logged and skipped at the request layer; reads always run so a
dry-run still resolves ids and logs the real sequence. The engine additionally
skips the state *polls* under dry-run (nothing changes to wait for) and skips the
metadata deploy (logging what it would deploy).

Errors raise :class:`LifecycleError`. The engine takes the transport as its one
dependency, so a unit test can pass a fake transport and assert the call sequence
without an org.
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
    DecisionTableClientError,
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
    """Raised on a lifecycle failure in the Decision Table toolkit."""


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
        self.log(f"Set DecisionTable {record_id} Metadata.status = {status}.")

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
            f"{self.max_wait}s (last seen: {last!r}). Activation is asynchronous; "
            f"re-check with list_decision_tables.py or raise --max-wait."
        )

    def activate(self, record_id: str) -> None:
        """Set Status → Active and poll past ``ActivationInProgress`` (async)."""
        self._set_status(record_id, _STATUS_ACTIVE)
        self.wait_for_status(record_id, _STATUS_ACTIVE)

    def deactivate(self, record_id: str) -> None:
        """Set Status → Inactive (synchronous) and confirm."""
        self._set_status(record_id, _STATUS_INACTIVE)
        self.wait_for_status(record_id, _STATUS_INACTIVE)

    # -- Active-edit guard ---------------------------------------------

    def assert_editable(self, table_row: Dict[str, Any]) -> None:
        """Raise unless the table can be edited/deleted in place.

        An **Active** (or activating) table's definition cannot be modified or
        deleted (``FIELD_NOT_UPDATABLE`` / "Can't edit an active Decision Table").
        This refuses up front so a mutator that does NOT opt into deactivate-first
        fails with actionable guidance rather than an opaque platform error.
        """
        status = table_row.get("Status")
        name = table_row.get("DeveloperName") or table_row.get("Id")
        if status in (_STATUS_ACTIVE, _ACTIVATION_IN_PROGRESS):
            raise LifecycleError(
                f"DecisionTable '{name}' is {status}; its definition cannot be "
                f"edited or deleted in place (platform error "
                f"'FIELD_NOT_UPDATABLE' / \"Can't edit an active Decision Table\"). "
                f"Deactivate it first (pass --deactivate-first to do it "
                f"automatically, or run deactivate_decision_table.py), then edit "
                f"and reactivate."
            )

    def run_guarded_update(
        self,
        *,
        table_row: Dict[str, Any],
        mutate: Callable[[], None],
        activate_after: bool,
        reactivate_on_failure: bool = False,
        verb: str = "update",
    ) -> None:
        """Deactivate → mutate → reactivate an Active table (deactivate-first).

        ``mutate`` is the verb-specific body; it runs while the table is
        deactivated. Only a table that **was Active** is deactivated and later
        reactivated (``activate_after`` gates the reactivation). A Draft/Inactive
        table is mutated in place with no status change.

        On mutate failure the table is left DEACTIVATED by default (a failed
        Connect full-body PATCH can leave a half-mutated definition, and
        re-enabling that is worse than leaving it offline). ``reactivate_on_failure``
        relaxes this for the atomic Tooling ``Metadata`` PATCH (a failed PATCH
        leaves the record byte-identical). The failure is always re-raised.
        """
        record_id = table_row["Id"]
        was_active = table_row.get("Status") in (_STATUS_ACTIVE, _ACTIVATION_IN_PROGRESS)
        deactivated = False
        failure: Optional[Exception] = None
        mutate_succeeded = False

        try:
            if was_active:
                self.deactivate(record_id)
                deactivated = True
            else:
                self.log(
                    f"DecisionTable {record_id} is "
                    f"{table_row.get('Status')!r}; editing in place (no deactivate)."
                )
            mutate()
            mutate_succeeded = True
        except Exception as exc:  # noqa: BLE001 — re-raised below
            failure = exc
        finally:
            should_reactivate = (
                activate_after
                and was_active
                and (mutate_succeeded or self.dry_run or (reactivate_on_failure and deactivated))
            )
            if should_reactivate:
                if failure and not (mutate_succeeded or self.dry_run):
                    self.log(
                        f"{verb} failed, but it is an atomic Tooling PATCH (record "
                        f"unchanged on failure), so reactivating DecisionTable "
                        f"{record_id} rather than leaving it offline. The failure is "
                        f"still reported."
                    )
                try:
                    self.activate(record_id)
                except Exception as reactivate_exc:  # noqa: BLE001
                    if failure:
                        raise LifecycleError(
                            f"{verb} failed, and reactivation also failed: "
                            f"{reactivate_exc}"
                        ) from failure
                    raise
            elif failure and deactivated and not self.dry_run:
                self.log(
                    f"{verb} failed and may have partially applied. Leaving "
                    f"DecisionTable {record_id} DEACTIVATED to avoid re-enabling a "
                    f"corrupted definition. Inspect/restore it, then reactivate with "
                    f"activate_decision_table.py."
                )
            elif deactivated and not self.dry_run and not activate_after:
                self.log(
                    f"activate_after=false; leaving DecisionTable {record_id} "
                    f"DEACTIVATED as requested."
                )

        if failure:
            raise failure

    # -- Refresh -------------------------------------------------------

    def refresh(self, developer_name: str, *, incremental: bool = False,
                version_number: Optional[int] = None) -> Dict[str, Any]:
        """Invoke the ``refreshDecisionTable`` standard action (async, ~100/hr).

        Uses the **live-verified** ``isDecisionTableIncremental`` flag — the CCI
        tasks send ``isIncremental``, which the action ignores (silently falling
        back to a full refresh). Returns the normalized action result
        (``{"isSuccess", "status", "raw"}``); ``status`` is typically ``Queued``.
        The refresh is asynchronous — ``DecisionTable.LastSyncDate`` advancing is
        the completion signal, not this return value.
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

    # -- Delete --------------------------------------------------------

    def delete_tooling(self, record_id: str) -> Dict[str, Any]:
        """Delete a DecisionTable via the Tooling setup object (``0lD``)."""
        self.t.tooling_sobject("DELETE", "DecisionTable", record_id)
        self.log(f"Deleted DecisionTable {record_id} (Tooling).")
        return {"action": "delete", "path": "tooling", "id": record_id,
                "dryRun": self.dry_run}

    def delete_connect(self, connect_id: str) -> Dict[str, Any]:
        """Delete a Decision Table definition via the Connect resource."""
        self.t.connect("DELETE", f"{DEFINITIONS_PATH}/{connect_id}")
        self.log(f"Deleted Decision Table definition {connect_id} (Connect).")
        return {"action": "delete", "path": "connect", "id": connect_id,
                "dryRun": self.dry_run}
