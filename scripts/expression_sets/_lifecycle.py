#!/usr/bin/env python3
"""Safety-critical activation lifecycle for BRE Expression Set mutations.

Part of the self-contained ``scripts/expression_sets/`` toolkit (imports nothing
from ``tasks/``). :class:`LifecycleEngine` wraps a :class:`_client.Transport` and
encapsulates the deactivate → mutate → reactivate sequencer, the
``ProcedurePlanDefinitionVersion`` cascade, the version-state
(``ExpressionSetVersion.IsActive``) transitions, the
``ExpressionSet.ResourceInitializationType`` alignment, and the Connect
GET/PATCH/POST/DELETE on the expression-set resource. It mirrors the
live-verified rules of the CCI task ``tasks/rlm_expression_set_connect.py``
(reference-only) so the CLIs give the same guarantees, without sharing code.

The load-bearing guarantees (verified on 262 / v67.0):

  * A Connect mutation requires the version **inactive**. An active version (and
    any referencing procedure-plan versions, when ``cascade``) is deactivated
    first, then reactivated on success.
  * Reactivation is governed by the explicit ``activate_after`` flag, NOT the
    prior active state — an explicit false wins (leaves it off for inspection).
  * **PATCH is not atomic.** A failed PATCH can leave a half-mutated, deactivated
    version. It is NEVER reactivated — re-enabling a corrupted pricing procedure
    is worse than leaving it offline. Reactivation happens only when
    ``activate_after`` AND the mutate body succeeded (or in dry-run, where
    nothing changed).

Dry-run is driven by the injected ``Transport`` (``Transport(dry_run=True)``):
mutating verbs are logged and skipped at the request layer; reads always run so
a dry-run still resolves ids and logs the real mutation sequence. The engine
only additionally skips the activation-state *polls* under dry-run (there is no
state change to wait for).

Errors raise :class:`LifecycleError`. The engine takes the transport as its one
dependency, so a unit test can pass a fake transport and assert the call
sequence without an org.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from ._client import CONNECT_BASE, ExpressionSetClientError, soql_literal


class LifecycleError(RuntimeError):
    """Raised on an activation-lifecycle failure in the Expression Set toolkit."""


# Enum of the two ResourceInitializationType values the PATCH body may carry.
_RESOURCE_INIT_TYPES = {"Default", "Off"}


class LifecycleEngine:
    """Deactivate → mutate → reactivate engine over a :class:`_client.Transport`.

    ``transport`` is the only dependency: all Connect calls, SObject PATCHes, and
    SOQL reads route through it, so its ``dry_run``/``logger`` govern the whole
    engine and a test can inject a fake.
    """

    def __init__(
        self,
        transport,
        *,
        logger: Callable[..., None] = None,
        max_wait_seconds: int = 45,
        poll_interval_seconds: int = 3,
    ):
        self.t = transport
        self.log = logger or transport.logger
        self.dry_run = transport.dry_run
        self.max_wait = max(0, max_wait_seconds)
        self.poll = max(1, poll_interval_seconds)

    # -- Connect resource ops ------------------------------------------

    def get_definition(self, es_id: str) -> dict:
        """GET the full expression-set definition (reads always execute)."""
        resp = self.t.get(f"{CONNECT_BASE}/{es_id}")
        if isinstance(resp, list):
            resp = resp[0] if resp and isinstance(resp[0], dict) else {}
        return resp if isinstance(resp, dict) else {}

    def patch_definition(self, es_id: str, payload: dict) -> dict:
        """Connect PATCH (full-graph replace). Skipped+logged under dry-run."""
        return self.t.connect("PATCH", f"{CONNECT_BASE}/{es_id}", payload)

    def post_definition(self, payload: dict) -> dict:
        """Connect POST-create. Skipped+logged under dry-run."""
        return self.t.connect("POST", CONNECT_BASE, payload)

    def delete_definition_connect(self, es_id: str) -> Any:
        """Connect DELETE of the whole expression set. Skipped+logged under dry-run."""
        return self.t.connect("DELETE", f"{CONNECT_BASE}/{es_id}")

    # -- Version-state transitions -------------------------------------

    def _version_state(self, version_id: str) -> Optional[bool]:
        records = self.t.soql(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE Id = '{soql_literal(version_id)}'"
        )
        if not records:
            return None
        return bool(records[0].get("IsActive"))

    def set_version_active(self, version_id: str, active: bool) -> None:
        """Set ``ExpressionSetVersion.IsActive`` (idempotent).

        Skips the SObject PATCH when the version is already in the desired state:
        a Connect full-graph PATCH whose body carries ``enabled: true`` reactivates
        the version itself, so a later explicit reactivation would otherwise hit
        the "An enabled Expression Set Version cannot be updated/deleted." guard
        and fail a genuinely-successful mutation. Under dry-run the transport
        skips+logs the PATCH; the read below still runs.
        """
        current = self._version_state(version_id)
        if current is active:
            self.log(
                f"ExpressionSetVersion {version_id} already IsActive={active}; "
                "no change needed."
            )
            return
        self.t.sobject(
            "PATCH", "ExpressionSetVersion", version_id, {"IsActive": active}
        )
        self.log(f"Set ExpressionSetVersion {version_id} IsActive={active}.")

    def wait_for_version_state(self, version_id: str, active: bool) -> None:
        """Poll until the version reaches ``IsActive=active`` (no-op under dry-run)."""
        if self.dry_run:
            return
        waited = 0
        while waited <= self.max_wait:
            if self._version_state(version_id) is active:
                self.log(
                    f"Confirmed ExpressionSetVersion {version_id} "
                    f"IsActive={active} after {waited}s."
                )
                return
            time.sleep(self.poll)
            waited += self.poll
        raise LifecycleError(
            f"ExpressionSetVersion {version_id} did not reach IsActive={active} "
            f"within {self.max_wait}s."
        )

    # -- ResourceInitializationType alignment --------------------------

    def ensure_resource_initialization_type(
        self, es_id: str, desired: Optional[str] = None
    ) -> None:
        """Align stored ``ExpressionSet.ResourceInitializationType`` before PATCH.

        Connect GET reports "Off" while the SObject stores null on seeded
        procedures; PATCH validates the body against the stored value and rejects
        a mismatch. Writing the stored field to the value the PATCH body carries
        aligns the two. The field is immutable once set: if it already holds a
        value this only raises on a conflict (never rewrites it). Raising here
        happens BEFORE any deactivation, so a guaranteed-PATCH-failure never
        leaves a version deactivated.
        """
        target = desired or "Off"
        if target not in _RESOURCE_INIT_TYPES:
            self.log(
                f"Ignoring unrecognized resourceInitializationType '{target}'; "
                f"valid values are {sorted(_RESOURCE_INIT_TYPES)}."
            )
            target = "Off"
        records = self.t.soql(
            "SELECT Id, ResourceInitializationType FROM ExpressionSet "
            f"WHERE Id = '{soql_literal(es_id)}'"
        )
        if not records:
            return
        current = records[0].get("ResourceInitializationType")
        if current:
            if desired and desired != current:
                raise LifecycleError(
                    f"ExpressionSet {es_id} ResourceInitializationType is already "
                    f"'{current}' and is immutable; the payload's '{desired}' "
                    f"cannot be applied. Update the payload to match the stored "
                    f"value before retrying."
                )
            return
        self.log(
            f"ExpressionSet {es_id} has null ResourceInitializationType; setting "
            f"it to '{target}' so the Connect PATCH is accepted."
        )
        self.t.sobject(
            "PATCH", "ExpressionSet", es_id, {"ResourceInitializationType": target}
        )

    # -- Procedure-plan cascade ----------------------------------------

    def find_referencing_procedure_plans(self, es_def_id: str) -> List[dict]:
        return self.t.soql(
            "SELECT Id, ProcedurePlanSection.ProcedurePlanVersionId "
            "FROM ProcedurePlanOption "
            f"WHERE ExpressionSetDefinitionId = '{soql_literal(es_def_id)}'"
        )

    def cascade_deactivate_procedure_plans(self, es_def_id: str) -> List[str]:
        """Deactivate active procedure-plan versions referencing this ES.

        Returns the version ids that were (or, in dry-run, would be) deactivated.
        On a partial failure, rolls back only the versions this call already
        deactivated, then raises — the pre-mutation cascade must not leave a
        half-deactivated cluster behind.
        """
        options = self.find_referencing_procedure_plans(es_def_id)
        if not options:
            return []
        version_ids = set()
        for opt in options:
            section = opt.get("ProcedurePlanSection") or {}
            vid = section.get("ProcedurePlanVersionId")
            if vid:
                version_ids.add(vid)
        deactivated: List[str] = []
        try:
            for vid in sorted(version_ids):
                records = self.t.soql(
                    "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
                    f"WHERE Id = '{soql_literal(vid)}'"
                )
                if records and records[0].get("IsActive"):
                    self.t.sobject(
                        "PATCH", "ProcedurePlanDefinitionVersion", vid,
                        {"IsActive": False},
                    )
                    self.log(
                        f"Deactivated ProcedurePlanDefinitionVersion {vid} (cascade)."
                    )
                    deactivated.append(vid)
        except Exception as exc:
            if deactivated and not self.dry_run:
                try:
                    self.cascade_reactivate_procedure_plans(deactivated)
                except Exception as rollback_exc:
                    raise LifecycleError(
                        "Cascade deactivation failed after deactivating "
                        f"ProcedurePlanDefinitionVersion(s) {deactivated}, and "
                        f"rollback also failed: {rollback_exc}"
                    ) from exc
                raise LifecycleError(
                    "Cascade deactivation failed after deactivating "
                    f"ProcedurePlanDefinitionVersion(s) {deactivated}; rolled them "
                    "back before aborting."
                ) from exc
            raise
        return deactivated

    def cascade_reactivate_procedure_plans(self, version_ids: List[str]) -> None:
        for vid in version_ids:
            self.t.sobject(
                "PATCH", "ProcedurePlanDefinitionVersion", vid, {"IsActive": True}
            )
            self.log(f"Reactivated ProcedurePlanDefinitionVersion {vid}.")

    # -- The deactivate → mutate → reactivate sequencer ----------------

    def run_mutation(
        self,
        *,
        es_def_id: str,
        esv: dict,
        mutate: Callable[[], None],
        activate_after: bool,
        cascade: bool,
        verb: str = "mutation",
    ) -> None:
        """Run the safety-critical deactivate→mutate→reactivate lifecycle.

        ``mutate`` is the verb-specific body (it runs while the version is
        deactivated). Re-raises the original failure (chaining a reactivation
        failure onto it when both happen).
        """
        esv_id = esv["Id"]
        was_active = bool(esv.get("IsActive"))
        deactivated = False
        cascaded_ppvs: List[str] = []
        failure: Optional[Exception] = None
        mutate_succeeded = False

        try:
            if was_active:
                if cascade:
                    cascaded_ppvs = self.cascade_deactivate_procedure_plans(es_def_id)
                self.set_version_active(esv_id, False)
                self.wait_for_version_state(esv_id, False)
                deactivated = True
            else:
                self.log(f"ExpressionSetVersion {esv_id} already inactive.")

            mutate()
            mutate_succeeded = True
        except Exception as exc:
            failure = exc
        finally:
            should_activate = activate_after and (mutate_succeeded or self.dry_run)
            if should_activate:
                try:
                    self.set_version_active(esv_id, True)
                    self.wait_for_version_state(esv_id, True)
                    if cascaded_ppvs:
                        self.cascade_reactivate_procedure_plans(cascaded_ppvs)
                except Exception as reactivate_exc:
                    if failure:
                        raise LifecycleError(
                            f"{verb} failed, and reactivation also failed: "
                            f"{reactivate_exc}"
                        ) from failure
                    raise
            elif failure and deactivated and not self.dry_run:
                self.log(
                    f"{verb} failed and may have partially applied. Leaving "
                    f"ExpressionSetVersion {esv_id} DEACTIVATED to avoid re-enabling "
                    f"a corrupted definition. Inspect/restore it manually, then "
                    f"reactivate (cascaded procedure plans {cascaded_ppvs or '(none)'} "
                    f"remain deactivated)."
                )
            elif deactivated and not self.dry_run:
                self.log(
                    f"activate_after=false; leaving ExpressionSetVersion {esv_id} "
                    f"and cascaded procedure plans {cascaded_ppvs or '(none)'} "
                    f"DEACTIVATED as requested."
                )

        if failure:
            raise failure

    # -- Delete --------------------------------------------------------

    def delete_single_version(
        self, version_api_name: str, es_id: str, api_name: str
    ) -> Dict[str, Any]:
        """Delete one ExpressionSetVersion (by ApiName) via the SObject API.

        Used by the post-new-version → delete-old-version workflow, leaving the
        expression set and its other versions intact. An enabled version is
        deactivated first.
        """
        records = self.t.soql(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE ApiName = '{soql_literal(version_api_name)}' "
            f"AND ExpressionSetId = '{soql_literal(es_id)}'"
        )
        if not records:
            raise LifecycleError(
                f"ExpressionSetVersion '{version_api_name}' not found under "
                f"expression set '{api_name}' ({es_id}). Verify the version name "
                f"belongs to this expression set."
            )
        version_id = records[0]["Id"]
        if bool(records[0].get("IsActive")):
            self.set_version_active(version_id, False)
            self.wait_for_version_state(version_id, False)
        self.t.sobject("DELETE", "ExpressionSetVersion", version_id)
        self.log(
            f"Deleted ExpressionSetVersion {version_api_name} ({version_id})."
        )
        return {
            "action": "delete_version",
            "expressionSet": api_name,
            "version": version_api_name,
            "versionId": version_id,
            "dryRun": self.dry_run,
        }

    def delete_expression_set(
        self, *, es_id: str, es_def_id: str, esv: dict, api_name: str
    ) -> Dict[str, Any]:
        """Delete a whole expression set (Connect DELETE), with rollback.

        Cascade-deactivate referencing procedure-plan versions, deactivate the ES
        version, then DELETE. If anything between cascade and DELETE fails,
        restore the cluster to its exact pre-attempt state — a failed DELETE
        leaves the record byte-identical, so re-enabling is safe (unlike a failed
        PATCH). The ES version is reactivated FIRST so the plans re-point at an
        active definition; if that rollback fails, the plans are LEFT deactivated
        rather than pointed at an inactive ES.
        """
        esv_was_active = bool(esv.get("IsActive"))
        cascaded_ppvs: List[str] = []
        esv_deactivated_by_us = False
        try:
            cascaded_ppvs = self.cascade_deactivate_procedure_plans(es_def_id)
            if esv_was_active:
                self.set_version_active(esv["Id"], False)
                self.wait_for_version_state(esv["Id"], False)
                if not self.dry_run:
                    esv_deactivated_by_us = True
            self.delete_definition_connect(es_id)
        except Exception:
            if not self.dry_run:
                self._rollback_delete(esv, esv_deactivated_by_us, cascaded_ppvs)
            raise
        self.log(f"Deleted expression set {api_name} ({es_id}).")
        return {
            "action": "delete_expression_set",
            "expressionSet": api_name,
            "expressionSetId": es_id,
            "cascadedProcedurePlanVersions": cascaded_ppvs,
            "dryRun": self.dry_run,
        }

    def _rollback_delete(
        self, esv: dict, esv_deactivated_by_us: bool, cascaded_ppvs: List[str]
    ) -> None:
        rollback_errors: List[str] = []
        es_rollback_safe = not esv_deactivated_by_us
        if esv_deactivated_by_us:
            try:
                self.set_version_active(esv["Id"], True)
                self.wait_for_version_state(esv["Id"], True)
                es_rollback_safe = True
            except Exception as rb_exc:
                rollback_errors.append(f"ExpressionSetVersion {esv['Id']}: {rb_exc}")
        if cascaded_ppvs:
            if es_rollback_safe:
                try:
                    self.cascade_reactivate_procedure_plans(cascaded_ppvs)
                except Exception as rb_exc:
                    rollback_errors.append(
                        f"ProcedurePlanDefinitionVersion(s) {cascaded_ppvs}: {rb_exc}"
                    )
            else:
                rollback_errors.append(
                    f"ProcedurePlanDefinitionVersion(s) {cascaded_ppvs} LEFT "
                    f"DEACTIVATED — ES version rollback failed, so reactivating the "
                    f"plans would point them at an inactive ES"
                )
        if rollback_errors:
            self.log(
                "Delete failed AND rollback reactivation failed: "
                + "; ".join(rollback_errors)
                + ". Manual intervention required."
            )
