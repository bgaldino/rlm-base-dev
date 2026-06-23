"""Shared execution models for the Transaction Data Harness.

Config parsing models stay in ``config.py`` because they represent unresolved
user intent. The models here represent resolved execution state that can be
shared by the CLI, runner, step registry, manifest store, and AI-facing tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from .config import ScenarioSpec
from .discovery import Account, Product

STAGES = ["opportunity", "quote", "order", "activate", "usage", "invoice", "post"]

# Full lifecycle implemented by the harness.
IMPLEMENTED_MAX_STAGE = "post"


@dataclass
class ResolvedUsageTarget:
    """One (UsageResource, UoM) the harness will write journals for.

    Multi-resource products (e.g. QB-DB grants UR-DATASTORAGE and UR-CPUTIME)
    resolve to one target per binding, each carrying its own UoM id so the per-
    resource defaults aren't collapsed onto a single class.
    """

    resource_id: str
    resource_code: str
    uom_id: str
    uom_code: Optional[str] = None


@dataclass
class ResolvedUsageSpec:
    """A ``UsageSpec`` bound to concrete UsageResource/UoM ids.

    The numeric ranges + ``days_back`` survive resolution unchanged; sampling
    happens per-row inside ``lifecycle.create_usage_journals`` so the same spec
    instance round-trips across retries.
    """

    quantity: tuple[float, float]
    records_per_line: tuple[int, int]
    days_back: int
    targets: list[ResolvedUsageTarget] = field(default_factory=list)


@dataclass
class Manifest:
    """Source-of-truth record of everything a scenario created, by stage.

    Written even on partial failure so cleanup can find orphans. ``run_id`` is
    the durable tag stamped on records and passed as invoice correlationId.
    """

    run_id: str
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    opportunity_id: Optional[str] = None
    quote_id: Optional[str] = None
    order_id: Optional[str] = None
    order_number: Optional[str] = None
    billing_schedule_ids: list[str] = field(default_factory=list)
    asset_ids: list[str] = field(default_factory=list)
    # TransactionJournal ids written by the ``usage`` stage. Tagged with
    # deterministic ``UniqueIdentifier``s so retries dedupe by query.
    usage_journal_ids: list[str] = field(default_factory=list)
    invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    # The line StartDate placed on this quote (ISO; drawn from the scenario's
    # start_date range, or None when defaulted to today).
    start_date: Optional[str] = None
    # The lines actually placed on the quote (sku/quantity/discount per line).
    lines: list[dict] = field(default_factory=list)
    reached_stage: Optional[str] = None
    error: Optional[str] = None
    # Number of attempts spent on this scenario (1 = succeeded or failed on the
    # first try; >1 means transient failures were retried). See runner.py.
    attempts: int = 1
    # The classification of the final ``error`` (transient/deterministic/unknown)
    # as decided by failure.classify_exception; None when the scenario succeeded.
    failure_class: Optional[str] = None

    def to_dict(self) -> dict:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, data: dict) -> "Manifest":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class LineItem:
    """One resolved quote line to place."""

    product: Product
    quantity: int = 1
    discount_percent: Optional[float] = None
    period_boundary: Optional[str] = None
    billing_frequency: Optional[str] = None
    # When set, run_usage emits TransactionJournals against the activated
    # asset for each target resource.
    usage: Optional[ResolvedUsageSpec] = None

    def to_manifest_record(self) -> dict:
        rec: dict = {
            "sku": self.product.sku,
            "quantity": self.quantity,
            "discount_percent": self.discount_percent,
        }
        if self.period_boundary is not None:
            rec["period_boundary"] = self.period_boundary
        if self.billing_frequency is not None:
            rec["billing_frequency"] = self.billing_frequency
        if self.usage is not None:
            rec["usage"] = {
                "quantity": list(self.usage.quantity),
                "records_per_line": list(self.usage.records_per_line),
                "days_back": self.usage.days_back,
                "targets": [
                    {
                        "resource_id": t.resource_id,
                        "resource_code": t.resource_code,
                        "uom_id": t.uom_id,
                        "uom_code": t.uom_code,
                    }
                    for t in self.usage.targets
                ],
            }
        return rec

    @classmethod
    def from_manifest_record(cls, record: dict, product: Product) -> "LineItem":
        usage = None
        usage_raw = record.get("usage")
        if usage_raw:
            qlo, qhi = usage_raw["quantity"]
            rlo, rhi = usage_raw["records_per_line"]
            usage = ResolvedUsageSpec(
                quantity=(float(qlo), float(qhi)),
                records_per_line=(int(rlo), int(rhi)),
                days_back=int(usage_raw.get("days_back", 0)),
                targets=[
                    ResolvedUsageTarget(
                        resource_id=t["resource_id"],
                        resource_code=t["resource_code"],
                        uom_id=t["uom_id"],
                        uom_code=t.get("uom_code"),
                    )
                    for t in usage_raw.get("targets", [])
                ],
            )
        return cls(
            product=product,
            quantity=int(record.get("quantity", 1)),
            discount_percent=record.get("discount_percent"),
            period_boundary=record.get("period_boundary"),
            billing_frequency=record.get("billing_frequency"),
            usage=usage,
        )


@dataclass
class ResolvedOption:
    """A config ``ProductOption`` bound to a concrete org Product."""

    product: Product
    quantity: tuple[int, int]
    discount: Optional[tuple[float, float]]
    period_boundary: Optional[str] = None
    billing_frequency: Optional[str] = None
    usage: Optional[ResolvedUsageSpec] = None


@dataclass
class ResolvedSpec:
    """A scenario spec bound to concrete org records, ready to fan out."""

    spec: ScenarioSpec
    account: Account
    options: list[ResolvedOption]
    effective_stage: str

    @property
    def start_date_range(self) -> Optional[tuple[date, date]]:
        return self.spec.start_date
