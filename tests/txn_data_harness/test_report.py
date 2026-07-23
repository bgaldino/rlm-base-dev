"""Tests for batch report assembly."""

from __future__ import annotations

from scripts.txn_data_harness.manifests import summarize_manifest
from scripts.txn_data_harness.models import Manifest
from scripts.txn_data_harness.report import build_batch_report, render_markdown


def _ok(run_id: str, stage: str = "invoice_posted", kind: str = "sales_txn_quote") -> Manifest:
    return Manifest(run_id=run_id, kind=kind, reached_stage=stage)


def _failed(
    run_id: str,
    stage: str,
    cls: str,
    error: str,
    attempts: int = 1,
    kind: str = "sales_txn_quote",
) -> Manifest:
    return Manifest(
        run_id=run_id, kind=kind, reached_stage=stage, error=error,
        failure_class=cls, attempts=attempts,
    )


def test_build_batch_report_counts_and_histogram() -> None:
    manifests = [
        _ok("R-1", "invoice_posted"),
        _ok("R-2", "invoice_posted"),
        _failed("R-3", "order_draft", "transient", "timed out", attempts=3),
        _failed("R-4", "quote_placed", "deterministic", "INVALID_FIELD: x"),
    ]
    report = build_batch_report(manifests, base_run_id="DEMO-X")

    assert report["base_run_id"] == "DEMO-X"
    assert report["total"] == 4
    assert report["succeeded"] == 2
    assert report["failed"] == 2
    assert report["retried"] == 1

    pst = report["stage_histogram_by_kind"]["sales_txn_quote"]
    assert pst["invoice_posted"] == 2
    assert pst["order_draft"] == 1
    assert pst["quote_placed"] == 1


def test_failure_signature_rollup_groups_same_signature() -> None:
    manifests = [
        _failed("R-1", "order_draft", "transient", "request timed out"),
        _failed("R-2", "order_draft", "transient", "request timed out"),
        _failed("R-3", "quote_placed", "deterministic", "INVALID_FIELD: x"),
    ]
    report = build_batch_report(manifests)
    sigs = report["failure_signatures"]

    # Most-frequent first: the doubled transient timeout leads.
    assert sigs[0]["count"] == 2
    assert sorted(sigs[0]["run_ids"]) == ["R-1", "R-2"]
    assert sigs[0]["signature"].startswith("transient:")
    assert sigs[1]["count"] == 1


def test_none_reached_stage_buckets_under_none() -> None:
    report = build_batch_report([Manifest(run_id="R-1", kind="sales_txn_quote")])
    assert report["stage_histogram_by_kind"]["sales_txn_quote"]["(none)"] == 1


def test_render_markdown_includes_signatures() -> None:
    report = build_batch_report(
        [_failed("R-1", "order_draft", "transient", "timed out")], base_run_id="DEMO-X"
    )
    md = render_markdown(report)
    assert "# Batch report — DEMO-X" in md
    assert "Failure signatures" in md
    assert "R-1" in md


def test_report_surfaces_poll_and_link_warnings() -> None:
    manifest = Manifest(
        run_id="R-1",
        kind="sales_txn_quote",
        reached_stage="invoice_posted",
        asset_poll_status="timeout_partial",
        invoice_order_link_status="failed",
        invoice_order_link_error="[post] request timed out",
    )
    report = build_batch_report([manifest])

    assert report["poll_warnings"] == [
        {"run_id": "R-1", "status": "timeout_partial"}
    ]
    assert report["link_warnings"] == [
        {
            "run_id": "R-1",
            "status": "failed",
            "error": "[post] request timed out",
        }
    ]

    md = render_markdown(report)
    assert "Poll warnings" in md
    assert "Link warnings" in md
    assert "request timed out" in md


def test_render_markdown_includes_unknown_stage_buckets() -> None:
    report = build_batch_report([
        Manifest(run_id="R-1", kind="sales_txn_quote", reached_stage="mystery")
    ])

    md = render_markdown(report)
    assert "- mystery: 1 (unknown)" in md


# ---------------------------------------------------------------------------
# Mixed-kind report shape (PR 5)
# ---------------------------------------------------------------------------


def test_mixed_kind_report_kind_histogram() -> None:
    """A batch with both kinds reports a kind_histogram split."""
    manifests = [
        _ok("R-1", "invoice_posted", kind="sales_txn_quote"),
        _ok("R-2", "invoice_posted", kind="sales_txn_quote"),
        _ok("R-3", "invoice_posted", kind="invoice_ingestion"),
        _ok("R-4", "invoice_posted", kind="invoice_ingestion"),
        _ok("R-5", "invoice_draft", kind="invoice_ingestion"),
    ]
    report = build_batch_report(manifests, base_run_id="MIXED")
    # kind_histogram seeds a zero bucket for every registered kind so a clean
    # report still announces empty kinds. ``sales_txn_order`` joined the
    # registry in Phase 3 but isn't exercised by this batch.
    assert report["kind_histogram"] == {
        "sales_txn_quote": 2,
        "sales_txn_order": 0,
        "invoice_ingestion": 3,
    }


