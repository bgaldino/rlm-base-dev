"""Tests for composable lifecycle step handlers."""

from __future__ import annotations

import pytest

from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import LineItem, Manifest
from scripts.txn_data_harness.steps import StepContext, execute_step, run_quote


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


def test_post_step_requires_invoice_id(fake_client, org_context, billable_account, term_product) -> None:
    with pytest.raises(LifecycleError, match="invoice_id is required"):
        execute_step(
            "post",
            _ctx(fake_client, org_context, billable_account, term_product),
            Manifest(run_id="DEMO-1"),
        )
