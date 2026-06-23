"""Tests for batch report assembly."""

from __future__ import annotations

from scripts.txn_data_harness.models import Manifest
from scripts.txn_data_harness.report import build_batch_report, render_markdown


def _ok(run_id: str, stage: str = "post") -> Manifest:
    return Manifest(run_id=run_id, reached_stage=stage)


def _failed(run_id: str, stage: str, cls: str, error: str, attempts: int = 1) -> Manifest:
    return Manifest(
        run_id=run_id, reached_stage=stage, error=error,
        failure_class=cls, attempts=attempts,
    )


def test_build_batch_report_counts_and_histogram() -> None:
    manifests = [
        _ok("R-1", "post"),
        _ok("R-2", "post"),
        _failed("R-3", "order", "transient", "timed out", attempts=3),
        _failed("R-4", "quote", "deterministic", "INVALID_FIELD: x"),
    ]
    report = build_batch_report(manifests, base_run_id="DEMO-X")

    assert report["base_run_id"] == "DEMO-X"
    assert report["total"] == 4
    assert report["succeeded"] == 2
    assert report["failed"] == 2
    assert report["retried"] == 1
    assert report["stage_histogram"]["post"] == 2
    assert report["stage_histogram"]["order"] == 1
    assert report["stage_histogram"]["quote"] == 1


def test_failure_signature_rollup_groups_same_signature() -> None:
    manifests = [
        _failed("R-1", "order", "transient", "request timed out"),
        _failed("R-2", "order", "transient", "request timed out"),
        _failed("R-3", "quote", "deterministic", "INVALID_FIELD: x"),
    ]
    report = build_batch_report(manifests)
    sigs = report["failure_signatures"]

    # Most-frequent first: the doubled transient timeout leads.
    assert sigs[0]["count"] == 2
    assert sorted(sigs[0]["run_ids"]) == ["R-1", "R-2"]
    assert sigs[0]["signature"].startswith("transient:")
    assert sigs[1]["count"] == 1


def test_none_reached_stage_buckets_under_none() -> None:
    report = build_batch_report([Manifest(run_id="R-1")])
    assert report["stage_histogram"]["(none)"] == 1


def test_render_markdown_includes_signatures() -> None:
    report = build_batch_report(
        [_failed("R-1", "order", "transient", "timed out")], base_run_id="DEMO-X"
    )
    md = render_markdown(report)
    assert "# Batch report — DEMO-X" in md
    assert "Failure signatures" in md
    assert "R-1" in md
