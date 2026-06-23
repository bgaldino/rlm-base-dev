"""Tests for shared models and manifest persistence."""

from __future__ import annotations

import os

from scripts.txn_data_harness.manifests import (
    list_manifests,
    load_manifest,
    summarize_manifest,
    write_manifest,
)
from scripts.txn_data_harness.models import LineItem, Manifest


def test_manifest_from_dict_ignores_unknown_future_keys() -> None:
    manifest = Manifest.from_dict({
        "run_id": "DEMO-1",
        "quote_id": "0Q0",
        "future_field": "ignored",
    })
    assert manifest.run_id == "DEMO-1"
    assert manifest.quote_id == "0Q0"
    assert not hasattr(manifest, "future_field")


def test_line_item_manifest_record_includes_optional_proration(term_product) -> None:
    rec = LineItem(
        product=term_product,
        quantity=2,
        discount_percent=10,
        period_boundary="Anniversary",
        billing_frequency="Monthly",
    ).to_manifest_record()
    assert rec == {
        "sku": "QB-API-FLEX",
        "quantity": 2,
        "discount_percent": 10,
        "period_boundary": "Anniversary",
        "billing_frequency": "Monthly",
    }


def test_write_and_load_manifest_by_run_id(tmp_path) -> None:
    original = Manifest(
        run_id="DEMO-1",
        account_name="Infinitech",
        reached_stage="quote",
        quote_id="0Q0QUOTE",
    )
    path = write_manifest(original, manifest_dir=tmp_path)
    assert path == tmp_path / "DEMO-1.json"

    loaded = load_manifest("DEMO-1", manifest_dir=tmp_path)
    assert loaded.to_dict() == original.to_dict()


def test_list_manifests_newest_first(tmp_path) -> None:
    old = write_manifest(Manifest(run_id="DEMO-OLD"), manifest_dir=tmp_path)
    new = write_manifest(Manifest(run_id="DEMO-NEW"), manifest_dir=tmp_path)
    os.utime(old, (1, 1))
    os.utime(new, (2, 2))

    assert list_manifests(tmp_path) == [new, old]


def test_list_manifests_excludes_batch_report_files(tmp_path) -> None:
    """Batch reports live alongside manifests but have a different schema; the
    listing must skip them or ``inspect --latest`` crashes in from_dict.
    """
    manifest = write_manifest(Manifest(run_id="DEMO-NEW"), manifest_dir=tmp_path)
    report = tmp_path / "DEMO-NEW-report.json"
    report.write_text('{"not": "a manifest"}\n')
    os.utime(manifest, (1, 1))
    os.utime(report, (2, 2))

    assert list_manifests(tmp_path) == [manifest]


def test_summarize_manifest_returns_compact_machine_shape() -> None:
    manifest = Manifest(
        run_id="DEMO-1",
        account_name="Infinitech",
        reached_stage="post",
        order_id="801ORDER",
        invoice_id="INV-ID",
        invoice_number="INV-0001",
        billing_schedule_ids=["BS-1"],
        asset_ids=["ASSET-1"],
        lines=[{"sku": "QB-API-FLEX"}],
    )
    summary = summarize_manifest(manifest)
    assert summary["account"] == "Infinitech"
    assert summary["line_count"] == 1
    assert summary["ids"]["order"] == "801ORDER"
    assert summary["ids"]["billing_schedules"] == ["BS-1"]
    assert summary["invoice_number"] == "INV-0001"
