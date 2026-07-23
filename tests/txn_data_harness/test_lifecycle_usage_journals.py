"""Tests for TransactionJournal create payloads + idempotent-retry behavior."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scripts.txn_data_harness.lifecycle import (
    LifecycleError,
    create_usage_journals,
    fetch_assets_product_ids,
)
from scripts.txn_data_harness.models import (
    LineItem,
    ResolvedUsageSpec,
    ResolvedUsageTarget,
)


def _line(product, *, targets, records=(2, 2), quantity=(100.0, 100.0), days_back=0):
    return LineItem(
        product=product,
        quantity=1,
        usage=ResolvedUsageSpec(
            quantity=quantity,
            records_per_line=records,
            days_back=days_back,
            targets=list(targets),
        ),
    )


def _target(suffix: str = "1", uom: str = "TB") -> ResolvedUsageTarget:
    return ResolvedUsageTarget(
        resource_id=f"RES-{suffix}",
        resource_code=f"UR-{suffix}",
        uom_id=f"UOM-{suffix}",
        uom_code=uom,
    )


def test_create_usage_journals_emits_one_chunk_with_expected_payload(
    fake_client, term_product
) -> None:
    # No existing UniqueIdentifiers in the org.
    fake_client.query_responses.append([])
    fake_client.post_responses.append([
        {"success": True, "id": "0VS001"},
        {"success": True, "id": "0VS002"},
    ])

    line = _line(term_product, targets=[_target("CPU", "hr")], records=(2, 2))
    now = datetime(2026, 6, 22, 12, 0, tzinfo=timezone.utc)

    ids = create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1", now=now
    )

    assert ids == ["0VS001", "0VS002"]
    path, body = fake_client.posts[0]
    assert path.endswith("/composite/sobjects")
    assert body["allOrNone"] is True
    records = body["records"]
    assert len(records) == 2
    # Per-row UniqueIdentifier scheme.
    uids = [r["UniqueIdentifier"] for r in records]
    assert uids == [
        "txn-harness-DEMO-1-02iASSET-0-0",
        "txn-harness-DEMO-1-02iASSET-0-1",
    ]
    # Payload shape matches the live-verified contract.
    row = records[0]
    assert row["attributes"] == {"type": "TransactionJournal"}
    assert row["ReferenceRecordId"] == "02iASSET"
    assert row["AccountId"] == "001ACC"
    assert row["UsageResourceId"] == "RES-CPU"
    assert row["QuantityUnitOfMeasureId"] == "UOM-CPU"
    assert row["Quantity"] == 100.0
    # ActivityDate / StartDate / EndDate all equal -- one-day journals.
    assert row["ActivityDate"] == row["StartDate"] == row["EndDate"]
    assert row["UsageType"] == "UsageManagement"
    assert row["Status"] == "Pending"


def test_create_usage_journals_writes_one_set_per_target(
    fake_client, term_product
) -> None:
    fake_client.query_responses.append([])
    fake_client.post_responses.append([
        {"success": True, "id": "0VS001"},
        {"success": True, "id": "0VS002"},
        {"success": True, "id": "0VS003"},
        {"success": True, "id": "0VS004"},
    ])
    line = _line(
        term_product,
        targets=[_target("DATA", "TB"), _target("CPU", "hr")],
        records=(2, 2),
    )
    ids = create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1",
        now=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )
    assert len(ids) == 4
    _, body = fake_client.posts[0]
    uids = [r["UniqueIdentifier"] for r in body["records"]]
    assert uids == [
        "txn-harness-DEMO-1-02iASSET-0-0",
        "txn-harness-DEMO-1-02iASSET-0-1",
        "txn-harness-DEMO-1-02iASSET-1-0",
        "txn-harness-DEMO-1-02iASSET-1-1",
    ]


def test_create_usage_journals_returns_existing_ids_when_some_already_exist(
    fake_client, term_product
) -> None:
    """Idempotent retry: a previously-created TJ row is reused (not recreated)
    AND its id is still returned, combined with the newly-created ids."""
    # Pre-flight query finds one of the two expected UniqueIdentifiers already
    # in the org. Only one new row will be posted; the other id comes from the
    # existing-row query.
    fake_client.query_responses.append([
        {
            "Id": "0VSEXISTING",
            "UniqueIdentifier": "txn-harness-DEMO-1-02iASSET-0-0",
        },
    ])
    fake_client.post_responses.append([{"success": True, "id": "0VSNEW"}])

    line = _line(term_product, targets=[_target("CPU", "hr")], records=(2, 2))
    ids = create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1",
        now=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )

    # The existing id is returned alongside the newly created id (order:
    # existing first, then new -- matches the implementation contract).
    assert sorted(ids) == sorted(["0VSEXISTING", "0VSNEW"])
    assert "0VSEXISTING" in ids
    assert "0VSNEW" in ids
    # Only ONE row sent to the create endpoint (the missing UniqueIdentifier).
    _, body = fake_client.posts[0]
    assert len(body["records"]) == 1
    assert body["records"][0]["UniqueIdentifier"] == "txn-harness-DEMO-1-02iASSET-0-1"


def test_create_usage_journals_all_existing_skips_post(
    fake_client, term_product
) -> None:
    """When every expected UniqueIdentifier is already in the org, we make no
    create call and simply return the existing ids."""
    fake_client.query_responses.append([
        {"Id": "0VS001", "UniqueIdentifier": "txn-harness-DEMO-1-02iASSET-0-0"},
        {"Id": "0VS002", "UniqueIdentifier": "txn-harness-DEMO-1-02iASSET-0-1"},
    ])
    line = _line(term_product, targets=[_target("CPU", "hr")], records=(2, 2))
    ids = create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1",
        now=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )
    assert sorted(ids) == ["0VS001", "0VS002"]
    assert fake_client.posts == []


def test_create_usage_journals_raises_on_partial_failure(
    fake_client, term_product
) -> None:
    fake_client.query_responses.append([])
    fake_client.post_responses.append([
        {"success": True, "id": "0VS001"},
        {"success": False, "errors": [{"message": "bad ref"}]},
    ])
    line = _line(term_product, targets=[_target("CPU", "hr")], records=(2, 2))
    with pytest.raises(LifecycleError, match="TransactionJournal create failures"):
        create_usage_journals(
            fake_client, "02iASSET", "001ACC", line, "DEMO-1",
            now=datetime(2026, 6, 22, tzinfo=timezone.utc),
        )


def test_create_usage_journals_with_no_targets_returns_empty(
    fake_client, term_product
) -> None:
    line = _line(term_product, targets=[])
    assert create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1",
        now=datetime(2026, 6, 22, tzinfo=timezone.utc),
    ) == []
    assert fake_client.posts == []
    assert fake_client.queries == []


def test_create_usage_journals_spreads_dates_when_days_back_set(
    fake_client, term_product
) -> None:
    fake_client.query_responses.append([])
    fake_client.post_responses.append([
        {"success": True, "id": f"0VS{i}"} for i in range(3)
    ])
    line = _line(term_product, targets=[_target("CPU", "hr")], records=(3, 3),
                 days_back=30)
    create_usage_journals(
        fake_client, "02iASSET", "001ACC", line, "DEMO-1",
        now=datetime(2026, 6, 22, tzinfo=timezone.utc),
    )
    _, body = fake_client.posts[0]
    activity_dates = [r["ActivityDate"] for r in body["records"]]
    # All 3 dates distinct; last row should be "today" (2026-06-22).
    assert len(set(activity_dates)) == 3
    assert activity_dates[-1] == "2026-06-22"


def test_fetch_assets_product_ids_returns_mapping(fake_client) -> None:
    fake_client.query_responses.append([
        {"Id": "02iAAA", "Product2Id": "01tDB"},
        {"Id": "02iBBB", "Product2Id": "01tTOKEN"},
    ])
    mapping = fetch_assets_product_ids(fake_client, ["02iAAA", "02iBBB"])
    assert mapping == {"02iAAA": "01tDB", "02iBBB": "01tTOKEN"}
    assert "Asset WHERE Id IN ('02iAAA', '02iBBB')" in fake_client.queries[0]


def test_fetch_assets_product_ids_empty_input_short_circuits(fake_client) -> None:
    assert fetch_assets_product_ids(fake_client, []) == {}
    assert fake_client.queries == []
