"""Scenario handler protocol.

A handler owns the parse/discover/resolve/run pipeline for one ``kind`` of
scenario (today: ``sales_txn_quote``, ``sales_txn_order``, and
``invoice_ingestion``). The
dispatcher in ``generate.py`` / ``cli.py`` looks up
``SCENARIO_HANDLERS[merged["kind"]]`` after the defaults merge and delegates
through this protocol so each lifecycle stays in its own module instead of
spreading conditionals across the harness.
"""

from __future__ import annotations

from typing import Any, ClassVar, Optional, Protocol, runtime_checkable

from ..auth import SfRestClient
from ..discovery import Account, OrgContext
from ..models import Manifest


@runtime_checkable
class ScenarioHandler(Protocol):
    """Per-``kind`` entry points the dispatcher calls into.

    Implementations are stateless singletons registered in
    ``handlers/__init__.py`` as ``SCENARIO_HANDLERS[kind]``. The ``spec``
    and ``resolved`` types vary by kind (PST uses
    :class:`scripts.txn_data_harness.config.ScenarioSpec` /
    :class:`scripts.txn_data_harness.models.ResolvedSpec`; ingestion uses
    :class:`scripts.txn_data_harness.config.InvoiceIngestionScenarioSpec` /
    :class:`scripts.txn_data_harness.models.ResolvedInvoiceIngestionSpec`),
    so the protocol leaves them as ``Any`` and each handler narrows the
    types on its own ``resolve`` / ``run`` signatures.
    """

    kind: ClassVar[str]

    def effective_stage(self, target_stage: str, account: Account) -> str:
        """Resolve the stage a scenario will actually reach.

        Implementations may cap the requested stage on this kind's rules
        (e.g. PST caps at ``order`` for non-billing accounts; ingestion
        has no cap).
        """
        ...

    def stage_sequence(self, target_stage: str, with_opportunity: bool) -> list[str]:
        """Ordered list of step names this kind runs to reach ``target_stage``."""
        ...

    def remaining_steps(
        self, reached_stage: Optional[str], target_stage: str, with_opportunity: bool
    ) -> list[str]:
        """Steps still needed to reach ``target_stage`` from a checkpointed run."""
        ...

    def resolve(self, client: SfRestClient, ctx: OrgContext, spec: Any) -> Any:
        """Bind a parsed spec's account/lines to concrete org records."""
        ...

    def run(
        self,
        client: SfRestClient,
        ctx: OrgContext,
        run_id: str,
        resolved: Any,
        poll_timeout: int,
        max_retries: int,
    ) -> Manifest:
        """Drive one scenario through this kind's lifecycle."""
        ...


def settlement_summary(m: Manifest) -> Optional[dict[str, Any]]:
    """Settlement block of an inspect/report summary; ``None`` before settlement.

    Shared by every kind so ``credit_applied`` / ``payment_applied`` read the
    same way whichever lifecycle produced the invoice.
    """
    if not (m.application_level or m.credit_memo_ids or m.payment_ids or m.settlement_warnings):
        return None
    return {
        "application_level": m.application_level,
        "application_level_source": m.application_level_source,
        "baseline": m.settlement_baseline,
        "credit": {
            "memo_ids": m.credit_memo_ids,
            "application_ids": m.credit_application_ids,
            "requested": m.credit_amount_requested,
            "applied": m.credit_amount_applied,
            "submitted": m.credit_submitted,
            "baseline": m.credit_baseline,
        },
        "payment": {
            "ids": m.payment_ids,
            "application_ids": m.payment_application_ids,
            "amount": m.payment_amount,
            "planned_apply": m.payment_apply_target,
            "applied": m.payment_amount_applied,
            "mode": m.payment_mode,
        },
        "invoice_balance": m.invoice_balance,
        "warnings": m.settlement_warnings,
    }
