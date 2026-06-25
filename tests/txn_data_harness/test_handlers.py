"""Tests for the scenario-handler-per-kind refactor (PR 1).

These tests pin the new dispatch surface to behavior that already exists in
``runner.py`` so the refactor is a *pure* refactor:

* the ``SalesTransactionHandler.STEP_GRAPH`` agrees with ``stage_sequence`` for
  every target stage, with and without an Opportunity head;
* ``ScenarioSpec`` and ``Manifest`` default ``kind`` to ``sales_txn_quote``
  and round-trip the discriminator;
* ``load_manifest`` rejects on-disk manifests without ``kind`` (loud failure,
  per the rollout note in :func:`load_manifest`);
* an unknown ``kind`` is rejected at config parse time.
"""

from __future__ import annotations

import json

import pytest

from scripts.txn_data_harness.config import ConfigError, _coerce_spec
from scripts.txn_data_harness.handlers import (
    SCENARIO_HANDLERS,
    SalesTransactionHandler,
)
from scripts.txn_data_harness.handlers.sales_transaction import STEP_GRAPH
from scripts.txn_data_harness.manifests import (
    load_manifest,
    summarize_manifest,
    write_manifest,
)
from scripts.txn_data_harness.models import Manifest
from scripts.txn_data_harness.runner import stage_sequence


def test_sales_txn_quote_handler_registered() -> None:
    handler = SCENARIO_HANDLERS["sales_txn_quote"]
    assert isinstance(handler, SalesTransactionHandler)
    assert handler.kind == "sales_txn_quote"


@pytest.mark.parametrize(
    "target_stage",
    ["opportunity_created", "quote_placed", "order_draft", "order_activated", "usage_upload", "invoice_draft", "invoice_posted"],
)
@pytest.mark.parametrize("with_opportunity", [False, True])
def test_step_graph_matches_stage_sequence(
    target_stage: str, with_opportunity: bool
) -> None:
    """The handler's static STEP_GRAPH must agree with the runner's
    stage_sequence for every target stage (with and without an Opportunity head).
    If these drift the refactor would silently reorder steps."""
    handler = SalesTransactionHandler()
    expected = stage_sequence(target_stage, with_opportunity=with_opportunity)
    # Static map skips the opportunity head (it's flag-driven), so prepend it
    # ourselves when with_opportunity is True or target is 'opportunity_created'.
    static = list(STEP_GRAPH[target_stage])
    if with_opportunity and target_stage != "opportunity_created" and static[0] != "opportunity_created":
        static = ["opportunity_created"] + static
    assert static == expected
    # And the handler method (which delegates to runner.stage_sequence) must
    # produce the same answer end-to-end.
    assert handler.stage_sequence(target_stage, with_opportunity) == expected


def test_scenario_spec_defaults_to_sales_txn_quote_kind() -> None:
    spec = _coerce_spec({"account": "Infinitech"}, "test")
    assert spec.kind == "sales_txn_quote"


def test_scenario_spec_accepts_explicit_kind() -> None:
    spec = _coerce_spec(
        {"account": "Infinitech", "kind": "sales_txn_quote"}, "test"
    )
    assert spec.kind == "sales_txn_quote"


def test_scenario_spec_rejects_unknown_kind() -> None:
    with pytest.raises(ConfigError, match="invalid kind 'bogus'"):
        _coerce_spec({"account": "Infinitech", "kind": "bogus"}, "test")


def test_transaction_kind_error_suggests_sales_txn_quote() -> None:
    with pytest.raises(ConfigError, match="use 'sales_txn_quote'"):
        _coerce_spec({"account": "Infinitech", "kind": "transaction"}, "test")


def test_legacy_sales_transaction_kind_error() -> None:
    with pytest.raises(ConfigError, match="renamed to 'sales_txn_quote'"):
        _coerce_spec({"account": "Infinitech", "kind": "sales_transaction"}, "test")


def test_manifest_defaults_kind_to_sales_txn_quote() -> None:
    assert Manifest(run_id="DEMO-K").kind == "sales_txn_quote"


def test_manifest_kind_roundtrips_through_disk(tmp_path) -> None:
    original = Manifest(run_id="DEMO-K", kind="sales_txn_quote")
    write_manifest(original, manifest_dir=tmp_path)
    loaded = load_manifest("DEMO-K", manifest_dir=tmp_path)
    assert loaded.kind == "sales_txn_quote"


def test_load_manifest_rejects_missing_kind(tmp_path) -> None:
    path = tmp_path / "DEMO-NO-KIND.json"
    path.write_text(json.dumps({"run_id": "DEMO-NO-KIND"}))
    with pytest.raises(ValueError, match="missing required 'kind' discriminator"):
        load_manifest("DEMO-NO-KIND", manifest_dir=tmp_path)


def test_summarize_manifest_surfaces_kind() -> None:
    summary = summarize_manifest(Manifest(run_id="DEMO-K"))
    assert summary["kind"] == "sales_txn_quote"
