"""Sales-transaction (PST) scenario handler.

Wraps today's PST parse/resolve/run logic into a handler so the
``invoice_ingestion`` handler (PR 2+) has a peer. No behavioral change: each
method delegates to the existing free function in ``runner.py``.

The step graph is the canonical PST lifecycle:

    opportunity -> quote -> order -> activate -> usage -> invoice -> post

with ``opportunity`` prepended only when ``with_opportunity=True`` or the
target stage is ``opportunity`` itself.
"""

from __future__ import annotations

from typing import ClassVar, Optional

from .. import runner
from ..auth import SfRestClient
from ..config import ScenarioSpec
from ..discovery import Account, OrgContext
from ..models import Manifest, ResolvedSpec
from ..runner import draw_lines, draw_start_date


# Canonical PST step graph keyed by target stage. Kept in sync with
# ``models.STAGES`` -- the parity test in tests/txn_data_harness/test_handlers.py
# asserts that ``stage_sequence(target, with_opportunity=False)`` agrees with
# slicing ``STAGES`` up to the target index.
STEP_GRAPH: dict[str, list[str]] = {
    "opportunity": ["opportunity"],
    "quote":       ["quote"],
    "order":       ["quote", "order"],
    "activate":    ["quote", "order", "activate"],
    "usage":       ["quote", "order", "activate", "usage"],
    "invoice":     ["quote", "order", "activate", "usage", "invoice"],
    "post":        ["quote", "order", "activate", "usage", "invoice", "post"],
}


class SalesTransactionHandler:
    """PST handler: drives Opportunity -> Quote -> Order -> Activate -> Usage
    -> Invoice -> Post. Implements the ``ScenarioHandler`` protocol.
    """

    kind: ClassVar[str] = "sales_transaction"

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
