"""Tests for plan/dry-run rendering in scripts.txn_data_harness.generate."""

from __future__ import annotations

from scripts.txn_data_harness.config import ProductOption, ScenarioSpec
from scripts.txn_data_harness.discovery import Account, Product
from scripts.txn_data_harness.generate import _print_pst_spec
from scripts.txn_data_harness.models import ResolvedOption, ResolvedSpec


def _resolved(kind: str, target_stage: str, effective_stage: str) -> ResolvedSpec:
    account = Account(id="001ACC", name="Infinitech", billing_account_id="ba1")
    product = Product(
        id="01tP", name="Cloud License", sku="QB-LIC-CLOUD",
        pricebook_entry_id="01uPBE", unit_price=100.0,
    )
    spec = ScenarioSpec(
        account="Infinitech",
        products=[ProductOption(sku="QB-LIC-CLOUD", quantity=(1, 1))],
        target_stage=target_stage,
        with_opportunity=False,
        opportunity_stage=None,
        count=1,
        kind=kind,
    )
    option = ResolvedOption(product=product, quantity=(1, 1), discount=None)
    return ResolvedSpec(
        spec=spec, account=account, options=[option], effective_stage=effective_stage,
    )


def test_direct_order_plan_includes_order_draft_head(capsys) -> None:
    """``sales_txn_order`` STAGES starts with ``order_draft`` (no
    ``opportunity_created`` head); the plan listing must include the
    direct-order placement step rather than skipping to ``order_activated``."""
    r = _resolved("sales_txn_order", "order_activated", "order_activated")
    _print_pst_spec(r, 0, 1)
    out = capsys.readouterr().out
    stages_line = next(ln for ln in out.splitlines() if "Stages" in ln)
    assert "order_draft" in stages_line
    assert "order_activated" in stages_line


def test_quote_plan_skips_opportunity_head_by_default(capsys) -> None:
    """The quote path still drops the leading ``opportunity_created`` head when
    the scenario didn't opt into an Opportunity -- head is ``quote_placed``."""
    r = _resolved("sales_txn_quote", "invoice_posted", "invoice_posted")
    _print_pst_spec(r, 0, 1)
    out = capsys.readouterr().out
    stages_line = next(ln for ln in out.splitlines() if "Stages" in ln)
    assert "quote_placed" in stages_line
    assert "opportunity_created" not in stages_line
