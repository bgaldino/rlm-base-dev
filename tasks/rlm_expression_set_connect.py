"""
Expression Set structural management via the BRE Connect API.

Provides four CCI tasks:
  - ExportExpressionSet: GET full definition → JSON file
  - ApplyExpressionSetOverlay: Declarative step/variable manipulation
  - ImportExpressionSet: Full replacement from JSON file
  - DeleteExpressionSet: Delete an expression set (or just an old version)

BRE Connect API endpoint (v58.0+):
  /services/data/v{version}/connect/business-rules/expression-set/{id}
  where {id} is the ExpressionSet runtime record Id (key prefix 9QL).

Connect mutation behavior (verified live on 262 / v67.0 — see
docs/references/expression-set-connect-api-reference.md for the full reference):

  * HTML-entity normalization: the Connect GET serializer escapes JSON-in-string
    content (customElement.parameters[].value, advancedCondition.criteria[].value,
    formula text) as &quot;/&#39;. The engine rejects those entities on input
    (flat: "Syntax error. Found '&'"; nested: an opaque "Error processing JSON"),
    so every mutation HTML-unescapes the payload (_normalize_html_entities)
    immediately before the Connect call. Pass `normalize_html_entities: false`
    to send the payload as-is.
  * PATCH requires an inactive/disabled version. An enabled version rejects PATCH
    with "An enabled Expression Set Version cannot be updated/deleted." Every
    mutation runs deactivate→PATCH→reactivate. Reactivation is idempotent (see
    _set_version_active) because a PATCH body carrying enabled=true reactivates
    the version itself.
  * PATCH is NOT atomic: a failed (400) PATCH still commits the parts it
    accepted. On failure we DO NOT reactivate — a half-mutated pricing procedure
    must never be re-enabled silently. We leave it deactivated and raise loudly,
    but restore the cascaded procedure plans: an inactive plan silently skips
    its procedures, while an active plan over an inactive version fails loudly.
  * Version `id` differs by verb: a PATCH body KEEPS the version-level `id` (the
    server matches it in place); a POST-create body OMITS it. Top-level
    `id`/`error` are always stripped (output-only).
  * ResourceInitializationType is immutable once set, and the PATCH body must
    equal the stored ExpressionSet.ResourceInitializationType (enum Default|Off).
    GET reports "Off" even when the stored field is null (seeded procedures), so
    we align the stored field once before patching (_ensure_resource_initialization_type).
  * Version identity comes from the ExpressionSetVersion sObject (source of
    truth), not GET — GET can transiently serve a stale clone version apiName
    (_check_version_name_consistency warns on divergence).

Overlays and import payloads are schema-validated BEFORE any Connect call (see
tasks/expression_set_schema.py) so a malformed step graph fails locally with an
actionable message instead of as the opaque server response the PATCH/POST
handler can produce. The validator also WARNS when a value still
carries HTML entities (i.e. un-normalized GET output). Pass
`skip_validation: true` to bypass.
"""
import html
import json
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

try:
    from cumulusci.tasks.salesforce import BaseSalesforceTask
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceTask = object
    BaseTask = object
    TaskOptionsError = Exception

from tasks.expression_set_schema import (
    existing_step_differences,
    overlay_step_content_errors,
    detect_kind,
    validate_definition,
    validate_overlay,
    validate_overlay_against_definition,
)
# Stdlib-only modules shared with the standalone toolkit (no CumulusCI import): the
# version guards and the one deactivate → mutate → recover engine.
from scripts.expression_sets._engine import (
    ROW_LOCK,
    ROW_LOCK_ATTEMPTS,
    LifecycleCore,
    row_lock_backoff,
)
from scripts.expression_sets._guards import (
    NO_ACTIVATION_CCI_APPLY,
    NO_ACTIVATION_CCI_IMPORT,
    VERSION_FIELDS,
    executing_version,
    import_target_refusal,
    null_rank_delete_refusal,
    null_rank_reactivation_refusal,
    other_active_versions_refusal,
    relabel_command,
    select_version,
    version_name_collision_refusal,
    rank_order_warning,
    target_version_warning,
)


_REQUEST_TIMEOUT = 120


class _TaskLifecycle(LifecycleCore):
    """The shared lifecycle engine, adapted to an ``ExpressionSetConnectBase`` task.

    Every read, write, wait and lifecycle step goes through the task's own methods
    (``_soql_query``, ``_patch_sobject``, ``_set_version_active``,
    ``_wait_for_version_state``, ``_cascade_*``, ``_report_procedure_health`` …),
    so a subclass or test that overrides one of them changes the engine's
    behaviour exactly as it changed the task's before the engine was shared.
    Failures raise ``TaskOptionsError``; a dry-run is announced, not issued.
    """

    error_class = TaskOptionsError
    dry_run_style = "announce"

    def __init__(self, task, dry_run: bool):
        super().__init__(dry_run=bool(dry_run))
        self.task = task

    # I/O
    def query(self, soql):
        return self.task._soql_query(soql)

    def write_sobject(self, sobject, record_id, body):
        self.task._patch_sobject(sobject, record_id, body)

    def delete_sobject(self, sobject, record_id):
        self.task._delete_sobject(sobject, record_id)

    def delete_definition(self, es_id):
        return self.task._delete_expression_set_via_connect(es_id)

    def wait_for_version_state(self, version_id, active):
        self.task._wait_for_version_state(version_id, active)

    def emit(self, level, message):
        getattr(self.task.logger, level)(message)

    def restore_target_org(self):
        return self.task.org_config.username

    def command_target_org(self):
        return self.task._org_username()

    def definition_name(self, es_def_id):
        return self.task._definition_name(es_def_id)

    # Lifecycle steps, through the task's (overridable) methods. ``force`` is
    # passed only when the engine passes one, matching the task's call shapes.
    def set_version_active(self, version_id, active, *, force=None):
        if force is None:
            self.task._set_version_active(version_id, active, self.dry_run)
        else:
            self.task._set_version_active(version_id, active, self.dry_run, force=force)

    def find_referencing_procedure_plans(self, es_def_id):
        return self.task._find_referencing_procedure_plans(es_def_id)

    def cascade_deactivate_procedure_plans(self, es_def_id, *, rollback=True):
        if rollback:
            return self.task._cascade_deactivate_procedure_plans(es_def_id, self.dry_run)
        return self.task._cascade_deactivate_procedure_plans(
            es_def_id, self.dry_run, rollback=False
        )

    def cascade_reactivate_procedure_plans(self, version_ids):
        self.task._cascade_reactivate_procedure_plans(version_ids, self.dry_run)

    def report_procedure_health(self, es_def_id, esv_id, *, taken_down,
                                version_taken_down, version_may_be_half_written=False):
        return self.task._report_procedure_health(
            es_def_id, esv_id, taken_down=taken_down,
            version_taken_down=version_taken_down,
            version_may_be_half_written=version_may_be_half_written,
        )


