"""Sales-transaction (PST via Quote) scenario handler.

Wraps today's PST parse/resolve/run logic into a handler so the
``invoice_ingestion`` handler has a peer. No behavioral change: each
method delegates to the existing free function in ``runner.py``.

The step graph is the canonical PST-via-Quote lifecycle:

    opportunity_created -> quote_placed -> order_draft -> order_activated
    -> usage_upload -> invoice_draft -> invoice_posted

with ``opportunity_created`` prepended only when ``with_opportunity=True``
or the target stage is ``opportunity_created`` itself.
"""

from __future__ import annotations

from typing import ClassVar, Optional

from typing import Any

from .. import runner
from ..auth import SfRestClient
from ..config import ScenarioSpec
from ..discovery import Account, OrgContext
from ..models import STAGES_QUOTE, Manifest, ResolvedSpec
from ..runner import draw_lines, draw_start_date


# Canonical PST step graph keyed by target stage. Generated from the same
# sequencing helper used by the runner so stage ordering has one source of
# truth (``models.STAGES_QUOTE`` + ``runner.stage_sequence``).
STEP_GRAPH: dict[str, list[str]] = {
    stage: runner.stage_sequence(stage, with_opportunity=False)
    for stage in STAGES_QUOTE
}


class SalesTransactionHandler:
    """PST handler: drives Opportunity -> Quote -> Order -> Activate -> Usage
    -> Invoice -> Post. Implements the ``ScenarioHandler`` protocol.
    """

    kind: ClassVar[str] = "sales_txn_quote"

    def effective_stage(self, target_stage: str, account: Account) -> str:
        return runner.effective_stage(target_stage, account)

    def stage_sequence(self, target_stage: str, with_opportunity: bool) -> list[str]:
        return runner.stage_sequence(target_stage, with_opportunity)

    def remaining_steps(
        self, reached_stage: Optional[str], target_stage: str, with_opportunity: bool
    ) -> list[str]:
        return runner.remaining_steps(reached_stage, target_stage, with_opportunity)

    def resolve(
        self, client: SfRestClient, ctx: OrgContext, spec: ScenarioSpec
    ) -> ResolvedSpec:
        return runner.resolve_spec(client, ctx, spec)

    def run(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        run_id: str,
        resolved: ResolvedSpec,
        poll_timeout: int,
        max_retries: int,
    ) -> Manifest:
        return runner.run_scenario(
            client=client,
            ctx=ctx,
            run_id=run_id,
            target_stage=resolved.spec.target_stage,
            account=resolved.account,
            lines=draw_lines(resolved.options),
            with_opportunity=resolved.spec.with_opportunity,
            poll_timeout=poll_timeout,
            start_date=draw_start_date(resolved.start_date_range),
            max_retries=max_retries,
        )

    def summarize(self, m: Manifest) -> dict[str, Any]:
        """Return the PST-shaped inspect/report summary for ``m``.

        Matches the pre-handler-dispatch shape of ``summarize_manifest`` for
        backward compatibility: existing inspect/report consumers (the AI
        tools described in ``AI_TOOLS.md``) read these keys and a regression
        here would silently break them. The parity test in
        ``test_sales_transaction_handler.py`` pins the dict shape.
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
