"""Tests for the run_usage step handler."""

from __future__ import annotations

import pytest

from scripts.txn_data_harness.discovery import Product
from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import (
    LineItem,
    Manifest,
    ResolvedUsageSpec,
    ResolvedUsageTarget,
)
from scripts.txn_data_harness.steps import StepContext, run_usage


def _usage_line(product: Product) -> LineItem:
    return LineItem(
        product=product,
        quantity=1,
        usage=ResolvedUsageSpec(
            quantity=(100.0, 100.0),
            records_per_line=(2, 2),
            days_back=0,
            targets=[
                ResolvedUsageTarget(
                    resource_id="RES-1",
                    resource_code="UR-1",
                    uom_id="UOM-1",
                    uom_code="TB",
                ),
            ],
        ),
    )


def _ctx(fake_client, org_context, billable_account, lines) -> StepContext:
    return StepContext(
        client=fake_client,
        org_context=org_context,
        run_id="DEMO-1",
        account=billable_account,
        lines=lines,
        with_opportunity=False,
        poll_timeout=1,
    )


def test_run_usage_skips_when_no_lines_opt_in(
    fake_client, org_context, billable_account, term_product
) -> None:
    ctx = _ctx(
        fake_client, org_context, billable_account,
        [LineItem(product=term_product, quantity=1)],
    )
    manifest = Manifest(run_id="DEMO-1", asset_ids=["02iAAA"])
    out = run_usage(ctx, manifest)
    assert out.reached_stage == "usage"
    assert out.usage_journal_ids == []
    assert fake_client.posts == []
    assert fake_client.queries == []


def test_run_usage_hard_fails_when_no_asset_for_line(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.fetch_assets_product_ids",
        lambda *_a, **_k: {},  # no asset->product mapping
    )
    ctx = _ctx(
        fake_client, org_context, billable_account,
        [_usage_line(term_product)],
    )
    manifest = Manifest(run_id="DEMO-1", asset_ids=["02iAAA"])
    with pytest.raises(LifecycleError, match="no asset found for usage line"):
        run_usage(ctx, manifest)


def test_run_usage_hard_fails_when_manifest_has_no_assets(
    fake_client, org_context, billable_account, term_product
) -> None:
    ctx = _ctx(
        fake_client, org_context, billable_account,
        [_usage_line(term_product)],
    )
    manifest = Manifest(run_id="DEMO-1", asset_ids=[])
    with pytest.raises(LifecycleError, match="no asset_ids on manifest"):
        run_usage(ctx, manifest)


def test_run_usage_pairs_duplicate_skus_one_to_one(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    """Two lines with the same SKU consume two distinct assets, in order."""
    calls: list[tuple[str, str]] = []

    def fake_create(_client, asset_id, account_id, line, run_id, *, now=None):
        calls.append((asset_id, line.product.sku))
        return [f"TJ-{asset_id}"]

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.fetch_assets_product_ids",
        lambda *_a, **_k: {"02iAAA": term_product.id, "02iBBB": term_product.id},
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.create_usage_journals",
        fake_create,
    )
    ctx = _ctx(
        fake_client, org_context, billable_account,
        [_usage_line(term_product), _usage_line(term_product)],
    )
    manifest = Manifest(run_id="DEMO-1", asset_ids=["02iAAA", "02iBBB"])
    out = run_usage(ctx, manifest)

    assert sorted(out.usage_journal_ids) == ["TJ-02iAAA", "TJ-02iBBB"]
    paired_assets = sorted(asset_id for asset_id, _ in calls)
    assert paired_assets == ["02iAAA", "02iBBB"]
    assert out.reached_stage == "usage"


def test_run_usage_populates_journal_ids_and_reached_stage(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.fetch_assets_product_ids",
        lambda *_a, **_k: {"02iAAA": term_product.id},
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.create_usage_journals",
        lambda *_a, **_k: ["TJ-1", "TJ-2"],
    )
    ctx = _ctx(
        fake_client, org_context, billable_account,
        [_usage_line(term_product)],
    )
    manifest = Manifest(run_id="DEMO-1", asset_ids=["02iAAA"])
    out = run_usage(ctx, manifest)
    assert out.usage_journal_ids == ["TJ-1", "TJ-2"]
    assert out.reached_stage == "usage"
