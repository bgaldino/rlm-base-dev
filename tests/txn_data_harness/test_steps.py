"""Tests for composable lifecycle step handlers."""

from __future__ import annotations

import pytest

from scripts.txn_data_harness.lifecycle import AssetPollResult, LifecycleError
from scripts.txn_data_harness.models import LineItem, Manifest
from scripts.txn_data_harness.steps import (
    StepContext,
    execute_step,
    run_activate,
    run_post,
    run_quote,
)


def _ctx(fake_client, org_context, billable_account, term_product, checkpoint=None) -> StepContext:
    return StepContext(
        client=fake_client,
        org_context=org_context,
        run_id="DEMO-1",
        account=billable_account,
        lines=[LineItem(product=term_product, quantity=1)],
        with_opportunity=False,
        poll_timeout=1,
        checkpoint=checkpoint,
    )


def test_run_quote_updates_manifest(monkeypatch, fake_client, org_context, billable_account, term_product) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.place_sales_transaction",
        lambda *_args, **_kwargs: "0Q0QUOTE",
    )
    manifest = run_quote(_ctx(fake_client, org_context, billable_account, term_product), Manifest(run_id="DEMO-1"))
    assert manifest.quote_id == "0Q0QUOTE"
    assert manifest.reached_stage == "quote"


def test_run_quote_checkpoints_partial_quote_id_on_failure(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    checkpoints = []

    def fail_place(*_args, **_kwargs):
        raise LifecycleError("quote", "PST failed", record_id="0Q0PARTIAL")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.place_sales_transaction",
        fail_place,
    )
    manifest = Manifest(run_id="DEMO-1")
    with pytest.raises(LifecycleError):
        run_quote(
            _ctx(fake_client, org_context, billable_account, term_product, checkpoints.append),
            manifest,
        )
    assert manifest.quote_id == "0Q0PARTIAL"
    assert checkpoints and checkpoints[0].quote_id == "0Q0PARTIAL"


def test_execute_step_rejects_unknown_step(fake_client, org_context, billable_account, term_product) -> None:
    with pytest.raises(LifecycleError, match="unknown lifecycle step"):
        execute_step(
            "not-a-step",
            _ctx(fake_client, org_context, billable_account, term_product),
            Manifest(run_id="DEMO-1"),
        )


def test_order_step_requires_quote_id(fake_client, org_context, billable_account, term_product) -> None:
    with pytest.raises(LifecycleError, match="quote_id is required"):
        execute_step(
            "order",
            _ctx(fake_client, org_context, billable_account, term_product),
            Manifest(run_id="DEMO-1"),
        )


def test_activate_step_requires_order_id(fake_client, org_context, billable_account, term_product) -> None:
    with pytest.raises(LifecycleError, match="order_id is required"):
        execute_step(
            "activate",
            _ctx(fake_client, org_context, billable_account, term_product),
            Manifest(run_id="DEMO-1"),
        )


def test_run_activate_uses_order_item_count_for_bs_and_order_id_for_assets(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    """Bundle case: one input LineItem expands into many OrderItems on the
    order. ``run_activate`` must derive the BS poll's ``expected_count`` from
    the OrderItem count (not ``len(ctx.lines)``), and pass the manifest's
    ``order_id`` to ``poll_assets`` so the AssetActionSource path can
    attribute every bundle-expanded asset back to this order.
    """
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.set_shipping_address",
        lambda *_a, **_kw: None,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.activate_order",
        lambda *_a, **_kw: None,
    )

    def fake_count(_client, order_id):
        assert order_id == "801ORDER"
        return 7  # bundle expanded to seven OrderItems

    def fake_bs(_client, _order_id, expected_count, timeout, **_kwargs):
        captured["bs_expected"] = expected_count
        return [f"BS-{i}" for i in range(expected_count)]

    def fake_assets(_client, order_id, timeout):
        captured["assets_order_id"] = order_id
        return AssetPollResult([f"A-{i}" for i in range(5)], "converged")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.count_order_items", fake_count
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.poll_billing_schedules", fake_bs
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.poll_assets", fake_assets
    )

    ctx = _ctx(fake_client, org_context, billable_account, term_product)
    # One input line (the bundle root) on the scenario, even though the
    # server-side bundle expansion produced seven OrderItems.
    assert len(ctx.lines) == 1
    manifest = Manifest(run_id="DEMO-1", order_id="801ORDER")

    run_activate(ctx, manifest)

    assert captured == {"bs_expected": 7, "assets_order_id": "801ORDER"}
    assert len(manifest.billing_schedule_ids) == 7
    assert len(manifest.asset_ids) == 5
    assert manifest.reached_stage == "activate"


def test_run_activate_does_not_mark_stage_when_billing_poll_fails(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.set_shipping_address",
        lambda *_a, **_kw: None,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.count_order_items",
        lambda *_a, **_kw: 1,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.activate_order",
        lambda *_a, **_kw: None,
    )

    def fail_billing_poll(*_a, **_kw):
        raise LifecycleError("billing_schedule", "request timed out")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.poll_billing_schedules",
        fail_billing_poll,
    )

    manifest = Manifest(run_id="DEMO-1", reached_stage="order", order_id="801ORDER")
    with pytest.raises(LifecycleError, match="request timed out"):
        run_activate(
            _ctx(fake_client, org_context, billable_account, term_product),
            manifest,
        )

    assert manifest.reached_stage == "order"
    assert manifest.billing_schedule_ids == []


def test_run_activate_does_not_mark_stage_when_asset_poll_hard_fails(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.set_shipping_address",
        lambda *_a, **_kw: None,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.count_order_items",
        lambda *_a, **_kw: 1,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.activate_order",
        lambda *_a, **_kw: None,
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.poll_billing_schedules",
        lambda *_a, **_kw: ["BS-1"],
    )

    def fail_asset_poll(*_a, **_kw):
        raise LifecycleError("activate", "request timed out")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.poll_assets",
        fail_asset_poll,
    )

    manifest = Manifest(run_id="DEMO-1", reached_stage="order", order_id="801ORDER")
    with pytest.raises(LifecycleError, match="request timed out"):
        run_activate(
            _ctx(fake_client, org_context, billable_account, term_product),
            manifest,
        )

    assert manifest.reached_stage == "order"
    assert manifest.billing_schedule_ids == ["BS-1"]
    assert manifest.asset_ids == []


def test_post_step_requires_invoice_id(fake_client, org_context, billable_account, term_product) -> None:
    with pytest.raises(LifecycleError, match="invoice_id is required"):
        execute_step(
            "post",
            _ctx(fake_client, org_context, billable_account, term_product),
            Manifest(run_id="DEMO-1"),
        )


def test_run_post_records_optional_order_link_failure(
    monkeypatch, fake_client, org_context, billable_account, term_product
) -> None:
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.post_invoice",
        lambda *_a, **_kw: "INV-1",
    )

    def fail_link(*_a, **_kw):
        raise LifecycleError("post", "request timed out")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.link_invoice_to_order",
        fail_link,
    )

    manifest = Manifest(run_id="DEMO-1", invoice_id="INV-ID", order_id="801ORDER")
    run_post(_ctx(fake_client, org_context, billable_account, term_product), manifest)

    assert manifest.reached_stage == "post"
    assert manifest.invoice_number == "INV-1"
    assert manifest.invoice_order_link_status == "failed"
    assert "request timed out" in (manifest.invoice_order_link_error or "")
