#!/usr/bin/env python3
"""The one expression-set deactivate → mutate → recover engine.

Shared by the standalone toolkit (``_lifecycle.LifecycleEngine``) and the CCI task
(``tasks/rlm_expression_set_connect.py``). Stdlib only, and it must stay that way:
the CCI task imports it, and ``tests/test_expression_set_schema.py`` runs under base
Python without CumulusCI.

:class:`LifecycleCore` owns the state machine — the procedure-plan cascade, the
version-state transitions, the failure recovery and health report, and the delete
rollback. An adapter subclasses it and supplies the I/O and the conventions that
differ between the two callers:

* **I/O hooks** — :meth:`query` (SOQL), :meth:`write_sobject` (an sObject PATCH),
  :meth:`delete_sobject`, :meth:`delete_definition` (the Connect DELETE) and
  :meth:`wait_for_version_state`.
* **Lifecycle hooks** — :meth:`set_version_active`,
  :meth:`find_referencing_procedure_plans`,
  :meth:`cascade_deactivate_procedure_plans`,
  :meth:`cascade_reactivate_procedure_plans` and :meth:`report_procedure_health`.
  The state machine calls these, never the ``*_impl`` methods directly, so an
  adapter can route them through its own seams (the CCI task's methods, which its
  tests override). The defaults call the shared ``*_impl`` implementations.
* **Conventions** — :attr:`error_class` (``LifecycleError`` for the toolkit,
  ``TaskOptionsError`` for CCI), :meth:`emit` (leveled logging),
  :attr:`dry_run_style` and :meth:`restore_target_org`.

``dry_run_style`` reproduces each caller's dry-run exactly:

* ``"transport"`` (toolkit) — reads run; writes go to the I/O hooks, whose transport
  logs and skips them; the engine logs the same success lines as a real run.
* ``"announce"`` (CCI) — writes are not issued at all; the engine logs
  ``[dry-run] Would …`` instead, and :meth:`set_version_active_impl` skips its read.

The guarantees (live-verified on 262 / v67.0 and 264 / v68.0) are documented on
:meth:`LifecycleCore.run_mutation`.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from ._guards import null_rank_reactivation_refusal

# The platform's rejection of an update to an enabled version; proves it is active.
ALREADY_ENABLED = "An enabled Expression Set Version cannot be updated"

# Enum of the two ResourceInitializationType values the PATCH body may carry.
RESOURCE_INIT_TYPES = frozenset({"Default", "Off"})

DRY_RUN_STYLES = ("transport", "announce")


def soql_literal(value: Any) -> str:
    """Escape a value for safe interpolation inside a single-quoted SOQL literal."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


