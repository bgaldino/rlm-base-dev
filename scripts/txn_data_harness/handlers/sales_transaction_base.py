"""Shared base handler for PST-spine scenario kinds.

Both ``sales_txn_quote`` and ``sales_txn_order`` (Phase 3) drive the same
post-Quote/post-Order tail: ``order_activated -> usage_upload -> invoice_draft
-> invoice_posted``. Only the head differs -- quote-path goes through PST place
+ ``order_from_quote``; order-path goes through PST place-on-Order
(``order_direct``). The split lives in each subclass's :attr:`STAGES` and
:attr:`STEP_GRAPH`; the resolve/run/retry/summarize logic is shared here so a
bug fix in the retry loop or a new public-stage rule lands in one place.

The base is intentionally *not* a ``Protocol`` -- it carries concrete
implementations the runtime calls into. :class:`scripts.txn_data_harness.
handlers.base.ScenarioHandler` is still the public contract (runtime-checked
in tests); subclasses satisfy it structurally.
"""

from __future__ import annotations

import logging
import time
from typing import Any, ClassVar, Optional

from ..auth import SfRestClient
from ..config import ScenarioSpec
from ..discovery import Account, OrgContext
from ..failure import classify_exception
from ..lifecycle import LifecycleError
from ..manifests import write_manifest
from ..models import IMPLEMENTED_MAX_STAGE, Manifest, ResolvedSpec
from ..steps import StepContext, execute_step

log = logging.getLogger("txn_data_harness.handlers.sales_transaction_base")

# Retry policy mirrors runner.run_scenario so handler-owned execution and
# the legacy free function agree on how aggressively transient failures retry.
_RETRY_BACKOFF_BASE = 30.0
_RETRY_BACKOFF_MAX = 90.0


def _retry_backoff(attempt: int) -> float:
    return min(_RETRY_BACKOFF_BASE * (2 ** (attempt - 1)), _RETRY_BACKOFF_MAX)