def test_mixed_kind_stage_histogram_isolates_kinds() -> None:
    """The ingestion stage bucket must not include PST-only stages.

    Guards against the regression where ``stage_histogram`` was a single dict
    keyed by stage name; a Draft-ingested invoice would have been double-
    counted under PST's ``invoice_draft`` bucket.
    """
    manifests = [
        _ok("R-1", "invoice_draft", kind="invoice_ingestion"),
        _ok("R-2", "invoice_posted", kind="invoice_ingestion"),
        _ok("R-3", "invoice_posted", kind="sales_txn_quote"),
        _ok("R-4", "order_draft", kind="sales_txn_quote"),
    ]
    report = build_batch_report(manifests)
    ingestion = report["stage_histogram_by_kind"]["invoice_ingestion"]

    # Ingestion only ever reaches invoice_draft or invoice_posted (plus the "(none)" catch-all).
    assert set(ingestion) == {"invoice_draft", "invoice_posted", "(none)"}
    assert ingestion["invoice_draft"] == 1
    assert ingestion["invoice_posted"] == 1

    pst = report["stage_histogram_by_kind"]["sales_txn_quote"]
    assert pst["invoice_posted"] == 1
    assert pst["order_draft"] == 1
    # PST stage allowlist includes all seven stages plus "(none)".
    assert set(pst) >= {"opportunity_created", "quote_placed", "order_draft", "order_activated", "usage_upload", "invoice_draft", "invoice_posted", "(none)"}


def test_render_markdown_groups_by_kind() -> None:
    manifests = [
        _ok("R-1", "invoice_posted", kind="sales_txn_quote"),
        _ok("R-2", "invoice_posted", kind="invoice_ingestion"),
    ]
    md = render_markdown(build_batch_report(manifests, base_run_id="MIXED"))
    assert "## Sales transaction (Quote) — stages reached" in md
    assert "## Invoice ingestion — stages reached" in md
    # Each section's bullet should appear under its own header.
    assert "## Kinds" in md
    assert "Sales transaction (Quote): 1" in md
    assert "Invoice ingestion: 1" in md


# ---------------------------------------------------------------------------
# Handler-dispatched summarize_manifest (PR 5)
# ---------------------------------------------------------------------------


def test_summarize_pst_manifest_keeps_legacy_keys() -> None:
    """A PST manifest still exposes the pre-handler-dispatch shape so
    inspect/report consumers don't regress."""
    m = Manifest(
        run_id="R-1",
        kind="sales_txn_quote",
        account_name="Infinitech",
        opportunity_id="006xx0000001",
        quote_id="0Q0xx0000001",
        order_id="801xx0000001",
        billing_schedule_ids=["b1"],
        asset_ids=["a1"],
        invoice_id="inv-1",
        invoice_number="INV-1",
        reached_stage="invoice_posted",
        start_date="2026-01-01",
        lines=[{"sku": "QB-API-FLEX", "quantity": 1}],
    )
    summary = summarize_manifest(m)
    assert summary["kind"] == "sales_txn_quote"
    assert summary["account"] == "Infinitech"
    assert summary["ids"]["opportunity"] == "006xx0000001"
    assert summary["ids"]["quote"] == "0Q0xx0000001"
    assert summary["ids"]["order"] == "801xx0000001"
    assert summary["ids"]["billing_schedules"] == ["b1"]
    assert summary["ids"]["assets"] == ["a1"]
    assert summary["invoice_number"] == "INV-1"
    assert summary["start_date"] == "2026-01-01"
    assert summary["line_count"] == 1
    assert "usage_journals" in summary


def test_summarize_ingestion_manifest_drops_pst_keys() -> None:
    """An ingestion manifest must not surface PST-shaped ids."""
    m = Manifest(
        run_id="R-2",
        kind="invoice_ingestion",
        account_name="Global Media",
        invoice_id="inv-2",
        invoice_number="INV-2",
        invoice_line_ids=["il-1", "il-2"],
        creation_mode="External",
        reached_stage="invoice_posted",
        lines=[{"name": "API", "quantity": 5, "unit_price": 100}],
    )
    summary = summarize_manifest(m)
    assert summary["kind"] == "invoice_ingestion"
    assert summary["account"] == "Global Media"
    assert summary["creation_mode"] == "External"
    assert summary["ids"] == {
        "invoice": "inv-2",
        "invoice_lines": ["il-1", "il-2"],
    }
    # PST-shaped keys must NOT leak into the ingestion summary.
    assert "opportunity" not in summary["ids"]
    assert "quote" not in summary["ids"]
    assert "order" not in summary["ids"]
    assert "billing_schedules" not in summary["ids"]
    assert "assets" not in summary["ids"]
    assert "usage_journals" not in summary
    assert "start_date" not in summary


def test_summarize_rejects_unknown_kind() -> None:
    """Loading a manifest stamped with an unknown kind should fail loud."""
    import pytest

    m = Manifest(run_id="R-X", kind="something_else", reached_stage=None)
    with pytest.raises(ValueError, match="unknown kind"):
        summarize_manifest(m)
