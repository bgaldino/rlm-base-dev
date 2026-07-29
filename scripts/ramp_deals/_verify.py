#!/usr/bin/env python3
"""Pure verification over a read-back ramped quote — no org call.

Given the structured read-back of a quote (a plain dict, however the caller
fetched it), assert the invariants that define a *correct* ramp. Shared by the
``verify_ramp`` CLI, the offline tests, and the MCP ``ramp_verify_quote`` tool so
the three cannot drift on what "valid" means.

Also owns the ``CalculationStatus`` polling sets, because deciding when a place /
clone has settled is part of trusting a read-back. The sets fold in the two live
264 corrections (findings §4.2):

  * ``CompletedWithTax`` / ``TaxCalculationSuccess`` are BOTH success — the org
    returns ``CompletedWithTax`` where the describe says ``TaxCalculationSuccess``
    (build_quote_to_asset.py:117-121).
  * The 264-new clone statuses: ``CloneInProgress`` is in-flight, ``CloneFailed``
    is a failure. A poller built from the 262 sets would hang on the first and
    treat the second as success.

TCV is checked on tolerance, never strict equality: ``TotalPriceOverride`` +
``AdjustmentDistributionLogic`` exist to make ``Quote.TotalPrice`` differ from the
line sum, so the check is skipped when a header override is set (PLAN.md §4.4).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ._schedule import assert_contiguous, ScheduleError

# --- CalculationStatus polling sets (live 264, findings §4.2) --------------- #

SUCCESS_STATUSES = frozenset({
    "CompletedWithPricing", "CompletedWithTax", "CompletedWithoutPricing",
    "TaxCalculationSuccess", "PartialSaveSuccess",
})
FAILURE_STATUSES = frozenset({
    "GroupRampConfigurationFailed", "ConfigurationFailed", "PriceCalculationFailed",
    "TaxCalculationFailed", "SaveFailedOrIncomplete", "QuoteRequestFailed",
    "ReconciliationFailed", "ImportQLIFailed", "PstBaseStepFailed",
    "CloneFailed",  # 264-new
})
# Everything not terminal is in-flight; enumerated so an unknown value is caught.
IN_FLIGHT_STATUSES = frozenset({
    "NotStarted", "TaxCalculationWaiting", "TaxCalculationInProcess",
    "PriceCalculationQueued", "PriceCalculationInProgress", "Saving",
    "ConfigurationInProgress", "ReconciliationInProgress", "QueuedForConfiguration",
    "QueuedForPricingAndSaving", "QueuedForPricing", "QueuedForSaving",
    "QuoteRequestPartiallySaved", "ImportQLIInProgress", "ContextHydrationInProgress",
    "CloneInProgress",  # 264-new
})

# Default tolerance for TCV vs Quote.TotalPrice (currency rounding across lines).
TCV_TOLERANCE = 0.01


def classify_status(status: str) -> str:
    """Return 'success' | 'failure' | 'in_flight' | 'unknown' for a status value.

    'unknown' is distinct on purpose: a status the sets don't know about must not
    be silently read as done. Treat 'unknown' as a reason to stop and look, not to
    keep polling forever or to declare success.
    """
    if status in SUCCESS_STATUSES:
        return "success"
    if status in FAILURE_STATUSES:
        return "failure"
    if status in IN_FLIGHT_STATUSES:
        return "in_flight"
    return "unknown"


class Result:
    """Accumulates named pass/fail checks; formats a report. Mirrors the toolkit
    convention (no pytest dependency at runtime)."""

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []

    def check(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "passed": bool(passed), "detail": detail})

    @property
    def passed(self) -> bool:
        return all(c["passed"] for c in self.checks)

    def failures(self) -> List[Dict[str, Any]]:
        return [c for c in self.checks if not c["passed"]]

    def format_report(self) -> str:
        lines = []
        for c in self.checks:
            mark = "PASS" if c["passed"] else "FAIL"
            suffix = f"  ({c['detail']})" if c["detail"] else ""
            lines.append(f"  [{mark}] {c['name']}{suffix}")
        n_pass = sum(1 for c in self.checks if c["passed"])
        lines.append(f"\n{n_pass}/{len(self.checks)} checks passed.")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {"passed": self.passed, "checks": self.checks}


def verify_quote(quote: Dict[str, Any], *, expected_segments: Optional[int] = None,
                 tcv_tolerance: float = TCV_TOLERANCE) -> Result:
    """Assert the ramp invariants over a read-back quote structure.

    Expected shape (the caller normalizes its SOQL/Connect read into this):
        {
          "Id": "...", "TotalPrice": <num or None>,
          "TotalPriceOverride": <num or None>,
          "groups": [
             {"Id": "...", "IsRamped": bool, "SegmentType": "...",
              "SortOrder": int, "StartDate": "YYYY-MM-DD", "EndDate": "YYYY-MM-DD",
              "lines": [{"RampIdentifier": "...", "SegmentIdentifier": "...",
                         "TotalPrice": <num>, ...}, ...]}
          ]
        }

    Checks:
      * at least one ramped group exists;
      * every ramped group carries a SegmentType and dates;
      * ramped groups are contiguous in sort order (no gaps/overlaps);
      * every line in a ramped group has a non-empty RampIdentifier AND
        SegmentIdentifier (proof the ramp went through groupRampAction, not a raw
        IsRamped PATCH — DO-NOT #6);
      * expected_segments matches the ramped-group count, when supplied;
      * TCV (sum of line TotalPrice) reconciles with Quote.TotalPrice within
        tolerance — skipped when TotalPriceOverride is set.
    """
    r = Result()
    groups = quote.get("groups") or []
    ramped = [g for g in groups if g.get("IsRamped")]

    r.check("has at least one ramped group", len(ramped) >= 1,
            f"{len(ramped)} ramped group(s)")
    if not ramped:
        return r

    for g in ramped:
        gid = g.get("Id", "?")
        r.check(f"group {gid} has a SegmentType", bool(g.get("SegmentType")),
                repr(g.get("SegmentType")))
        r.check(f"group {gid} has start+end dates",
                bool(g.get("StartDate")) and bool(g.get("EndDate")),
                f"{g.get('StartDate')}..{g.get('EndDate')}")

    # Contiguity across ramped segments.
    try:
        assert_contiguous([
            {"sort_order": g.get("SortOrder", 0),
             "start_date": g.get("StartDate"), "end_date": g.get("EndDate")}
            for g in ramped
        ])
        r.check("ramped segments are contiguous", True)
    except ScheduleError as exc:
        r.check("ramped segments are contiguous", False, str(exc))

    # Every ramped line carries both system identifiers.
    for g in ramped:
        for line in g.get("lines") or []:
            lid = line.get("Id", line.get("Product2Id", "?"))
            has_ids = bool(line.get("RampIdentifier")) and bool(line.get("SegmentIdentifier"))
            r.check(f"line {lid} has Ramp+Segment identifiers", has_ids,
                    f"Ramp={line.get('RampIdentifier')!r} "
                    f"Segment={line.get('SegmentIdentifier')!r}")

    if expected_segments is not None:
        r.check(f"ramped-group count == {expected_segments}",
                len(ramped) == expected_segments, f"actual {len(ramped)}")

    # TCV reconciliation on tolerance, skipped when a header override is set.
    override = quote.get("TotalPriceOverride")
    if override in (None, "", 0):
        line_sum = 0.0
        for g in ramped:
            for line in g.get("lines") or []:
                tp = line.get("TotalPrice")
                if isinstance(tp, (int, float)):
                    line_sum += tp
        total = quote.get("TotalPrice")
        if isinstance(total, (int, float)):
            r.check("TCV reconciles with Quote.TotalPrice",
                    abs(line_sum - total) <= tcv_tolerance,
                    f"sum(lines)={line_sum} vs TotalPrice={total} "
                    f"(tol {tcv_tolerance})")
        else:
            r.check("Quote.TotalPrice present for TCV check", False,
                    f"TotalPrice={total!r}")
    else:
        r.check("TCV check skipped (TotalPriceOverride set)", True, f"override={override}")

    return r