class SalesTransactionBaseHandler:
    """Concrete base for PST-spine handlers (quote-path + order-path).

    Subclasses declare ``kind``, :attr:`STAGES`, and :attr:`STEP_GRAPH`; the
    base implements stage math, resolve, run-with-retry, and summarize.
    """

    kind: ClassVar[str] = ""
    # Public stages this kind walks (ordered). Subclass overrides:
    # quote-path -> STAGES_QUOTE; order-path -> STAGES_ORDER.
    STAGES: ClassVar[list[str]] = []
    # Public stage -> internal step name. Most stages map 1:1 by name; the
    # only divergence today is ``order_draft`` (quote -> ``order_from_quote``,
    # order -> ``order_direct``). The base falls back to the public name when a
    # stage is missing from the map.
    STEP_GRAPH: ClassVar[dict[str, str]] = {}

    # -- stage math ----------------------------------------------------------

    def effective_stage(self, target_stage: str, account: Account) -> str:
        """Resolve the stage a scenario will actually reach.

        Caps the requested stage to whatever the harness implements, then
        further caps at ``order_draft`` for non-billing-ready accounts
        (activation generates BillingSchedules and Assets, which require a
        BillingAccount on the Account).
        """
        stages = self.STAGES
        stage = target_stage
        if stages.index(stage) > stages.index(IMPLEMENTED_MAX_STAGE):
            stage = IMPLEMENTED_MAX_STAGE
        if not account.is_billing_ready and stages.index(stage) > stages.index("order_draft"):
            stage = "order_draft"
        return stage

    def stage_sequence(
        self, target_stage: str, with_opportunity: bool
    ) -> list[str]:
        """Return the ordered public stages needed to reach ``target_stage``.

        ``opportunity_created`` is prepended only when ``with_opportunity`` is
        true or the target stage is ``opportunity_created`` itself; otherwise
        the sequence starts at the stage immediately after it (``quote_placed``
        for quote-path, ``order_draft`` for order-path).
        """
        stages = self.STAGES
        stop_at = stages.index(target_stage)
        seq: list[str] = []
        if with_opportunity or target_stage == "opportunity_created":
            seq.append("opportunity_created")
        opp_idx = stages.index("opportunity_created")
        if stop_at == opp_idx:
            return seq
        return seq + stages[opp_idx + 1: stop_at + 1]

    def remaining_steps(
        self,
        reached_stage: Optional[str],
        target_stage: str,
        with_opportunity: bool,
    ) -> list[str]:
        """Return the public stages still needed to reach ``target_stage``.

        Fresh run (``reached_stage is None``) -> full :meth:`stage_sequence`.
        Resumed run -> the slice after ``reached_stage`` up to and including
        ``target_stage``. Already at-or-past target -> empty list.
        """
        stages = self.STAGES
        if reached_stage is None:
            return self.stage_sequence(target_stage, with_opportunity)
        if stages.index(reached_stage) >= stages.index(target_stage):
            return []
        return stages[stages.index(reached_stage) + 1: stages.index(target_stage) + 1]

    # -- step graph dispatch -------------------------------------------------

    def _internal_step(self, public_stage: str) -> str:
        """Translate a public stage to the internal step registered in
        :data:`scripts.txn_data_harness.steps.STEP_REGISTRY`.

        Public stages that map 1:1 by name (every stage on the PST tail) can
        be omitted from :attr:`STEP_GRAPH`; only the order_draft variant has
        a real mapping today.
        """
        return self.STEP_GRAPH.get(public_stage, public_stage)

    # -- resolve / run -------------------------------------------------------

    def resolve(
        self, client: SfRestClient, ctx: OrgContext, spec: ScenarioSpec
    ) -> ResolvedSpec:
        # PST resolve is shared across quote-path and order-path: both bind
        # the same Account + product pool + term/end_date overrides. Live in
        # runner.resolve_spec until the order-path probe shows divergence.
        from .. import runner

        resolved = runner.resolve_spec(client, ctx, spec)
        # ResolvedSpec.effective_stage is computed by runner.resolve_spec
        # against the quote-path stage list. Re-stamp it through *this*
        # handler so an order-path subclass with a different STAGES set
        # caps correctly. No-op for quote-path.
        resolved.effective_stage = self.effective_stage(spec.target_stage, resolved.account)
        return resolved

    def run(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        run_id: str,
        resolved: ResolvedSpec,
        poll_timeout: int,
        max_retries: int,
        sleep=time.sleep,
    ) -> Manifest:
        """Drive one scenario end-to-end with checkpointed retries.

        Owns the retry loop: transient failures resume from the last
        checkpointed stage; deterministic failures fail fast. Public stages
        are mapped through :attr:`STEP_GRAPH` to internal step names before
        dispatch so the step registry can keep stable internal identifiers
        (e.g. ``order_from_quote`` vs ``order_direct``) independent of public
        stage naming.
        """
        from ..runner import current_run_id, draw_lines, draw_start_date

        current_run_id.set(run_id)

        lines = draw_lines(resolved.options)
        start_date = draw_start_date(resolved.start_date_range)
        target_stage = resolved.spec.target_stage
        with_opportunity = resolved.spec.with_opportunity

        manifest = Manifest(
            run_id=run_id,
            kind=self.kind,
            account_id=resolved.account.id,
            account_name=resolved.account.name,
            start_date=start_date.isoformat() if start_date is not None else None,
            lines=[line.to_manifest_record() for line in lines],
        )

        step_ctx = StepContext(
            client=client,
            org_context=ctx,
            run_id=run_id,
            account=resolved.account,
            lines=lines,
            with_opportunity=with_opportunity,
            poll_timeout=poll_timeout,
            start_date=start_date,
            checkpoint=write_manifest,
            target_stage=target_stage,
        )

        effective = self.effective_stage(target_stage, resolved.account)
        attempt = 0
        while True:
            attempt += 1
            manifest.attempts = attempt
            public_stages = self.remaining_steps(
                manifest.reached_stage, effective, with_opportunity
            )
            try:
                for public_stage in public_stages:
                    internal = self._internal_step(public_stage)
                    manifest = execute_step(internal, step_ctx, manifest)
                    write_manifest(manifest)
                manifest.error = None
                manifest.failure_class = None
                break
            except Exception as exc:  # noqa: BLE001 -- isolate one scenario's failure
                manifest.error = (
                    str(exc) if isinstance(exc, LifecycleError)
                    else f"{type(exc).__name__}: {exc}"
                )
                manifest.failure_class = classify_exception(exc)
                retryable = manifest.failure_class == "transient" and attempt <= max_retries
                log.error(
                    "scenario failed (attempt %d, %s%s): %s",
                    attempt, manifest.failure_class,
                    "; will retry" if retryable else "",
                    manifest.error,
                    exc_info=log.isEnabledFor(logging.DEBUG),
                )
                if not retryable:
                    break
                delay = _retry_backoff(attempt)
                log.warning(
                    "retrying scenario in %.0fs (attempt %d/%d)",
                    delay, attempt + 1, max_retries + 1,
                )
                write_manifest(manifest)
                sleep(delay)

        write_manifest(manifest)
        return manifest

    # -- summarize -----------------------------------------------------------

    def summarize(self, m: Manifest) -> dict[str, Any]:
        """Return the PST-shaped inspect/report summary for ``m``.

        Shared by both PST kinds. ``quote`` is included in the ids dict even
        for order-path manifests (where it is always None) so existing
        consumers in ``AI_TOOLS.md`` don't have to branch on kind.
        """
        from ..manifests import manifest_path

        return {
            "kind": m.kind,
            "run_id": m.run_id,
            "path": str(manifest_path(m.run_id)),
            "account": m.account_name or m.account_id,
            "reached_stage": m.reached_stage,
            "attempts": m.attempts,
            "failure_class": m.failure_class,
            "error": m.error,
            "start_date": m.start_date,
            "line_count": len(m.lines),
            "usage_journals": {
                "count": len(m.usage_journal_ids),
                "ids": m.usage_journal_ids[:5],
            },
            "ids": {
                "opportunity": m.opportunity_id,
                "quote": m.quote_id,
                "order": m.order_id,
                "billing_schedules": m.billing_schedule_ids,
                "assets": m.asset_ids,
                "invoice": m.invoice_id,
            },
            "invoice_order_link": {
                "status": m.invoice_order_link_status,
                "error": m.invoice_order_link_error,
            },
            "invoice_number": m.invoice_number,
        }