class LifecycleCore:
    """The shared state machine. Subclass it and implement the I/O hooks."""

    #: Exception class the engine raises (an adapter sets its own).
    error_class: type = RuntimeError
    #: ``"transport"`` or ``"announce"`` — see the module docstring.
    dry_run_style: str = "transport"

    def __init__(self, *, dry_run: bool):
        if self.dry_run_style not in DRY_RUN_STYLES:
            raise ValueError(f"dry_run_style must be one of {DRY_RUN_STYLES}")
        self.dry_run = dry_run

    # -- Adapter hooks: I/O ----------------------------------------------

    def query(self, soql: str) -> List[dict]:
        raise NotImplementedError

    def write_sobject(self, sobject: str, record_id: str, body: dict) -> None:
        raise NotImplementedError

    def delete_sobject(self, sobject: str, record_id: str) -> None:
        raise NotImplementedError

    def delete_definition(self, es_id: str) -> Any:
        raise NotImplementedError

    def wait_for_version_state(self, version_id: str, active: bool) -> None:
        """Wait until the version reads ``IsActive=active`` (usually via
        :meth:`poll_version_state` with the adapter's timing)."""
        raise NotImplementedError

    def emit(self, level: str, message: str) -> None:
        """Log ``message`` at ``level`` (``info`` / ``warning`` / ``error``)."""
        raise NotImplementedError

    def restore_target_org(self) -> Optional[str]:
        """The ``--target-org`` value printed in restore commands; None when unknown
        (the restore step is then described in words)."""
        return None

    def command_target_org(self) -> Optional[str]:
        """The org the run used, for a printed remedy command; None when unknown."""
        return None

    def definition_name(self, es_def_id: str) -> Optional[str]:
        """The set's DeveloperName, for a printed command; None when unreadable."""
        try:
            rows = self.query("SELECT DeveloperName FROM ExpressionSetDefinition "
                              f"WHERE Id = '{soql_literal(es_def_id)}'")
        except Exception:  # noqa: BLE001 -- only fills a message
            return None
        return (rows[0].get("DeveloperName") if rows else None) or None

    # -- Adapter hooks: lifecycle (default to the shared implementations) --

    def set_version_active(self, version_id: str, active: bool, *,
                           force: Optional[bool] = None) -> None:
        """``force=None`` means the caller did not pass one (same as False)."""
        self.set_version_active_impl(version_id, active, force=bool(force))

    def find_referencing_procedure_plans(self, es_def_id: str) -> List[dict]:
        return self.find_referencing_procedure_plans_impl(es_def_id)

    def cascade_deactivate_procedure_plans(self, es_def_id: str, *,
                                           rollback: bool = True) -> List[str]:
        return self.cascade_deactivate_impl(es_def_id, rollback=rollback)

    def cascade_reactivate_procedure_plans(self, version_ids: List[str]) -> None:
        self.cascade_reactivate_impl(version_ids)

    def report_procedure_health(self, es_def_id: str, esv_id: str, *,
                                taken_down: List[str], version_taken_down: bool,
                                version_may_be_half_written: bool = False) -> List[str]:
        return self.report_procedure_health_impl(
            es_def_id, esv_id, taken_down=taken_down,
            version_taken_down=version_taken_down,
            version_may_be_half_written=version_may_be_half_written)

    # -- Helpers -----------------------------------------------------------

    @property
    def _announce(self) -> bool:
        """True when a dry-run write is announced instead of issued."""
        return self.dry_run and self.dry_run_style == "announce"

    def _version_state(self, version_id: str) -> Optional[bool]:
        records = self.query(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE Id = '{soql_literal(version_id)}'"
        )
        if not records:
            return None
        return bool(records[0].get("IsActive"))

    def _plan_is_active(self, vid: str) -> bool:
        records = self.query(
            "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
            f"WHERE Id = '{soql_literal(vid)}'"
        )
        return bool(records and records[0].get("IsActive"))

    # -- Version state -----------------------------------------------------

    def set_version_active_impl(self, version_id: str, active: bool, *,
                                force: bool = False) -> None:
        """Set ``ExpressionSetVersion.IsActive`` (idempotent unless ``force``).

        ``force`` sends the PATCH even when a read already shows the desired
        state. Recovery after an unconfirmed deactivation uses it: the stale read
        that made the deactivation poll time out would otherwise skip the
        reactivation. A forced PATCH rejected with the platform's "already
        enabled" error is taken as active; any other rejection raises.

        Skips the PATCH when the version is already in the desired state: a
        Connect full-graph PATCH whose body carries ``enabled: true`` reactivates
        the version itself, so a later explicit reactivation would otherwise hit
        the "An enabled Expression Set Version cannot be updated/deleted." guard
        and fail a genuinely-successful mutation.
        """
        if self._announce:
            self.emit("info", f"[dry-run] Would set ExpressionSetVersion {version_id} "
                              f"IsActive={active}")
            return
        if not force and self._version_state(version_id) is active:
            self.emit("info", f"ExpressionSetVersion {version_id} already "
                              f"IsActive={active}; no change needed.")
            return
        try:
            self.write_sobject("ExpressionSetVersion", version_id, {"IsActive": active})
        except Exception as exc:
            # Only the platform's own "already enabled" rejection proves the
            # version is active. A read can't: recovery forces the PATCH because
            # reads were stale.
            if force and active and ALREADY_ENABLED in str(exc):
                self.emit("warning", f"ExpressionSetVersion {version_id} rejected the "
                                     "forced PATCH as already enabled; taking it as active.")
                return
            raise
        self.emit("info", f"Set ExpressionSetVersion {version_id} IsActive={active}.")

    def poll_version_state(self, version_id: str, active: bool, *, max_wait: int,
                           poll: int, sleep: Callable[[float], None] = time.sleep) -> None:
        """Poll until the version reads ``IsActive=active``; raise after ``max_wait``s."""
        waited = 0
        while waited <= max_wait:
            if self._version_state(version_id) is active:
                self.emit("info", f"Confirmed ExpressionSetVersion {version_id} "
                                  f"IsActive={active} after {waited}s.")
                return
            sleep(poll)
            waited += poll
        raise self.error_class(
            f"ExpressionSetVersion {version_id} did not reach IsActive={active} "
            f"within {max_wait}s."
        )

    def ensure_resource_initialization_type_impl(self, es_id: str,
                                                 desired: Optional[str] = None) -> None:
        """Align stored ``ExpressionSet.ResourceInitializationType`` before a PATCH.

        Connect GET reports "Off" while the sObject stores null on seeded
        procedures; PATCH validates the body against the stored value and rejects
        a mismatch. Writing the stored field to the value the PATCH body carries
        aligns the two. ``desired`` is the value the body will carry (default
        "Off", what GET serializes over a stored null). The field is immutable once
        set: if it already holds a value this only raises on a conflict (never
        rewrites it). Raising here happens BEFORE any deactivation, so a guaranteed
        PATCH failure never leaves a version deactivated.
        """
        target = desired or "Off"
        if target not in RESOURCE_INIT_TYPES:
            self.emit("warning", "Ignoring unrecognized resourceInitializationType "
                                 f"'{target}'; valid values are "
                                 f"{sorted(RESOURCE_INIT_TYPES)}.")
            target = "Off"
        records = self.query(
            "SELECT Id, ResourceInitializationType FROM ExpressionSet "
            f"WHERE Id = '{soql_literal(es_id)}'"
        )
        if not records:
            return
        current = records[0].get("ResourceInitializationType")
        if current:
            if desired and desired != current:
                raise self.error_class(
                    f"ExpressionSet {es_id} ResourceInitializationType is already "
                    f"'{current}' and is immutable; the payload's '{desired}' "
                    f"cannot be applied. Update the payload to match the stored "
                    f"value before retrying."
                )
            return
        if self._announce:
            self.emit("info", f"[dry-run] Would set ExpressionSet {es_id} "
                              f"ResourceInitializationType={target} (currently null).")
            return
        self.emit("info", f"ExpressionSet {es_id} has null ResourceInitializationType; "
                          f"setting it to '{target}' so the Connect PATCH is accepted.")
        self.write_sobject("ExpressionSet", es_id, {"ResourceInitializationType": target})

    # -- Procedure-plan cascade ----------------------------------------------

    def find_referencing_procedure_plans_impl(self, es_def_id: str) -> List[dict]:
        return self.query(
            "SELECT Id, ProcedurePlanSection.ProcedurePlanVersionId "
            "FROM ProcedurePlanOption "
            f"WHERE ExpressionSetDefinitionId = '{soql_literal(es_def_id)}'"
        )

    def cascade_deactivate_impl(self, es_def_id: str, *, rollback: bool = True) -> List[str]:
        """Deactivate active procedure-plan versions referencing this ES.

        Returns the version ids that were (or, in dry-run, would be) deactivated.
        On a partial failure, rolls back only the versions this call already
        deactivated, then raises — the pre-mutation cascade must not leave a
        half-deactivated cluster behind. With ``rollback=False`` (the emergency
        shutdown after a failed PATCH) every plan is attempted, nothing is turned
        back on, and the raised error's ``left_inactive`` names the plans it did
        turn off.
        """
        options = self.find_referencing_procedure_plans(es_def_id)
        if not options:
            return []
        version_ids = set()
        for opt in options:
            vid = (opt.get("ProcedurePlanSection") or {}).get("ProcedurePlanVersionId")
            if vid:
                version_ids.add(vid)
        deactivated: List[str] = []
        if not rollback and not self._announce:
            failures: List[str] = []
            for vid in sorted(version_ids):
                try:
                    if self._plan_is_active(vid):
                        self.write_sobject("ProcedurePlanDefinitionVersion", vid,
                                           {"IsActive": False})
                        self.emit("info", f"Deactivated ProcedurePlanDefinitionVersion {vid}.")
                        deactivated.append(vid)
                except Exception as exc:
                    failures.append(f"{vid}: {exc}")
            if failures:
                error = self.error_class(
                    "Could not deactivate ProcedurePlanDefinitionVersion(s): "
                    + "; ".join(failures)
                )
                error.left_inactive = list(deactivated)
                raise error
            return deactivated
        try:
            for vid in sorted(version_ids):
                if self._plan_is_active(vid):
                    if self._announce:
                        self.emit("info", "[dry-run] Would deactivate "
                                          f"ProcedurePlanDefinitionVersion {vid}")
                    else:
                        self.write_sobject("ProcedurePlanDefinitionVersion", vid,
                                           {"IsActive": False})
                        self.emit("info", "Deactivated ProcedurePlanDefinitionVersion "
                                          f"{vid} (cascade).")
                    deactivated.append(vid)
        except Exception as exc:
            if deactivated and not self.dry_run:
                try:
                    self.cascade_reactivate_procedure_plans(deactivated)
                except Exception as rollback_exc:
                    error = self.error_class(
                        "Cascade deactivation failed after deactivating "
                        f"ProcedurePlanDefinitionVersion(s) {deactivated}, and "
                        f"rollback also failed: {rollback_exc}"
                    )
                    # Callers restore and report these; the return value never
                    # reaches them on this path.
                    error.left_inactive = list(deactivated)
                    raise error from exc
                raise self.error_class(
                    "Cascade deactivation failed after deactivating "
                    f"ProcedurePlanDefinitionVersion(s) {deactivated}; rolled them "
                    "back before aborting."
                ) from exc
            raise
        return deactivated

    def cascade_reactivate_impl(self, version_ids: List[str]) -> None:
        """Reactivate each plan version, attempting every one before raising.

        One failed PATCH must not leave the later plans offline, so failures are
        collected and raised together after all ids have been tried.
        """
        failures: List[str] = []
        for vid in version_ids:
            if self._announce:
                self.emit("info", "[dry-run] Would reactivate "
                                  f"ProcedurePlanDefinitionVersion {vid}")
                continue
            try:
                self.write_sobject("ProcedurePlanDefinitionVersion", vid, {"IsActive": True})
                self.emit("info", f"Reactivated ProcedurePlanDefinitionVersion {vid}.")
            except Exception as exc:
                failures.append(f"{vid}: {exc}")
        if failures:
            raise self.error_class(
                "Could not reactivate ProcedurePlanDefinitionVersion(s): "
                + "; ".join(failures)
            )

    # -- The deactivate → mutate → reactivate sequencer ----------------------

    def run_mutation(
        self,
        *,
        es_def_id: str,
        esv: dict,
        mutate: Callable[[], None],
        activate_after: bool,
        cascade: bool,
        verb: str = "mutation",
        reactivate_on_failure: bool = False,
    ) -> None:
        """Run the safety-critical deactivate → mutate → reactivate lifecycle.

        * A mutation requires the version **inactive**, so an active version (and,
          with ``cascade``, the referencing procedure-plan versions) is deactivated
          first. ``mutate`` runs while it is off and handles its own dry-run.
        * Reactivation follows the explicit ``activate_after``, not the prior
          state: an explicit false wins and leaves it off for inspection.
        * **A failed definition PATCH is not atomic.** The version is never
          reactivated over it: reactivation happens only when the mutation
          succeeded, failed before it started (nothing was written, e.g. the
          deactivation poll timed out), or in dry-run. ``reactivate_on_failure``
          relaxes this for a mutation that cannot corrupt the definition (an atomic
          Tooling sObject PATCH, such as a relabel), so its failure does not take a
          live procedure offline.
        * **A failed PATCH still restores the cascaded procedure plans** (when
          ``activate_after``), once the version is confirmed off. An inactive plan
          is skipped at pricing time — pricing falls back to the Revenue Settings
          default procedure, so prices look plausible while wrong — whereas an
          active plan over an inactive version fails loudly (both live-checked on
          264 / v68.0). If the version cannot be confirmed off the plans stay off,
          and with ``cascade`` every other active referencing plan is taken off.
        * After any failure, including a failed recovery, the version and every
          referencing plan are re-read and reported; records this run deactivated
          get a restore command.

        Re-raises the original failure (chaining a recovery failure onto it when
        both happen). Refuses, before any write, to cycle an active version with no
        Rank (``_guards.null_rank_reactivation_refusal``): the API could not turn it
        back on.
        """
        if null_rank_reactivation_refusal(esv, activate_after):
            # Fill the remedy commands with this run's org and the set's name.
            raise self.error_class(null_rank_reactivation_refusal(
                esv, activate_after, target_org=self.command_target_org(),
                es_api_name=self.definition_name(es_def_id)))
        esv_id = esv["Id"]
        was_active = bool(esv.get("IsActive"))
        deactivated = False
        cascaded_ppvs: List[str] = []
        failure: Optional[Exception] = None
        reactivate_error: Optional[Exception] = None
        mutate_succeeded = False
        # Set before the version PATCH, so a PATCH that lands but whose
        # confirmation poll fails still counts as taken down.
        version_off_attempted = False
        mutate_started = False

        try:
            if was_active:
                if cascade:
                    try:
                        cascaded_ppvs = self.cascade_deactivate_procedure_plans(es_def_id)
                    except Exception as cascade_exc:
                        cascaded_ppvs = list(getattr(cascade_exc, "left_inactive", ()))
                        raise
                version_off_attempted = True
                self.set_version_active(esv_id, False)
                if not self.dry_run:
                    self.wait_for_version_state(esv_id, False)
                deactivated = True
            else:
                self.emit("info", f"ExpressionSetVersion {esv_id} already inactive.")

            mutate_started = True
            mutate()
            mutate_succeeded = True
        except Exception as exc:
            failure = exc
        finally:
            # A failure before mutate() started wrote nothing, so everything
            # this run took down is safe to restore.
            failed_before_mutate = bool(failure) and not mutate_started
            should_activate = activate_after and (
                mutate_succeeded
                or self.dry_run
                or (reactivate_on_failure and deactivated)
                or (failed_before_mutate and (version_off_attempted or cascaded_ppvs))
            )
            if should_activate:
                if failed_before_mutate and not self.dry_run:
                    self.emit("warning",
                              f"{verb} failed before the mutation ran, so nothing was "
                              f"written; restoring ExpressionSetVersion {esv_id} and the "
                              f"cascaded procedure plans. The failure is still reported.")
                elif failure and not (mutate_succeeded or self.dry_run):
                    self.emit("warning",
                              f"{verb} failed, but it is a non-corrupting mutation (an "
                              f"atomic Tooling Metadata PATCH, so nothing was "
                              f"half-written), so reactivating ExpressionSetVersion "
                              f"{esv_id} rather than leaving it offline. The failure "
                              f"is still reported.")
                # The version and the plans are restored independently, so a
                # failed version reactivation can't leave the plans offline.
                # Errors are raised after the health report below.
                if was_active or not failed_before_mutate:
                    try:
                        # After an unconfirmed deactivation, a stale read could
                        # make the idempotent setter skip the PATCH; force it.
                        self.set_version_active(
                            esv_id, True,
                            force=failed_before_mutate and version_off_attempted,
                        )
                        if not self.dry_run:
                            self.wait_for_version_state(esv_id, True)
                    except Exception as reactivate_exc:
                        reactivate_error = reactivate_exc
                if cascaded_ppvs:
                    try:
                        self.cascade_reactivate_procedure_plans(cascaded_ppvs)
                    except Exception as plan_exc:
                        if reactivate_error:
                            self.emit("error", f"Plan reactivation also failed: {plan_exc}")
                        else:
                            reactivate_error = plan_exc
            elif (failure and mutate_started and not reactivate_on_failure
                  and not self.dry_run):
                self.emit("error",
                          f"{verb} failed and may have partially applied. Leaving "
                          f"ExpressionSetVersion {esv_id} DEACTIVATED to avoid "
                          f"re-enabling a corrupted definition. Inspect/restore it "
                          f"manually, then reactivate it.")
                # A failed full-graph PATCH may still have applied
                # `enabled: true`, leaving a half-written version active, even
                # one that was off before the run. Turn it off and confirm,
                # whether or not any plans are waiting to be restored.
                try:
                    # Forced: a read right after the PATCH can still say false
                    # (stale) while the version is active. A forced
                    # IsActive=false on an inactive version is accepted
                    # (live-checked on 264), so this is safe either way.
                    self.set_version_active(esv_id, False, force=True)
                    self.wait_for_version_state(esv_id, False)
                    version_off = True
                except Exception as off_exc:
                    version_off = False
                    reactivate_error = off_exc
                    self.emit("error",
                              f"Could not confirm ExpressionSetVersion {esv_id} is "
                              f"inactive after the failed {verb} ({off_exc}); it may be "
                              f"active and half-written. Any cascaded procedure plans "
                              f"stay off, because they could route pricing to it.")
                    if cascade:
                        # A plan that was active before the run (the version
                        # started inactive, so nothing cascaded) would route
                        # pricing to it too; take every active one off.
                        try:
                            more = self.cascade_deactivate_procedure_plans(
                                es_def_id, rollback=False
                            )
                        except Exception as plan_off_exc:
                            more = list(getattr(plan_off_exc, "left_inactive", ()))
                            self.emit("error", "Could not deactivate the referencing "
                                               f"procedure plans: {plan_off_exc}")
                        cascaded_ppvs = cascaded_ppvs + [
                            vid for vid in more if vid not in cascaded_ppvs
                        ]
                if activate_after and cascaded_ppvs and version_off:
                    try:
                        self.cascade_reactivate_procedure_plans(cascaded_ppvs)
                        self.emit("info",
                                  "Reactivated the cascaded procedure plans, so pricing "
                                  "doesn't silently skip the plan: with no other active "
                                  "version of this expression set it fails loudly instead.")
                    except Exception as plan_exc:
                        # Kept, so the combined error below says a plan is
                        # still off.
                        reactivate_error = plan_exc
            elif deactivated and not self.dry_run:
                # Success, but activate_after=false: leave the version (and any
                # cascaded procedure plans) deactivated as the caller requested.
                self.emit("info",
                          f"activate_after=false; leaving ExpressionSetVersion {esv_id} "
                          f"and cascaded procedure plans {cascaded_ppvs or '(none)'} "
                          f"DEACTIVATED as requested.")

        if (failure or reactivate_error) and not self.dry_run:
            try:
                self.report_procedure_health(
                    es_def_id, esv_id,
                    taken_down=cascaded_ppvs, version_taken_down=version_off_attempted,
                    version_may_be_half_written=(
                        mutate_started and not mutate_succeeded
                        and not reactivate_on_failure
                    ),
                )
            except Exception as health_exc:
                self.emit("error", "Could not read procedure health after the "
                                   f"failure: {health_exc}")

        if reactivate_error:
            if failure:
                raise self.error_class(
                    f"{verb} failed, and recovery also failed: "
                    f"{reactivate_error}"
                ) from failure
            raise reactivate_error
        if failure:
            raise failure

    def report_procedure_health_impl(
        self,
        es_def_id: str,
        esv_id: str,
        *,
        taken_down: List[str],
        version_taken_down: bool,
        version_may_be_half_written: bool = False,
    ) -> List[str]:
        """Re-read activation state after a failure and warn on anything off.

        Only records this run deactivated (``taken_down`` plans, and the version
        when ``version_taken_down``) get a restore command; their prior state is
        known to be active. Other inactive procedure-plan versions referencing the
        expression set are listed for inspection only: a plan can keep inactive
        draft, expired or lower-ranked versions on purpose, and activating one
        could change which version runs. Returns one ``"<sObject> <Id>"`` entry
        per record this run left inactive.

        ``version_may_be_half_written`` marks a failed definition PATCH: if the
        version still reads active, restoring a plan would route pricing to it,
        so the report says to inspect and deactivate the version first.
        """
        left_off: List[str] = []
        # Records whose state couldn't be read; never counted as healthy.
        unknown: List[str] = []
        version_was_off = False
        version_state = self._version_state(esv_id)
        if version_state is None:
            unknown.append(f"ExpressionSetVersion {esv_id}")
        if version_state is False:
            if version_taken_down:
                left_off.append(f"ExpressionSetVersion {esv_id}")
            else:
                version_was_off = True
        plan_ids = sorted({
            (opt.get("ProcedurePlanSection") or {}).get("ProcedurePlanVersionId")
            for opt in self.find_referencing_procedure_plans(es_def_id)
        } - {None} | set(taken_down))
        other_inactive: List[str] = []
        for vid in plan_ids:
            records = self.query(
                "SELECT Id, IsActive FROM ProcedurePlanDefinitionVersion "
                f"WHERE Id = '{soql_literal(vid)}'"
            )
            if not records:
                unknown.append(f"ProcedurePlanDefinitionVersion {vid}")
            elif not records[0].get("IsActive"):
                if vid in taken_down:
                    left_off.append(f"ProcedurePlanDefinitionVersion {vid}")
                else:
                    other_inactive.append(vid)
        version_unsafe = version_may_be_half_written and version_state is not False
        if not left_off and not other_inactive and not version_was_off \
                and not version_unsafe and not unknown:
            self.emit("info", "Procedure health after the failure: the version and all "
                              "referencing procedure plans are active.")
            return left_off
        lines = ["!" * 72]
        if unknown:
            lines.append(
                f"WARNING: could not read the state of {', '.join(unknown)}. "
                "Check each before reading any price; an inactive plan this run "
                "deactivated needs IsActive=true."
            )
        if version_unsafe:
            lines.append(
                f"WARNING: ExpressionSetVersion {esv_id} is NOT confirmed inactive "
                "after the failed PATCH and may be half-written. Inspect it and "
                "deactivate it before restoring any plan; an active plan would "
                "route pricing to it."
            )
        if left_off:
            lines.append("WARNING: records this run deactivated are still INACTIVE.")
            if any(r.startswith("ProcedurePlanDefinitionVersion") for r in left_off):
                lines.append(
                    "An inactive procedure plan is skipped: pricing silently falls back "
                    "to the Revenue Settings default procedure and none of the plan's "
                    "other procedures run, so prices look plausible but are wrong."
                )
                if not version_unsafe:
                    lines.append("Restore the plan before reading any price.")
            for record in left_off:
                sobject, record_id = record.split(" ", 1)
                if sobject == "ExpressionSetVersion" and version_may_be_half_written:
                    lines.append(
                        f"  {record}: no command; the failed PATCH may have left it "
                        "half-written. Re-import a known-good definition before "
                        "reactivating it."
                    )
                    continue
                org = self.restore_target_org()
                lines.append(
                    f"  {record}: sf data update record --target-org {org} --sobject "
                    f"{sobject} --record-id {record_id} --values \"IsActive=true\""
                    if org else
                    f"  {record}: set IsActive true on it in the org this run used"
                )
            if (f"ExpressionSetVersion {esv_id}" in left_off
                    and not version_may_be_half_written):
                lines.append(
                    "Inspect the expression-set version before reactivating it; a "
                    "failed PATCH can leave it half-written."
                )
        if version_was_off:
            lines.append(
                f"ExpressionSetVersion {esv_id} is inactive, as it was before this "
                "run; it was not reactivated."
            )
        if other_inactive:
            lines.append(
                "Other procedure-plan versions referencing this expression set are "
                f"inactive: {', '.join(other_inactive)}. They may be intentional "
                "(draft, expired or lower-ranked) or left off by an earlier failed "
                "run; check which version should be active before changing any."
            )
        lines.append("!" * 72)
        for line in lines:
            self.emit("error", line)
        return left_off

    # -- Delete --------------------------------------------------------------

    def delete_single_version(self, version_api_name: str, es_id: str,
                              api_name: str) -> Dict[str, Any]:
        """Delete one ExpressionSetVersion (by ApiName), leaving the set and its
        other versions intact. An enabled version is deactivated first."""
        records = self.query(
            "SELECT Id, IsActive FROM ExpressionSetVersion "
            f"WHERE ApiName = '{soql_literal(version_api_name)}' "
            f"AND ExpressionSetId = '{soql_literal(es_id)}'"
        )
        if not records:
            raise self.error_class(
                f"ExpressionSetVersion '{version_api_name}' not found under "
                f"expression set '{api_name}' ({es_id}). Verify the version name "
                f"belongs to this expression set."
            )
        version_id = records[0]["Id"]
        if bool(records[0].get("IsActive")):
            # An enabled version cannot be deleted; deactivate first.
            self.set_version_active(version_id, False)
            if not self.dry_run:
                self.wait_for_version_state(version_id, False)
        result = {
            "action": "delete_version",
            "expressionSet": api_name,
            "version": version_api_name,
            "versionId": version_id,
            "dryRun": self.dry_run,
        }
        if self._announce:
            self.emit("info", f"[dry-run] Would delete ExpressionSetVersion "
                              f"{version_api_name} ({version_id}).")
            return result
        self.delete_sobject("ExpressionSetVersion", version_id)
        self.emit("info", f"Deleted ExpressionSetVersion {version_api_name} ({version_id}).")
        return result

    def delete_expression_set(self, *, es_id: str, es_def_id: str, esv: dict,
                              api_name: str) -> Dict[str, Any]:
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
        result: Dict[str, Any] = {
            "action": "delete_expression_set",
            "expressionSet": api_name,
            "expressionSetId": es_id,
            "cascadedProcedurePlanVersions": cascaded_ppvs,
            "dryRun": self.dry_run,
        }
        try:
            try:
                cascaded_ppvs = self.cascade_deactivate_procedure_plans(es_def_id)
            except Exception as cascade_exc:
                cascaded_ppvs = list(getattr(cascade_exc, "left_inactive", ()))
                raise
            result["cascadedProcedurePlanVersions"] = cascaded_ppvs
            if esv_was_active:
                self.set_version_active(esv["Id"], False)
                if not self.dry_run:
                    self.wait_for_version_state(esv["Id"], False)
                    esv_deactivated_by_us = True
            if self._announce:
                self.emit("info", f"[dry-run] Would DELETE expression set {api_name} "
                                  f"({es_id}).")
                return result
            self.delete_definition(es_id)
        except Exception:
            if not self.dry_run:
                self._rollback_delete(esv, esv_deactivated_by_us, cascaded_ppvs)
            raise
        self.emit("info", f"Deleted expression set {api_name} ({es_id}).")
        return result

    def _rollback_delete(self, esv: dict, esv_deactivated_by_us: bool,
                         cascaded_ppvs: List[str]) -> None:
        rollback_errors: List[str] = []
        # Reactivate the ES version FIRST so re-enabled plans reference an active
        # definition. If that fails (or it was never deactivated), DO NOT
        # reactivate the plans: they would point traffic at an inactive ES.
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
            self.emit("error", "Delete failed AND rollback reactivation failed: "
                               + "; ".join(rollback_errors)
                               + ". Manual intervention required.")
