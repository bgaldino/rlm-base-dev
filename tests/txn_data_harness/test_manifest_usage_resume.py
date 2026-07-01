"""Round-trip a usage-bearing LineItem through manifest serialization.

The resume path (``cli step --to-stage usage`` after ``activate``) rebuilds
``LineItem`` instances from the manifest dict via
``LineItem.from_manifest_record``. The serialized usage block must carry
enough information to reconstruct the ``ResolvedUsageSpec`` (including each
target's resource + UoM id) so the step needs no second discovery pass.
"""

from __future__ import annotations

from scripts.txn_data_harness.models import (
    LineItem,
    ResolvedUsageSpec,
    ResolvedUsageTarget,
)


def _line(product) -> LineItem:
    return LineItem(
        product=product,
        quantity=2,
        usage=ResolvedUsageSpec(
            quantity=(100.0, 500.0),
            records_per_line=(5, 10),
            days_back=30,
            targets=[
                ResolvedUsageTarget(
                    resource_id="RES-DATA",
                    resource_code="UR-DATASTORAGE",
                    uom_id="UOM-TB",
                    uom_code="TB",
                ),
                ResolvedUsageTarget(
                    resource_id="RES-CPU",
                    resource_code="UR-CPUTIME",
                    uom_id="UOM-HR",
                    uom_code="hr",
                ),
            ],
        ),
    )


def test_to_manifest_record_serializes_usage_block(term_product) -> None:
    rec = _line(term_product).to_manifest_record()
    assert rec["sku"] == "QB-API-FLEX"
    assert rec["quantity"] == 2
    usage = rec["usage"]
    assert usage["quantity"] == [100.0, 500.0]
    assert usage["records_per_line"] == [5, 10]
    assert usage["days_back"] == 30
    codes = [t["resource_code"] for t in usage["targets"]]
    assert codes == ["UR-DATASTORAGE", "UR-CPUTIME"]
    assert all("resource_id" in t and "uom_id" in t for t in usage["targets"])


def test_from_manifest_record_rehydrates_resolved_usage_spec(term_product) -> None:
    record = _line(term_product).to_manifest_record()
    line = LineItem.from_manifest_record(record, term_product)

    assert line.product is term_product
    assert line.quantity == 2
    assert line.usage is not None
    assert line.usage.quantity == (100.0, 500.0)
    assert line.usage.records_per_line == (5, 10)
    assert line.usage.days_back == 30
    assert len(line.usage.targets) == 2

    data, cpu = line.usage.targets
    assert data.resource_id == "RES-DATA"
    assert data.resource_code == "UR-DATASTORAGE"
    assert data.uom_id == "UOM-TB"
    assert data.uom_code == "TB"
    assert cpu.resource_code == "UR-CPUTIME"
    assert cpu.uom_id == "UOM-HR"


def test_from_manifest_record_without_usage_block(term_product) -> None:
    """Non-usage lines round-trip without an injected usage spec."""
    record = LineItem(product=term_product, quantity=1).to_manifest_record()
    assert "usage" not in record
    line = LineItem.from_manifest_record(record, term_product)
    assert line.usage is None