def _parse_bool_option(value: Any, default: bool) -> bool:
    """Parse a CCI bool option: None → default, bool → as-is, string → truthy match."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes")


class ExpressionSetConnectBase(BaseSalesforceTask):
    """Base class with BRE Connect API helpers and lifecycle methods."""

    task_options: Dict[str, Dict[str, Any]] = {}

    # -- Auth / URL properties -----------------------------------------

    @property
    def _api_version(self) -> str:
        return (
            self.options.get("api_version")
            or getattr(self.org_config, "api_version", None)
            or getattr(
                self.project_config,
                "project__package__api_version",
                "68.0",
            )
        )

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.org_config.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def _base_url(self) -> str:
        return f"{self.org_config.instance_url}/services/data/v{self._api_version}"

    @property
    def _connect_url(self) -> str:
        return f"{self._base_url}/connect/business-rules/expression-set"

    # -- SOQL helpers --------------------------------------------------

    @staticmethod
    def _soql_escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _soql_query(self, soql: str) -> List[dict]:
        # Raise on HTTP failure rather than returning []. Callers like
        # ImportExpressionSet use an empty result to decide whether to
        # POST-create vs PATCH-update; swallowing a 401/500 here would route a
        # transient error into the create path and risk duplicate definitions.
        url = f"{self._base_url}/query"
        resp = requests.get(
            url, headers=self._headers, params={"q": soql}, timeout=_REQUEST_TIMEOUT
        )
        if resp.status_code != 200:
            raise TaskOptionsError(
                f"SOQL query failed ({resp.status_code}): {resp.text}"
            )
        body = resp.json()
        records: List[dict] = body.get("records", [])
        while not body.get("done", True) and body.get("nextRecordsUrl"):
            nurl = f"{self.org_config.instance_url}{body['nextRecordsUrl']}"
            resp = requests.get(nurl, headers=self._headers, timeout=_REQUEST_TIMEOUT)
            if resp.status_code != 200:
                raise TaskOptionsError(
                    f"SOQL pagination failed ({resp.status_code}): {resp.text}"
                )
            body = resp.json()
            records.extend(body.get("records", []))
        return records

    # -- REST helpers --------------------------------------------------

    def _patch_sobject(self, sobject: str, record_id: str, payload: dict) -> None:
        url = f"{self._base_url}/sobjects/{sobject}/{record_id}"
        # The shared row-lock policy (the toolkit applies it in its engine adapter).
        max_attempts = ROW_LOCK_ATTEMPTS
        for attempt in range(1, max_attempts + 1):
            resp = requests.patch(
                url, headers=self._headers, json=payload, timeout=_REQUEST_TIMEOUT
            )
            if resp.status_code in (200, 204):
                return
            resp_text = resp.text or ""
            if ROW_LOCK in resp_text and attempt < max_attempts:
                wait = row_lock_backoff(attempt)
                self.logger.warning(
                    "Row lock on %s/%s (attempt %s/%s). Retrying in %ss.",
                    sobject, record_id, attempt, max_attempts, wait,
                )
                time.sleep(wait)
                continue
            raise TaskOptionsError(
                f"PATCH {sobject}/{record_id} failed ({resp.status_code}): {resp_text}"
            )

    def _delete_sobject(self, sobject: str, record_id: str) -> None:
        url = f"{self._base_url}/sobjects/{sobject}/{record_id}"
        resp = requests.delete(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if resp.status_code not in (200, 204):
            raise TaskOptionsError(
                f"DELETE {sobject}/{record_id} failed "
                f"({resp.status_code}): {resp.text}"
            )

    # -- BRE Connect API helpers ---------------------------------------

    def _get_expression_set_definition_id(self, api_name: str) -> str:
        safe = self._soql_escape(api_name)
        records = self._soql_query(
            f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{safe}'"
        )
        if not records:
            raise TaskOptionsError(
                f"ExpressionSetDefinition '{api_name}' not found in org."
            )
        return records[0]["Id"]

    def _get_expression_set_id(self, api_name: str) -> str:
        """Get the ExpressionSet runtime record ID (used by the Connect API)."""
        safe = self._soql_escape(api_name)
        records = self._soql_query(
            "SELECT Id FROM ExpressionSet "
            f"WHERE ExpressionSetDefinition.DeveloperName = '{safe}'"
        )
        if not records:
            raise TaskOptionsError(
                f"ExpressionSet for '{api_name}' not found in org."
            )
        return records[0]["Id"]

    def _resolve_version_by_es_id(self, es_id: str) -> dict:
        """Resolve the runtime ExpressionSetVersion from the ExpressionSet Id.

        The ExpressionSetVersion sObject is the source of truth for the
        version's Id / ApiName / IsActive — unlike the Connect GET payload,
        whose version identity can be a transiently stale clone name. We match
        on the ExpressionSetId FK rather than guessing by naming convention.

        Prefer the version actually executing (the shared
        ``_guards.executing_version``: highest Rank among active versions whose
        date window covers now) over a merely higher VersionNumber:
        mutating/deactivating the latest-numbered draft while a different version
        is live would target the wrong record. Absent an executing version, the
        active (then highest-numbered) version comes first.
        """
        safe = self._soql_escape(es_id)
        records = self._soql_query(
            f"SELECT {VERSION_FIELDS} "
            f"FROM ExpressionSetVersion WHERE ExpressionSetId = '{safe}' "
            "ORDER BY IsActive DESC, VersionNumber DESC"
        )
        if not records:
            raise TaskOptionsError(
                f"No ExpressionSetVersion found for ExpressionSet {es_id}."
            )
        try:
            running = executing_version(records)
            note = rank_order_warning(records)
        except ValueError as exc:  # an unreadable StartDateTime/EndDateTime
            raise TaskOptionsError(str(exc)) from exc
        chosen = running or records[0]
        active = [r for r in records if r.get("IsActive")]
        message = target_version_warning(es_id, active, running, chosen)
        if message:
            self.logger.warning(message)
            if note:
                self.logger.warning(note)
        return chosen

    def _org_username(self) -> Optional[str]:
        """The org's username, the ``--target-org`` a printed toolkit or ``sf``
        command needs (never the access token); None when there is no org."""
        return getattr(getattr(self, "org_config", None), "username", None)

    def _definition_name(self, es_def_id: str) -> Optional[str]:
        """The set's DeveloperName, for a printed command; None when unreadable."""
        try:
            rows = self._soql_query(
                "SELECT DeveloperName FROM ExpressionSetDefinition "
                f"WHERE Id = '{self._soql_escape(es_def_id)}'")
        except Exception:  # noqa: BLE001 -- only fills a message
            return None
        return (rows[0].get("DeveloperName") if rows else None) or None

    def _list_versions(self, es_id: str) -> List[dict]:
        """Every ExpressionSetVersion of an ExpressionSet, lowest number first, with
        the fields the shared executing-version resolver reads (Rank, date window)."""
        return self._soql_query(
            f"SELECT {VERSION_FIELDS} FROM ExpressionSetVersion "
            f"WHERE ExpressionSetId = '{self._soql_escape(es_id)}' "
            "ORDER BY VersionNumber"
        )

    def _resolve_label_version(
        self, esv: dict, version_api_name: Optional[str], versions: List[dict]
    ) -> Optional[dict]:
        """The version an overlay edits, which receives the overlay's labels.

        ``esv`` is the active-first version the activation cycle toggles; an
        explicit ``version_api_name`` can select a different (draft) version.
        Returns None when the named version has no sObject row, so the
        overlay's labels are dropped rather than written to the wrong version.
        """
        if not version_api_name or version_api_name == esv.get("ApiName"):
            return esv
        match = next((v for v in versions if v.get("ApiName") == version_api_name), None)
        if match is None:
            self.logger.warning(
                "No ExpressionSetVersion named %s; the overlay's step labels "
                "will not be applied.", version_api_name,
            )
        return match

    def _check_version_name_consistency(
        self, es_id: str, esv: dict, definition: Optional[dict] = None
    ) -> None:
        """Warn if Connect GET's version apiName disagrees with the sObject.

        A stale clone apiName served by GET breaks PATCH. This is usually
        transient and resolves on re-GET; surface it so a failure is
        diagnosable rather than mysterious. Pass ``definition`` to reuse an
        already-fetched GET payload instead of issuing another round-trip.
        """
        try:
            if definition is None:
                definition = self._get_expression_set_via_connect(es_id)
            versions = definition.get("versions", [])
            get_apis = [v.get("apiName") for v in versions if v.get("apiName")]
        except Exception:
            return
        sobject_api = esv.get("ApiName")
        # On a multi-version set the GET lists every version, and the targeted one
        # need not come first: warn only when none of them carries its name.
        if get_apis and sobject_api and sobject_api not in get_apis:
            get_api = get_apis[0] if len(get_apis) == 1 else ", ".join(get_apis)
            self.logger.warning(
                "Connect GET version apiName '%s' disagrees with the "
                "ExpressionSetVersion sObject ApiName '%s' (stale clone name). "
                "PATCH may fail; re-run to let the GET cache settle.",
                get_api, sobject_api,
            )

    def _ensure_resource_initialization_type(
        self, es_id: str, dry_run: bool, desired: Optional[str] = None
    ) -> None:
        """Align stored ExpressionSet.ResourceInitializationType before PATCH.

        Connect GET reports "Off" while the sObject stores null on seeded
        procedures; PATCH validates the body against the stored value and
        rejects with "resourceInitializationType is set to null and cannot be
        changed." Writing the stored field to the value the PATCH body carries
        aligns the two so the PATCH is accepted.

        ``desired`` is the value the PATCH body will carry (the payload's
        ``resourceInitializationType``). It defaults to "Off" — the value GET
        serializes over a stored null, which is what an overlay or a GET-derived
        export sends. A payload that declares "Default" must pass it here, or the
        stored field would be aligned to "Off" and then mismatch the body.

        The field is immutable once set: if it already holds a value, this only
        raises on a conflict (before _run_connect_mutation deactivates anything)
        and never rewrites it. The logic is the shared engine's
        (``scripts/expression_sets/_engine.py``).
        """
        self._lifecycle(dry_run).ensure_resource_initialization_type_impl(es_id, desired)

    def _lifecycle(self, dry_run: bool) -> "_TaskLifecycle":
        """The shared lifecycle engine, bound to this task's seams for one call."""
        return _TaskLifecycle(self, dry_run)

    def _connect_error(self, verb: str, es_id: str, resp) -> TaskOptionsError:
        """Build a TaskOptionsError surfacing the Connect errorCode/message."""
        detail = resp.text or ""
        try:
            body = resp.json()
            if isinstance(body, list) and body:
                body = body[0]
            if isinstance(body, dict):
                detail = (
                    f"{body.get('errorCode', '')}: {body.get('message', detail)}"
                ).strip(": ")
        except Exception:
            pass
        return TaskOptionsError(
            f"{verb} expression set {es_id} failed ({resp.status_code}): {detail}"
        )

    def _get_expression_set_via_connect(self, es_id: str) -> dict:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.get(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if not resp.ok:
            raise self._connect_error("GET", es_id, resp)
        return resp.json()

    def _patch_expression_set_via_connect(self, es_id: str, payload: dict) -> dict:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.patch(
            url, headers=self._headers, json=payload, timeout=_REQUEST_TIMEOUT
        )
        if not resp.ok:
            raise self._connect_error("PATCH", es_id, resp)
        # A full-graph PATCH rebuilds every step label from its spaceless name;
        # _run_connect_mutation reads this flag to restore them before activation.
        self._labels_clobbered = True
        return resp.json() if resp.content else {}

    def _post_expression_set_via_connect(self, payload: dict) -> dict:
        resp = requests.post(
            self._connect_url, headers=self._headers, json=payload,
            timeout=_REQUEST_TIMEOUT,
        )
        if resp.status_code not in (200, 201):
            raise self._connect_error("POST", "(new)", resp)
        return resp.json()

    def _delete_expression_set_via_connect(self, es_id: str) -> None:
        url = f"{self._connect_url}/{es_id}"
        resp = requests.delete(url, headers=self._headers, timeout=_REQUEST_TIMEOUT)
        if resp.status_code not in (200, 204):
            raise self._connect_error("DELETE", es_id, resp)

    # -- Version lifecycle helpers -------------------------------------

    def _set_version_active(
        self, version_id: str, active: bool, dry_run: bool, *, force: bool = False
    ):
        """Set ExpressionSetVersion.IsActive, idempotent unless ``force``.

        ``force`` sends the PATCH even when a read already shows the desired
        state. Recovery after an unconfirmed deactivation uses it: the stale read
        that made the deactivation poll time out would otherwise skip the
        reactivation. A forced PATCH rejected with the platform's "already
        enabled" error is taken as active; any other rejection raises. Under
        dry_run it logs what it would do and reads nothing. Idempotent: a
        Connect PATCH whose body carries ``enabled: true`` reactivates the
        version itself, so a later explicit reactivation is skipped rather than
        rejected.
        """
        self._lifecycle(dry_run).set_version_active_impl(version_id, active, force=force)

    def _wait_for_version_state(self, version_id: str, active: bool):
        self._lifecycle(False).poll_version_state(
            version_id, active,
            max_wait=self._int_option("max_wait_seconds", 45),
            poll=self._int_option("poll_interval_seconds", 3, minimum=1),
            sleep=time.sleep,
        )

    # -- Cascade deactivation (procedure plan references) --------------

    def _find_referencing_procedure_plans(self, es_def_id: str) -> List[dict]:
        return self._lifecycle(False).find_referencing_procedure_plans_impl(es_def_id)

    def _cascade_deactivate_procedure_plans(
        self, es_def_id: str, dry_run: bool, *, rollback: bool = True
    ) -> List[str]:
        """Deactivate any active procedure plan versions referencing this ES.
        Returns list of version IDs that were deactivated.

        If setup fails partway through, rollback only the procedure-plan
        versions this cascade already deactivated. A later Connect PATCH
        failure also restores them (see _run_connect_mutation); this rollback
        covers only pre-mutation cascade setup. With ``rollback=False`` (the
        emergency shutdown after a failed PATCH) every plan is attempted,
        nothing is turned back on, and the raised error's ``left_inactive``
        names the plans it did turn off.
        """
        return self._lifecycle(dry_run).cascade_deactivate_impl(es_def_id, rollback=rollback)

    def _cascade_reactivate_procedure_plans(
        self, version_ids: List[str], dry_run: bool
    ):
        """Reactivate each plan version; every id is attempted before raising,
        so one failed PATCH can't leave the later plans offline."""
        self._lifecycle(dry_run).cascade_reactivate_impl(version_ids)

    # -- Shared mutation lifecycle -------------------------------------

    def _run_connect_mutation(
        self,
        *,
        es_def_id: str,
        esv: dict,
        mutate,
        dry_run: bool,
        activate_after: bool,
        cascade: bool,
        verb: str = "mutation",
        extra_labels: Optional[Dict[str, str]] = None,
        label_esv: Optional[dict] = None,
        label_versions: Optional[List[dict]] = None,
    ) -> None:
        """Run a Connect mutation and keep the version's step labels intact.

        Every Connect full-graph PATCH resets all step labels to the spaceless
        step names, so label preservation lives HERE rather than in each
        caller: any mutator routed through this method gets it without opting
        in. Labels are snapshotted from the Tooling API before ``mutate``; if
        ``mutate`` PATCHed (``_patch_expression_set_via_connect`` sets
        ``_labels_clobbered``), they are written back while the version is
        still inactive, before the existing activation. ``extra_labels``
        (e.g. an overlay's labels for new steps) are layered on top.
        The PATCH sends, and so relabels, every version in the definition:
        ``label_versions`` lists them all (default: just ``esv``), and each is
        captured and restored. ``extra_labels`` go to ``label_esv`` (default
        ``esv``), the version the mutation edits, e.g. an overlay's draft.

        Label reads/writes are best-effort; activation failures propagate.
        Restore runs only after the mutation fully succeeded; the
        ``preserve_labels`` task option (default true) turns it off. See
        ``_run_activation_cycle`` for the activation guarantees.
        """
        preserve_requested = self._bool_option(self.options.get("preserve_labels"), True)
        label_target = label_esv or esv
        versions = list(label_versions or [esv])
        if not any(v.get("VersionNumber") == label_target.get("VersionNumber")
                   for v in versions):
            versions.append(label_target)
        captured: List[tuple] = []
        if preserve_requested and not dry_run:
            for version in versions:
                labels = self._capture_step_labels(es_def_id, version)
                if version.get("VersionNumber") == label_target.get("VersionNumber"):
                    labels.update(extra_labels or {})
                if labels:
                    captured.append((version, labels))
        elif dry_run and preserve_requested:
            self.logger.info("[dry-run] Would restore step labels after the PATCH.")
        self._labels_clobbered = False
        # Each version's state once this run ends, for a printed relabel command:
        # the cycled version ends active only with activate_after; the others keep
        # their own state.
        self._label_final_active = {
            version.get("Id"): (bool(activate_after) if version.get("Id") == esv.get("Id")
                                else bool(version.get("IsActive")))
            for version, _ in captured
        }

        def mutate_and_restore():
            mutate()
            if self._labels_clobbered:
                for version, labels in captured:
                    self._restore_step_labels(
                        es_def_id=es_def_id, esv=version, labels=labels
                    )

        self._run_activation_cycle(
            es_def_id=es_def_id, esv=esv, mutate=mutate_and_restore, dry_run=dry_run,
            activate_after=activate_after, cascade=cascade, verb=verb,
        )

    def _run_activation_cycle(
        self,
        *,
        es_def_id: str,
        esv: dict,
        mutate,
        dry_run: bool,
        activate_after: bool,
        cascade: bool,
        verb: str,
    ) -> None:
        """Run the safety-critical deactivate→mutate→reactivate lifecycle.

        Shared by ApplyExpressionSetOverlay and ImportExpressionSet's
        replace path so the guarantees below live in ONE place and cannot drift:

          * A Connect mutation requires the version inactive, so an active
            version (and any referencing procedure-plan versions, when
            ``cascade``) is deactivated first.
          * ``mutate`` is the verb-specific body (Apply: GET→overlay→validate→
            PATCH→verify; Import: strip→PATCH). It runs while the version is
            deactivated and is responsible for its own dry-run handling.
          * Reactivation is governed by the explicit ``activate_after`` (NOT by
            the prior active state — an explicit false must win, leaving the
            version inactive for inspection).
          * PATCH is NOT atomic: a failed PATCH can leave a half-mutated,
            deactivated version. It is NEVER reactivated — re-enabling a
            corrupted pricing procedure is worse than leaving it offline. So
            reactivation happens only when ``activate_after`` AND the mutate body
            succeeded, or failed before it started (nothing was written, e.g.
            the deactivation poll timed out), or in dry-run.
          * A failed PATCH still restores the cascaded procedure plans (when
            ``activate_after``). A deactivated plan is skipped: pricing silently
            falls back to the Revenue Settings default procedure and the plan's
            other procedures stop running. An active plan over an inactive
            version fails loudly at pricing time instead (both live-checked on
            264 / v68.0). After any failure, including a failed reactivation,
            the version and every referencing plan are re-read. Records this
            run deactivated get a restore command; other inactive plan versions
            are listed for inspection only.

        Re-raises the original failure (chaining a reactivation failure onto it
        when both happen) so the caller surfaces it.

        The state machine is the shared engine's
        (``scripts/expression_sets/_engine.py``, ``LifecycleCore.run_mutation``);
        it reaches the org through this task's methods (see ``_TaskLifecycle``).
        """
        self._lifecycle(dry_run).run_mutation(
            es_def_id=es_def_id, esv=esv, mutate=mutate,
            activate_after=activate_after, cascade=cascade, verb=verb,
        )

    # -- Step labels (Tooling API) -------------------------------------
    #
    # A step's readable label is not part of the Connect representation, and a
    # Connect full-graph PATCH rebuilds every label from the spaceless step name
    # ("Get Base Prices from Pricebook" -> "Getbasepricesfrompricebook"). Labels
    # live only on the Tooling ExpressionSetDefinitionVersion
    # Metadata.steps[].label, so the Connect mutators snapshot them before the
    # PATCH and write them back afterwards (wired in _run_connect_mutation).
    # scripts/expression_sets/_tooling.py is the standalone toolkit's copy.

    _ESDV_SOBJECT = "ExpressionSetDefinitionVersion"

    def _tooling_request(self, method: str, path: str, payload=None):
        url = f"{self._base_url}/tooling/{path}"
        resp = requests.request(
            method, url, headers=self._headers, json=payload,
            timeout=_REQUEST_TIMEOUT,
        )
        if not resp.ok:
            raise TaskOptionsError(
                f"Tooling {method} {path} failed ({resp.status_code}): {resp.text}"
            )
        return resp.json() if resp.content else {}

    def _resolve_esdv_id(self, es_def_id: str, version_number) -> str:
        # Resolve by definition Id + VersionNumber, never by DeveloperName: a
        # Connect PATCH rewrites the ESDV DeveloperName in place, so a lookup
        # by the version ApiName right after one can miss.
        where = f"ExpressionSetDefinitionId = '{self._soql_escape(es_def_id)}'"
        if version_number is not None:
            where += f" AND VersionNumber = {int(version_number)}"
        soql = (
            f"SELECT Id FROM {self._ESDV_SOBJECT} WHERE {where} "
            "ORDER BY VersionNumber DESC"
        )
        body = self._tooling_request("GET", f"query?q={quote(soql)}")
        records = body.get("records") or []
        if not records:
            raise TaskOptionsError(
                f"No {self._ESDV_SOBJECT} found for definition {es_def_id}."
            )
        return records[0]["Id"]

    def _get_step_metadata(self, esdv_id: str) -> dict:
        body = self._tooling_request("GET", f"sobjects/{self._ESDV_SOBJECT}/{esdv_id}")
        metadata = body.get("Metadata")
        if not isinstance(metadata, dict):
            raise TaskOptionsError(f"{self._ESDV_SOBJECT} {esdv_id} returned no Metadata.")
        return metadata

    @staticmethod
    def _step_labels(metadata: dict) -> Dict[str, Optional[str]]:
        return {
            step["name"]: step.get("label")
            for step in metadata.get("steps") or []
            if isinstance(step, dict) and step.get("name")
        }

    @staticmethod
    def _overlay_labels(overlay: dict) -> Dict[str, str]:
        """Labels an overlay ships: a top-level map or per-step labels."""
        out: Dict[str, str] = {}
        top = overlay.get("labels")
        if isinstance(top, dict):
            out.update({k: v for k, v in top.items() if isinstance(v, str)})
        for operation in ("addSteps", "updateSteps"):
            for step in overlay.get(operation) or []:
                if isinstance(step, dict) and step.get("name") and isinstance(step.get("label"), str):
                    out[step["name"]] = step["label"]
        return out

    def _capture_step_labels(self, es_def_id: str, esv: dict) -> Dict[str, str]:
        """Snapshot the readable labels a Connect PATCH is about to reset.

        Best-effort: a failure logs a warning and returns ``{}`` so capturing
        labels can never block the mutation itself.
        """
        try:
            esdv_id = self._resolve_esdv_id(es_def_id, esv.get("VersionNumber"))
            labels = self._step_labels(self._get_step_metadata(esdv_id))
        except Exception as exc:  # noqa: BLE001 — labels are cosmetic
            self.logger.warning(
                "Could not read step labels before the PATCH (%s); they will "
                "not be restored.", exc,
            )
            return {}
        return {n: l for n, l in labels.items() if l and l != n}

    def _relabel_hint(self, es_def_id: str, esv: dict, labels: Dict[str, str],
                      current: Optional[Dict[str, str]]) -> str:
        """How to restore ``labels`` on ``esv``, as a relabel_expression_set.py
        command that runs as printed: the labels (only steps the version still has,
        when known) go to a JSON file; the command names the org's username and the
        set, and adds --no-activate when the version ends this run inactive, so it
        does not switch it on."""
        keep = {n: l for n, l in labels.items()
                if l and (current is None or n in current)}
        if not keep:
            return (f"nothing to restore on {esv.get('ApiName')} (none of its labelled "
                    "steps remain).")
        final_active = getattr(self, "_label_final_active", {}).get(
            esv.get("Id"), bool(esv.get("IsActive")))
        try:
            with tempfile.NamedTemporaryFile(
                    "w", encoding="utf-8", suffix=".json", delete=False,
                    prefix=f"relabel-{esv.get('ApiName')}-") as fh:
                json.dump(keep, fh, indent=2, ensure_ascii=False)
                path = fh.name
        except OSError as exc:
            return f"could not save the labels to a file ({exc})."
        command = relabel_command(path, target_org=self._org_username(),
                                  es_api_name=self._definition_name(es_def_id),
                                  version_api_name=esv.get("ApiName"),
                                  no_activate=not final_active)
        if command is None:  # the org or the set name is unknown: describe it
            return (f"run relabel_expression_set.py on {esv.get('ApiName')} with "
                    f"--labels-file {path} (the labels saved)"
                    + (", adding --no-activate." if not final_active else "."))
        return "run " + command

    def _restore_step_labels(
        self,
        *,
        es_def_id: str,
        esv: dict,
        labels: Dict[str, str],
    ) -> bool:
        """Write step labels back after a Connect PATCH reset them.

        Called inside the Connect mutation's inactive window. Label failures
        are cosmetic and logged; the enclosing lifecycle still reactivates the
        version. Steps the mutation removed or renamed are skipped.
        """
        if not labels:
            return True
        current: Optional[Dict[str, str]] = None
        try:
            esdv_id = self._resolve_esdv_id(es_def_id, esv.get("VersionNumber"))
            metadata = self._get_step_metadata(esdv_id)
            current = self._step_labels(metadata)
            planned = {
                n: l for n, l in labels.items()
                if l and n in current and current[n] != l
            }
            if not planned:
                self.logger.info("Step labels already current; nothing to restore.")
                return True
            for step in metadata.get("steps") or []:
                if isinstance(step, dict) and step.get("name") in planned:
                    step["label"] = planned[step["name"]]
            # `urls` is server-emitted and rejected on write.
            body = {k: v for k, v in metadata.items() if k != "urls"}
            self._tooling_request(
                "PATCH", f"sobjects/{self._ESDV_SOBJECT}/{esdv_id}",
                {"Metadata": body},
            )
            stored = self._step_labels(self._get_step_metadata(esdv_id))
            missing = sorted(n for n, l in planned.items() if stored.get(n) != l)
            if missing:
                raise TaskOptionsError(f"labels did not persist for {missing}")
        except Exception as exc:  # noqa: BLE001 — only label work is cosmetic
            self.logger.warning(
                "The Connect mutation succeeded, but restoring step labels "
                "failed (%s). To restore them: %s", exc,
                self._relabel_hint(es_def_id, esv, labels, current),
            )
            return False
        self.logger.info("Restored %d step label(s).", len(planned))
        return True

    @staticmethod
    def _keep_patched_version_inactive(payload: dict, version_id: str) -> dict:
        """Prevent a Connect PATCH from reactivating the version before relabeling."""
        versions = payload.get("versions") or []
        target = next(
            (v for v in versions if isinstance(v, dict) and v.get("id") == version_id),
            None,
        )
        if target is None:
            raise TaskOptionsError(f"PATCH payload has no version id {version_id}.")
        target["enabled"] = False
        return payload

    def _report_procedure_health(
        self,
        es_def_id: str,
        esv_id: str,
        *,
        taken_down: List[str],
        version_taken_down: bool,
        version_may_be_half_written: bool = False,
    ) -> List[str]:
        """Re-read activation state after a failure and warn on anything off.

        Only records this run deactivated get a restore command; their prior
        state is known to be active. Other inactive procedure-plan versions
        referencing the expression set are listed for inspection only: a plan
        can keep inactive draft, expired or lower-ranked versions on purpose.

        ``version_may_be_half_written`` marks a failed definition PATCH: if the
        version still reads active, restoring a plan would route pricing to it,
        so the report says to inspect and deactivate the version first. Restore
        commands name this org's username.
        """
        return self._lifecycle(False).report_procedure_health_impl(
            es_def_id, esv_id, taken_down=taken_down,
            version_taken_down=version_taken_down,
            version_may_be_half_written=version_may_be_half_written,
        )

    # -- Payload sanitization -----------------------------------------
    #
    # Deny-list, not allow-list. The Connect Input representation accepts almost
    # every field the Output representation returns; the only fields that MUST
    # be removed are the output-only ones the parser rejects. The TOP-LEVEL
    # `id`/`error` are output-only and rejected on input for both verbs.
    #
    # The version-level `id` is verb-dependent:
    #   * PATCH (replace) KEEPS it — the server matches the version in place;
    #     stripping it makes the server treat the version as new and gack.
    #   * POST (create) OMITS it — a create body carrying a source-org version
    #     id (a 9QM from `export_expression_set`) makes the server reject or
    #     mis-bind the new version. `for_create=True` strips versions[].id.

    _TOP_LEVEL_DENY = {"id", "error"}

    @classmethod
    def _strip_readonly_fields(cls, payload: dict, for_create: bool = False) -> dict:
        """Remove output-only fields the Connect API rejects on PATCH/POST.

        Keeps everything else, including top-level interfaceSourceType /
        resourceInitializationType / contextDefinitions. The version-level `id`
        is kept for a PATCH (which needs it to match in place) and stripped when
        ``for_create`` is set (a POST-create must not carry a source-org id).
        """
        stripped = {k: v for k, v in payload.items() if k not in cls._TOP_LEVEL_DENY}
        if for_create:
            versions = stripped.get("versions")
            if isinstance(versions, list):
                stripped["versions"] = [
                    {k: v for k, v in version.items() if k != "id"}
                    if isinstance(version, dict)
                    else version
                    for version in versions
                ]
        return stripped

    @staticmethod
    def _rewrite_version_id(payload: dict, target_version_id: str) -> dict:
        """Rewrite versions[0].id to the target org's version id for PATCH.

        An export-from-source/import-into-target workflow carries the source
        org's version id in the payload, while the Connect PATCH endpoint
        matches on the target version id. Without this rewrite the server
        rejects or mis-binds the version. Idempotent when the id already
        matches (same-org re-import).
        """
        versions = payload.get("versions")
        if not isinstance(versions, list) or not versions:
            return payload
        # Only rewrite the first/active version — the PATCH operates on a
        # single version at a time, matching the one resolved in `esv`.
        first = versions[0]
        if isinstance(first, dict):
            first["id"] = target_version_id
        return payload

    # -- HTML-entity normalization -------------------------------------
    #
    # The Connect GET serializer HTML-escapes JSON-in-string content: a pricing
    # procedure export stores customElement.parameters[].value as escaped JSON
    # (e.g. "{&quot;whereConditions&quot;:[]}") and advancedCondition.criteria[].value
    # as escaped literals (e.g. "&#39;Evergreen&#39;"). JSON — unlike the XML
    # Metadata path, where the XML parser decodes &quot;→" before the engine sees
    # the value — carries no entity layer, so json.loads returns the literal
    # `&quot;`/`&#39;` characters and the engine's value sub-parser rejects them
    # on input ("Syntax error. Found '&'" on a flat formula; an opaque parse
    # failure on a nested blob). html.unescape() is the exact inverse of a single
    # escape pass and a no-op on entity-free strings, so a full recursive walk
    # over string leaves is safe and correct.

    @staticmethod
    def _unescape_value(value):
        """Recursively HTML-unescape every string leaf in a JSON-like value.

        Returns a new structure; does not mutate the input.
        """
        if isinstance(value, str):
            return html.unescape(value)
        if isinstance(value, list):
            return [ExpressionSetConnectBase._unescape_value(v) for v in value]
        if isinstance(value, dict):
            return {
                k: ExpressionSetConnectBase._unescape_value(v)
                for k, v in value.items()
            }
        return value  # int / float / bool / None pass through unchanged

    def _normalize_html_entities(self, payload: dict) -> dict:
        """HTML-unescape all string leaves before a Connect PATCH/POST.

        Off only when `normalize_html_entities: false` is passed (a probe
        escape hatch to reproduce the un-normalized gack on demand).
        """
        if not self._bool_option(self.options.get("normalize_html_entities"), True):
            self.logger.info(
                "normalize_html_entities=false — sending payload WITHOUT "
                "HTML-entity normalization (escaped GET output may gack)."
            )
            return payload
        return self._unescape_value(payload)

    # -- Schema pre-flight validation ----------------------------------
    #
    # Validate payloads BEFORE the Connect call. The PATCH/POST handler can
    # swallow real errors into opaque gacks, so a malformed step graph
    # otherwise surfaces as "Something went wrong" with no actionable detail.
    # Blocking by default; pass `skip_validation: true` to bypass (e.g. to probe
    # a payload the validator is too strict about).

    def _skip_validation(self) -> bool:
        return self._bool_option(self.options.get("skip_validation"), False)

    def _raise_on_validation_errors(self, result, what: str, *, log_summary: bool = True) -> None:
        handled = 0
        normalize = self._bool_option(self.options.get("normalize_html_entities"), True)
        for issue in result.warnings:
            automatic = what == "definition" and (
                issue.code in {"output_only_fields", "version_id"}
                or (issue.code == "html_entities" and normalize)
            )
            if automatic:
                handled += 1
            else:
                self.logger.warning(
                    "Schema %s: %s — %s", what, issue.location, issue.message
                )
        if handled and log_summary:
            self.logger.info(
                "Schema %s: %d transport warning(s) handled automatically by "
                "payload preparation (HTML decoding and/or server-field handling).",
                what, handled,
            )
        if result.errors:
            detail = "; ".join(f"{i.location}: {i.message}" for i in result.errors)
            raise TaskOptionsError(
                f"Schema validation failed for the {what} ({len(result.errors)} "
                f"error(s)): {detail}. Fix the payload, or pass "
                f"skip_validation:true to bypass."
            )

    def _preflight_validate_definition(self, definition: dict, *, log_summary: bool = True) -> None:
        if self._skip_validation():
            self.logger.info("skip_validation=true — skipping definition schema check.")
            return
        self._raise_on_validation_errors(
            validate_definition(definition), "definition", log_summary=log_summary
        )

    def _preflight_validate_overlay(self, overlay: dict) -> None:
        if self._skip_validation():
            self.logger.info("skip_validation=true — skipping overlay schema check.")
            return
        self._raise_on_validation_errors(validate_overlay(overlay), "overlay")

    def _preflight_validate_overlay_against_definition(
        self, overlay: dict, definition: dict, version_api_name: Optional[str]
    ) -> None:
        """Cross-check overlay targets against the live definition BEFORE any
        deactivation, so a typo'd placement/update/reorder/remove target fails
        locally instead of after the version has been toggled off (which would
        leave a live procedure deactivated)."""
        if self._skip_validation():
            self.logger.info(
                "skip_validation=true — skipping overlay/definition cross-check."
            )
            return
        self._raise_on_validation_errors(
            validate_overlay_against_definition(
                overlay, definition, version_api_name
            ),
            "overlay against the live definition",
        )

    # -- Utility -------------------------------------------------------

    _bool_option = staticmethod(_parse_bool_option)

    def _int_option(self, name: str, default: int, minimum: int = 0) -> int:
        """Read an int option, raising a clear TaskOptionsError on a non-numeric
        value rather than letting int() throw an opaque ValueError mid-run."""
        value = self.options.get(name)
        if value is None:
            return max(minimum, default)
        try:
            return max(minimum, int(value))
        except (TypeError, ValueError):
            raise TaskOptionsError(
                f"Option '{name}' must be an integer (got {value!r})."
            )


# ======================================================================
# ExportExpressionSet
# ======================================================================


class ExportExpressionSet(ExpressionSetConnectBase):
    """Export an expression set definition from the org to a JSON file."""

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "expression_set_api_name": {
            "description": "DeveloperName of the expression set to export.",
            "required": True,
        },
        "output_file": {
            "description": "Path to write the exported JSON.",
            "required": True,
        },
    }

    def _run_task(self):
        api_name = self.options["expression_set_api_name"]
        output_path = Path(self.options["output_file"])

        es_id = self._get_expression_set_id(api_name)
        self.logger.info("Exporting expression set %s (Id: %s)...", api_name, es_id)

        definition = self._get_expression_set_via_connect(es_id)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(definition, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self.logger.info("Exported to %s", output_path)


# ======================================================================
# ApplyExpressionSetOverlay
# ======================================================================


class ApplyExpressionSetOverlay(ExpressionSetConnectBase):
    """Apply a declarative overlay to an expression set via BRE Connect API.

    Supports: addSteps, removeSteps, updateSteps, reorderSteps,
              addVariables, removeVariables.
    """

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "overlay_file": {
            "description": "Path to the overlay JSON file.",
            "required": True,
        },
        "expression_set_api_name": {
            "description": (
                "Override expression set API name (default: from overlay file)."
            ),
            "required": False,
        },
        "version_api_name": {
            "description": (
                "Version API name to edit (default: the overlay's versionApiName, "
                "else the executing version)."
            ),
            "required": False,
        },
        "dry_run": {
            "description": "Log changes without modifying the org.",
            "required": False,
        },
        "verify": {
            "description": "GET definition after apply to verify changes.",
            "required": False,
        },
        "skip_validation": {
            "description": (
                "Skip the schema pre-flight on the overlay and merged definition "
                "(default: false — validation blocks on errors)."
            ),
            "required": False,
        },
        "normalize_html_entities": {
            "description": (
                "HTML-unescape (&quot;->\", &#39;->', etc.) all string leaves in "
                "the payload before the Connect call (default: true). Required to "
                "round-trip real GET output, whose serializer escapes "
                "JSON-in-string param/criteria/formula values. Set false only to "
                "reproduce the escape gack."
            ),
            "required": False,
        },
        "preserve_labels": {
            "description": (
                "Restore readable step labels after the Connect PATCH, which "
                "resets them to the spaceless step names (default: true)."
            ),
            "required": False,
        },
        "activate_after_apply": {
            "description": "Reactivate version after overlay (default: true).",
            "required": False,
        },
        "cascade_deactivate_procedure_plan": {
            "description": (
                "Deactivate referencing procedure plan versions if needed (default: true)."
            ),
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        overlay = self._load_overlay()
        # Validate the overlay shape up front — before any deactivation — so a
        # malformed overlay never leaves a version toggled off.
        self._preflight_validate_overlay(overlay)
        es_api_name = (
            self.options.get("expression_set_api_name")
            or overlay.get("expressionSetApiName")
        )
        if not es_api_name:
            raise TaskOptionsError(
                "expression_set_api_name required in options or overlay file."
            )

        dry_run = self._bool_option(self.options.get("dry_run"), False)
        verify = self._bool_option(self.options.get("verify"), True)
        activate_after = self._bool_option(
            self.options.get("activate_after_apply"), True
        )
        cascade = self._bool_option(
            self.options.get("cascade_deactivate_procedure_plan"), True
        )

        es_id = self._get_expression_set_id(es_api_name)
        es_def_id = self._get_expression_set_definition_id(es_api_name)
        esv = self._resolve_version_by_es_id(es_id)

        # With no version named, edit the version the lifecycle cycles: the
        # executing one. The GET lists versions lowest first, so its first entry
        # can be a draft (measured on 264, 2026-11-25: an overlay with no version
        # edited the draft v1 while reporting the active v2).
        self._executing_api_name = esv.get("ApiName")
        version_api_name = self._overlay_version_api_name(overlay)
        if version_api_name != esv.get("ApiName"):
            self.logger.warning(
                "The overlay edits %s, but %s is the executing version (highest Rank "
                "among active versions in their date window; earliest created among "
                "null Ranks), so pricing does not run the edited version.",
                version_api_name, esv.get("ApiName"),
            )

        # Fetch the live definition up front (before any deactivation) for the
        # read-only pre-flights: the overlay/definition cross-check — which
        # rejects a typo'd placement/update/reorder/remove target locally so a
        # bad overlay never leaves a live version toggled off — and the
        # version-name consistency warning. The actual overlay is applied to a
        # fresh post-deactivation GET inside the mutate body below so the PATCH
        # payload reflects the deactivated state.
        all_versions = self._list_versions(es_id)
        # The GET's block is matched by VersionNumber: its apiName can be a stale
        # clone name (see _find_version).
        self._overlay_version_number = next(
            (v.get("VersionNumber") for v in all_versions
             if v.get("ApiName") == version_api_name), None)
        preflight_definition = self._get_expression_set_via_connect(es_id)
        # Cross-check against exactly the block the run edits (found by number), so
        # a stale GET name that repeats another version's cannot pick the wrong one.
        self._preflight_validate_overlay_against_definition(
            overlay,
            dict(preflight_definition, versions=[self._find_version(
                preflight_definition.get("versions") or [], version_api_name)]),
            None,
        )
        self._check_version_name_consistency(es_id, esv, preflight_definition)
        label_esv = self._resolve_label_version(esv, version_api_name, all_versions)

        # Simulate the merge on the preflight snapshot and validate the merged
        # graph BEFORE deactivation. The cross-check only catches typo'd
        # targets; structural local failures (e.g. removing a ListGroup parent
        # but not its children, leaving a dangling parentStep) can still raise
        # only inside the post-deactivation mutate(). Catching them here means
        # a purely local validation failure never leaves the version or its
        # cascaded procedure plans deactivated. The inner mutate() keeps its
        # own validation as a last guard against drift between this preflight
        # snapshot and the post-deactivation GET.
        simulated = self._apply_overlay(preflight_definition, overlay)
        self._preflight_validate_definition(simulated, log_summary=False)

        # Before any write: a null-Rank active version could not be reactivated,
        # the PATCH must not rewrite another active version, and a PATCH whose
        # versions' names are not unique is rejected.
        refusal = (null_rank_reactivation_refusal(esv, activate_after,
                                                  NO_ACTIVATION_CCI_APPLY,
                                                  target_org=self._org_username(),
                                                  es_api_name=es_api_name)
                   or other_active_versions_refusal(es_api_name, all_versions, esv,
                                                    target_org=self._org_username())
                   or version_name_collision_refusal(es_api_name, all_versions, simulated))
        if refusal:
            raise TaskOptionsError(refusal)
        # Align ResourceInitializationType to the value the PATCH body will
        # carry (GET fabricates "Off" over a stored null), before touching
        # activation state.
        self._ensure_resource_initialization_type(
            es_id, dry_run, preflight_definition.get("resourceInitializationType")
        )

        def mutate():
            definition = self._get_expression_set_via_connect(es_id)
            modified = self._apply_overlay(definition, overlay)
            change_summary = self._overlay_change_summary(
                self._find_version(definition["versions"], version_api_name),
                self._find_version(modified["versions"], version_api_name),
            )

            # Pre-flight: validate the merged definition before PATCH so a
            # malformed step graph fails locally with a clear message rather
            # than as an opaque server gack.
            self._preflight_validate_definition(modified)

            # Send the WHOLE definition (sanitized), not a reconstructed thin
            # object, so identity/structural fields (interfaceSourceType,
            # resourceInitializationType, contextDefinitions) and the
            # version-level `id` PATCH requires are preserved. The Connect PATCH
            # is a full-graph replace. Normalize HTML entities LAST (after
            # validation, which must see the escaped form to warn) so the bytes
            # on the wire are valid JSON inside the param/criteria value strings.
            patch_payload = self._strip_readonly_fields(modified)
            patch_payload = self._normalize_html_entities(patch_payload)
            patch_payload = self._keep_patched_version_inactive(patch_payload, esv["Id"])

            if dry_run:
                self.logger.info("[dry-run] Would PATCH expression set %s.", es_id)
            else:
                self._patch_expression_set_via_connect(es_id, patch_payload)
                self.logger.info("PATCHed expression set %s.", es_id)

            if verify and not dry_run:
                self._verify_overlay(es_id, overlay, patch_payload)
            self.logger.info("Overlay changes: %s", change_summary)

        self._run_connect_mutation(
            es_def_id=es_def_id,
            esv=esv,
            mutate=mutate,
            dry_run=dry_run,
            activate_after=activate_after,
            cascade=cascade,
            verb="Overlay apply",
            extra_labels=self._overlay_labels(overlay) if label_esv else None,
            label_esv=label_esv,
            label_versions=all_versions,
        )

        self.logger.info(
            "Successfully applied overlay %s to %s.",
            self.options["overlay_file"], es_api_name,
        )

    # -- Overlay loading -----------------------------------------------

    def _load_overlay(self) -> dict:
        path = Path(self.options["overlay_file"])
        if not path.exists():
            raise TaskOptionsError(f"Overlay file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _overlay_version_api_name(self, overlay: dict) -> Optional[str]:
        """The version the overlay edits: the option, the overlay's versionApiName,
        else the executing version ``_run_task`` resolved."""
        return (
            self.options.get("version_api_name")
            or overlay.get("versionApiName")
            or getattr(self, "_executing_api_name", None)
        )

    # -- Overlay transformation (pure function) ------------------------

    def _apply_overlay(self, definition: dict, overlay: dict) -> dict:
        """Apply overlay transformations to the definition. Returns modified copy."""
        result = deepcopy(definition)
        versions = result.get("versions", [])
        if not versions:
            raise TaskOptionsError("Expression set has no versions to modify.")

        version = self._find_version(versions, self._overlay_version_api_name(overlay))
        steps = version.get("steps", [])
        variables = version.get("variables", [])

        if overlay.get("removeSteps"):
            steps = self._remove_steps(steps, overlay["removeSteps"])
        if overlay.get("addSteps"):
            steps = self._add_steps(steps, overlay["addSteps"])
        if overlay.get("updateSteps"):
            steps = self._update_steps(steps, overlay["updateSteps"])
        if overlay.get("reorderSteps"):
            steps = self._reorder_steps(steps, overlay["reorderSteps"])

        if overlay.get("removeVariables"):
            variables = self._remove_variables(variables, overlay["removeVariables"])
        if overlay.get("addVariables"):
            variables = self._add_variables(variables, overlay["addVariables"])

        version["steps"] = steps
        version["variables"] = variables
        return result

    def _find_version(self, versions: list, version_api_name: Optional[str]) -> dict:
        """The target version block: by the VersionNumber ``_run_task`` resolved (the
        GET's apiName can be a stale clone name), then ``apiName``; a one-version
        definition gives its only version. Never the first of several."""
        version = select_version(versions, version_api_name,
                                 getattr(self, "_overlay_version_number", None))
        if version is None:
            raise TaskOptionsError(
                f"Version '{version_api_name}' not found in definition."
                if version_api_name else
                f"Definition has {len(versions)} versions; name the target version."
            )
        return version

    @staticmethod
    def _overlay_change_summary(before: dict, after: dict) -> str:
        """Count actual graph changes, including steps shifted by placement."""
        parts = []
        for key in ("steps", "variables"):
            old = {item["name"]: item for item in before.get(key, [])}
            new = {item["name"]: item for item in after.get(key, [])}
            added = len(new.keys() - old.keys())
            removed = len(old.keys() - new.keys())
            changed = sum(old[name] != new[name] for name in old.keys() & new.keys())
            parts.append(f"{key} +{added}/-{removed}/changed {changed}")
        return "; ".join(parts)

    # -- Step operations -----------------------------------------------

    def _remove_steps(self, steps: list, to_remove: list) -> list:
        names_to_remove = {s["name"] for s in to_remove}
        present = {s.get("name") for s in steps}
        steps = [s for s in steps if s.get("name") not in names_to_remove]
        # Log per name against that name's actual presence — not a batch-wide
        # count, which would mislabel every name once any one was removed.
        for name in names_to_remove:
            if name in present:
                self.logger.debug("Removed step '%s'.", name)
            else:
                self.logger.warning("Step '%s' not found for removal.", name)
        steps = self._renumber_top_level_steps(steps)
        return steps

    def _add_steps(self, steps: list, to_add: list) -> list:
        for step_def in to_add:
            existing = next(
                (s for s in steps if s.get("name") == step_def["name"]), None
            )
            if existing:
                differences = existing_step_differences(step_def, existing)
                if differences:
                    raise TaskOptionsError(
                        f"addSteps target '{step_def['name']}' already exists with different "
                        f"content ({', '.join(differences)}); use updateSteps to change it."
                    )
                self.logger.debug(
                    "Step '%s' already matches the requested content.", step_def["name"]
                )
                continue

            # Read placement WITHOUT mutating the caller's overlay dict: the
            # verification pass (_verify_step_placement) reads placement back off
            # the same overlay, so popping it here would silently disable the
            # placement check. _build_step copies only the fields it needs.
            placement = step_def.get("placement")
            new_step = self._build_step(step_def)

            # Child steps (parentStep set) are ordered by their own
            # sequenceNumber scoped WITHIN the parent (children restart at 1).
            # They take no top-level placement and must not trigger the
            # top-level renumber/bump logic below, which would overwrite their
            # per-parent sequenceNumber with max_top_level + 1 (colliding
            # siblings onto the same slot). _build_step already copied the
            # provided sequenceNumber, so just append.
            if step_def.get("parentStep"):
                steps.append(new_step)
                self.logger.debug(
                    "Added child step '%s' (parent '%s') at sequence %s.",
                    new_step["name"], step_def["parentStep"],
                    new_step["sequenceNumber"],
                )
                continue

            if placement and placement.get("afterStep"):
                target_name = placement["afterStep"]
                target_seq = self._find_step_sequence(steps, target_name)
                new_step["sequenceNumber"] = target_seq + 1
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) > target_seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            elif placement and placement.get("beforeStep"):
                target_name = placement["beforeStep"]
                target_seq = self._find_step_sequence(steps, target_name)
                new_step["sequenceNumber"] = target_seq
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) >= target_seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            elif placement and placement.get("sequenceNumber") is not None:
                seq = placement["sequenceNumber"]
                new_step["sequenceNumber"] = seq
                for s in steps:
                    if (
                        s.get("parentStep") is None
                        and s.get("sequenceNumber", 0) >= seq
                    ):
                        s["sequenceNumber"] = s["sequenceNumber"] + 1
            else:
                max_seq = max(
                    (
                        s.get("sequenceNumber", 0)
                        for s in steps
                        if s.get("parentStep") is None
                    ),
                    default=0,
                )
                new_step["sequenceNumber"] = max_seq + 1

            steps.append(new_step)
            self.logger.debug(
                "Added step '%s' at sequence %s.",
                new_step["name"], new_step["sequenceNumber"],
            )
        return steps

    def _update_steps(self, steps: list, to_update: list) -> list:
        for update_def in to_update:
            name = update_def["name"]
            if "placement" in update_def:
                raise TaskOptionsError(
                    f"updateSteps target '{name}' cannot use placement; use reorderSteps."
                )
            target = next((s for s in steps if s.get("name") == name), None)
            if not target:
                # Raise rather than warn-and-continue: a missing target means the
                # edit silently does nothing, yet the PATCH still succeeds and is
                # reported as success. Fail loudly so a typo'd name is caught.
                raise TaskOptionsError(
                    f"updateSteps target '{name}' not found in the definition."
                )
            for key, value in update_def.items():
                if key in ("name", "label"):
                    continue
                target[key] = value
            self.logger.debug("Updated step '%s'.", name)
        return steps

    def _reorder_steps(self, steps: list, reorder_defs: list) -> list:
        for reorder in reorder_defs:
            name = reorder["name"]
            target = next((s for s in steps if s.get("name") == name), None)
            if not target:
                raise TaskOptionsError(
                    f"reorderSteps target '{name}' not found in the definition."
                )
            target["sequenceNumber"] = reorder["sequenceNumber"]
            self.logger.debug(
                "Reordered step '%s' to sequence %s.",
                name, reorder["sequenceNumber"],
            )
        return steps

    # Overlay-only metadata that must NOT be forwarded to the Connect payload.
    # `placement` directs _add_steps to compute sequenceNumber and never goes
    # to the API. Add new overlay-local keys here as the schema evolves.
    _OVERLAY_ONLY_STEP_KEYS = frozenset({"placement", "label"})

    def _build_step(self, step_def: dict) -> dict:
        # Pass through every field the overlay author wrote (minus overlay-only
        # metadata), so a future step field — e.g. populated
        # passedMessageTokenMappings — survives apply. The validator already
        # gates step shape (stepType enum, required keys, customElement
        # parameter shape) before we get here, so any unknown field is the
        # author's responsibility. Sensible defaults still fill in the small
        # set of required-by-engine flags when an overlay omits them.
        defaults = {
            "description": "",
            "sequenceNumber": 1,
            "stepType": "BusinessKnowledgeModel",
            "resultIncluded": False,
            "shouldExposeExecPathMsgOnly": True,
            "shouldExposeConditionDetails": False,
            "shouldShowExplExternally": False,
        }
        step = {k: v for k, v in step_def.items()
                if k not in self._OVERLAY_ONLY_STEP_KEYS}
        if "name" not in step:
            # _validate_step requires name; defensive — never reached after
            # validation.
            raise TaskOptionsError("addSteps entry is missing 'name'.")
        for key, value in defaults.items():
            step.setdefault(key, value)
        return step

    def _find_step_sequence(self, steps: list, name: str) -> int:
        for s in steps:
            if s.get("name") == name and s.get("parentStep") is None:
                return s.get("sequenceNumber", 0)
        raise TaskOptionsError(
            f"Placement target step '{name}' not found in definition."
        )

    def _renumber_top_level_steps(self, steps: list) -> list:
        top_level = [s for s in steps if s.get("parentStep") is None]
        top_level.sort(key=lambda s: s.get("sequenceNumber", 0))
        for i, s in enumerate(top_level, start=1):
            s["sequenceNumber"] = i
        return steps

    # -- Variable operations -------------------------------------------

    def _add_variables(self, variables: list, to_add: list) -> list:
        existing_names = {v.get("name") for v in variables}
        for var_def in to_add:
            name = var_def["name"]
            if name in existing_names:
                # Covers both names already on the live definition AND names
                # we've just appended from an earlier addVariables entry — so
                # an overlay with two entries for the same name skips the
                # second instead of appending a duplicate the Connect API
                # would then reject after the version was already deactivated.
                self.logger.debug(
                    "Variable '%s' already exists, skipping.", name
                )
                continue
            variables.append(var_def)
            existing_names.add(name)
            self.logger.debug("Added variable '%s'.", name)
        return variables

    def _remove_variables(self, variables: list, to_remove: list) -> list:
        # Accept either bare strings or {"name": "..."} entries — variables
        # have no other field to address, so a list of names is the natural
        # shape. removeSteps requires objects (it could grow extra keys).
        names = set()
        for entry in to_remove:
            if isinstance(entry, str):
                names.add(entry)
            elif isinstance(entry, dict) and entry.get("name"):
                names.add(entry["name"])
        original_count = len(variables)
        variables = [v for v in variables if v.get("name") not in names]
        removed = original_count - len(variables)
        if removed:
            self.logger.debug("Removed %d variable(s).", removed)
        return variables

    # -- Verification --------------------------------------------------

    def _verify_overlay(self, es_id: str, overlay: dict, expected: dict):
        post_state = self._get_expression_set_via_connect(es_id)
        versions = post_state.get("versions", [])
        if not versions:
            raise TaskOptionsError("Verification failed: no versions found.")

        version_api_name = self._overlay_version_api_name(overlay)
        version = self._find_version(versions, version_api_name)
        expected_version = self._find_version(expected.get("versions", []), version_api_name)
        errors = overlay_step_content_errors(overlay, expected_version, version)
        if errors:
            raise TaskOptionsError("Verification failed: " + "; ".join(errors))
        # Preserve the CCI task's existing placement contract in addition to
        # checking the stored graph. Placement is overlay metadata, not a field
        # in the PATCH payload, and cannot be verified by body comparison alone.
        seq_by_name = {s.get("name"): s.get("sequenceNumber")
                       for s in version.get("steps", []) if s.get("parentStep") is None}
        for added in overlay.get("addSteps", []):
            self._verify_step_placement(added, seq_by_name)
        self.logger.info("Verified overlay step content and removals against the merged payload.")

    @staticmethod
    def _verify_step_placement(added: dict, seq_by_name: dict):
        """Assert an added top-level step landed in the right sequence slot.

        Validates against sequenceNumber (the engine's execution order), not
        the GET response array order (which is alphabetical by name).
        """
        placement = added.get("placement") or {}
        name = added["name"]
        added_seq = seq_by_name.get(name)
        if added_seq is None:
            # Child step (has a parentStep) or no sequence to check.
            return

        if placement.get("afterStep"):
            target = placement["afterStep"]
            target_seq = seq_by_name.get(target)
            if target_seq is not None and added_seq != target_seq + 1:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {target_seq + 1} (immediately after "
                    f"'{target}' at {target_seq})."
                )
        elif placement.get("beforeStep"):
            target = placement["beforeStep"]
            target_seq = seq_by_name.get(target)
            if target_seq is not None and added_seq != target_seq - 1:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {target_seq - 1} (immediately before "
                    f"'{target}' at {target_seq})."
                )
        elif placement.get("sequenceNumber") is not None:
            want = placement["sequenceNumber"]
            if added_seq != want:
                raise TaskOptionsError(
                    f"Verification failed: step '{name}' has sequenceNumber "
                    f"{added_seq}, expected {want}."
                )


# ======================================================================
# ImportExpressionSet
# ======================================================================


class ImportExpressionSet(ExpressionSetConnectBase):
    """Import (create or replace) an expression set from a JSON file."""

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "input_file": {
            "description": "Path to the full expression set definition JSON.",
            "required": True,
        },
        "dry_run": {
            "description": "Log changes without modifying the org.",
            "required": False,
        },
        "skip_validation": {
            "description": (
                "Skip the schema pre-flight on the input definition "
                "(default: false — validation blocks on errors)."
            ),
            "required": False,
        },
        "normalize_html_entities": {
            "description": (
                "HTML-unescape (&quot;->\", &#39;->', etc.) all string leaves in "
                "the payload before the Connect call (default: true). Required to "
                "round-trip real GET output, whose serializer escapes "
                "JSON-in-string param/criteria/formula values. Set false only to "
                "reproduce the escape gack."
            ),
            "required": False,
        },
        "preserve_labels": {
            "description": (
                "Restore readable step labels after the Connect PATCH, which "
                "resets them to the spaceless step names (default: true)."
            ),
            "required": False,
        },
        "activate_after_import": {
            "description": "Activate version after import (default: true).",
            "required": False,
        },
        "cascade_deactivate_procedure_plan": {
            "description": (
                "Deactivate referencing procedure plan versions if needed (default: true)."
            ),
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        input_path = Path(self.options["input_file"])
        if not input_path.exists():
            raise TaskOptionsError(f"Input file not found: {input_path}")

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        api_name = payload.get("apiName")
        if not api_name:
            raise TaskOptionsError("Input JSON must contain 'apiName' field.")

        # Pre-flight: validate the full definition before any create/replace.
        self._preflight_validate_definition(payload)

        dry_run = self._bool_option(self.options.get("dry_run"), False)
        activate_after = self._bool_option(
            self.options.get("activate_after_import"), True
        )
        cascade = self._bool_option(
            self.options.get("cascade_deactivate_procedure_plan"), True
        )

        # Check if expression set already exists
        safe = self._soql_escape(api_name)
        existing = self._soql_query(
            f"SELECT Id FROM ExpressionSetDefinition WHERE DeveloperName = '{safe}'"
        )

        if existing:
            es_def_id = existing[0]["Id"]
            es_id = self._get_expression_set_id(api_name)
            self.logger.info("Expression set '%s' exists, updating...", api_name)
            versions = self._list_versions(es_id)
            esv = self._resolve_version_by_es_id(es_id)
            # On a multi-version set, refuse a PATCH that would rebind the
            # payload's version onto another one, before ANY write (the
            # ResourceInitializationType alignment below is a write too).
            refusal = (import_target_refusal(api_name, versions, esv, payload)
                       or null_rank_reactivation_refusal(esv, activate_after,
                                                         NO_ACTIVATION_CCI_IMPORT,
                                                         target_org=self._org_username(),
                                                         es_api_name=api_name))
            if refusal:
                raise TaskOptionsError(refusal)

            # Align ResourceInitializationType to the value the PATCH body will
            # carry, before touching activation state.
            self._ensure_resource_initialization_type(
                es_id, dry_run, payload.get("resourceInitializationType")
            )

            def mutate():
                if dry_run:
                    self.logger.info("[dry-run] Would PATCH expression set %s.", es_id)
                    return
                # Rewrite versions[0].id to the TARGET org's version id.
                # _strip_readonly_fields keeps versions[].id (PATCH needs it to
                # match in place), but in an export-from-source/import-into-
                # target workflow the payload carries the SOURCE org's id (a
                # 9QM...). The endpoint expects the target version id resolved
                # in `esv` above; without this rewrite the server rejects or
                # mis-binds the version. Same-org re-import is a no-op.
                patch_payload = self._strip_readonly_fields(payload)
                patch_payload = self._rewrite_version_id(patch_payload, esv["Id"])
                patch_payload = self._normalize_html_entities(patch_payload)
                patch_payload = self._keep_patched_version_inactive(patch_payload, esv["Id"])
                self._patch_expression_set_via_connect(es_id, patch_payload)
                self.logger.info("Imported (updated) expression set %s.", es_id)

            self._run_connect_mutation(
                es_def_id=es_def_id,
                esv=esv,
                mutate=mutate,
                dry_run=dry_run,
                activate_after=activate_after,
                cascade=cascade,
                verb="Import",
                # The PATCH relabels every version of the set, not just esv.
                label_versions=versions,
            )
        else:
            self.logger.info("Expression set '%s' does not exist, creating...", api_name)
            if dry_run:
                self.logger.info("[dry-run] Would POST new expression set.")
            else:
                # A POST-create must OMIT the version-level `id` (for_create):
                # a source-org id from a GET export makes the server reject or
                # mis-bind the new version.
                create_payload = self._strip_readonly_fields(payload, for_create=True)
                create_payload = self._normalize_html_entities(create_payload)
                result = self._post_expression_set_via_connect(create_payload)
                es_id = result.get("id")
                if not es_id:
                    raise TaskOptionsError(
                        "Connect POST returned no expression set id; the create "
                        f"may not have committed. Response: {result!r}"
                    )
                self.logger.info("Created expression set %s (Id: %s).", api_name, es_id)

                # The created version's active state comes from the payload's
                # `enabled` flag. Honor activate_after_import explicitly so the
                # option is meaningful on create, not just on replace.
                esv = self._resolve_version_by_es_id(es_id)
                if activate_after and not bool(esv.get("IsActive")):
                    self._set_version_active(esv["Id"], True, dry_run)
                    self._wait_for_version_state(esv["Id"], True)
                elif not activate_after and bool(esv.get("IsActive")):
                    self.logger.info(
                        "activate_after_import=false; leaving created "
                        "ExpressionSetVersion %s deactivated.", esv["Id"]
                    )
                    self._set_version_active(esv["Id"], False, dry_run)
                    self._wait_for_version_state(esv["Id"], False)

        self.logger.info("Import complete for '%s'.", api_name)


# ======================================================================
# DeleteExpressionSet
# ======================================================================


class DeleteExpressionSet(ExpressionSetConnectBase):
    """Delete an expression set, or just a single (old) version.

    Two modes:
      * Whole expression set (default): DELETE the Connect resource. Any
        enabled version must be deactivated first.
      * Single version (``version_api_name``): delete just that
        ExpressionSetVersion via the sObject API — used by the
        post-new-version → delete-old-version workflow, leaving the
        expression set and its other versions intact.

    Destructive: requires ``confirm: true`` (or ``dry_run: true``).
    """

    task_options = {
        **ExpressionSetConnectBase.task_options,
        "expression_set_api_name": {
            "description": "DeveloperName of the expression set to delete from.",
            "required": True,
        },
        "version_api_name": {
            "description": (
                "If set, delete only this ExpressionSetVersion (by ApiName) "
                "rather than the whole expression set."
            ),
            "required": False,
        },
        "confirm": {
            "description": "Must be true to actually delete (guard).",
            "required": False,
        },
        "dry_run": {
            "description": "Log what would be deleted without deleting.",
            "required": False,
        },
        "max_wait_seconds": {
            "description": "Max seconds to poll for activation state changes.",
            "required": False,
        },
        "poll_interval_seconds": {
            "description": "Seconds between activation state polls.",
            "required": False,
        },
    }

    def _run_task(self):
        api_name = self.options["expression_set_api_name"]
        version_api_name = self.options.get("version_api_name")
        dry_run = self._bool_option(self.options.get("dry_run"), False)
        confirm = self._bool_option(self.options.get("confirm"), False)

        if not confirm and not dry_run:
            raise TaskOptionsError(
                "Refusing to delete without confirmation. Pass -o confirm true "
                "(or -o dry_run true to preview)."
            )

        es_id = self._get_expression_set_id(api_name)

        if version_api_name:
            self._delete_single_version(version_api_name, es_id, api_name, dry_run)
            return

        # Whole expression set: an active ProcedurePlanDefinitionVersion
        # referencing this ES can lock the ES version (mirrors the apply/import
        # lifecycle). Cascade-deactivate referencing procedure plan versions
        # first, then deactivate the ES version, then DELETE.
        #
        # If anything between cascade and DELETE fails, restore the cluster to
        # the exact pre-attempt state — both the ES version AND the cascaded
        # procedure plans. Unlike apply/import (where a failed PATCH may have
        # corrupted the definition mid-write), a failed DELETE leaves the
        # record byte-identical, so re-enabling is safe. Restoring only the
        # plans would leave them referencing a deactivated ES — worse than the
        # state the user saw before the delete attempt.
        # The cascade, deactivation, DELETE and rollback (ES version first, then
        # the plans only if that succeeded) are the shared engine's
        # (LifecycleCore.delete_expression_set).
        es_def_id = self._get_expression_set_definition_id(api_name)
        esv = self._resolve_version_by_es_id(es_id)
        # A failed DELETE is rolled back by reactivating the version, which the API
        # refuses for a version with no Rank: refuse before any write.
        refusal = null_rank_delete_refusal(esv, target_org=self._org_username(),
                                           es_api_name=api_name)
        if refusal:
            raise TaskOptionsError(refusal)
        self._lifecycle(dry_run).delete_expression_set(
            es_id=es_id, es_def_id=es_def_id, esv=esv, api_name=api_name,
        )

    def _delete_single_version(
        self, version_api_name: str, es_id: str, api_name: str, dry_run: bool,
    ):
        """Delete one version (deactivating it first); the shared engine's
        LifecycleCore.delete_single_version."""
        self._lifecycle(dry_run).delete_single_version(version_api_name, es_id, api_name)


# ======================================================================
# ValidateExpressionSet (org-less)
# ======================================================================


class ValidateExpressionSet(BaseTask):
    """Validate an expression set definition or overlay JSON against the schema.

    Org-less: runs the same pre-flight validator the apply/import tasks use
    (tasks/expression_set_schema.py). Auto-detects overlay vs definition shape
    unless ``kind`` is given. Fails the task on schema errors (and on warnings
    when ``strict`` is true).
    """

    task_options = {
        "file": {
            "description": "Path to the definition or overlay JSON to validate.",
            "required": True,
        },
        "kind": {
            "description": "Force 'overlay' or 'definition' (default: auto-detect).",
            "required": False,
        },
        "strict": {
            "description": "Treat warnings as failures (default: false).",
            "required": False,
        },
    }

    _bool_option = staticmethod(_parse_bool_option)

    def _run_task(self):
        path = Path(self.options["file"])
        if not path.exists():
            raise TaskOptionsError(f"File not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        kind = self.options.get("kind") or detect_kind(data)

        result = validate_definition(data) if kind == "definition" else validate_overlay(data)

        for issue in result.warnings:
            self.logger.warning("%s: %s", issue.location, issue.message)
        for issue in result.errors:
            self.logger.error("%s: %s", issue.location, issue.message)

        strict = self._bool_option(self.options.get("strict"), False)
        if result.errors or (strict and result.warnings):
            raise TaskOptionsError(
                f"Schema validation failed for {path} as {kind}: "
                f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
            )
        self.logger.info(
            "Schema validation passed for %s as %s (%d warning(s)).",
            path, kind, len(result.warnings),
        )
