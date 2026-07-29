#!/usr/bin/env python3
"""Plan (and validate) a ramp schedule — pure, no org, no auth.

The first shippable verb of the ramp-deals toolkit: turn a term + segment type +
start date (+ optional free trial) into the ordered segment table a ramped quote
needs, and prove it obeys the ramp rules (calendar-month sizing, contiguity, the
≤12-paid-segment ceiling) BEFORE anyone builds a `place` body against an org.

Because it wraps only ``_schedule.build_schedule`` it needs no ``--target-org`` and
opens no socket — safe to run anywhere, and the natural first tool for the MCP
façade (``ramp_plan_schedule``).

Usage
-----
    # 3 yearly segments from 2026-01-01
    python scripts/ramp_deals/plan_ramp_schedule.py \
        --start-date 2026-01-01 --segment-type Yearly --segments 3

    # 2 custom 6-month segments after a 1-month free trial, as JSON
    python scripts/ramp_deals/plan_ramp_schedule.py \
        --start-date 2026-01-01 --segment-type Custom --segments 2 \
        --months-per-segment 6 --trial-months 1 --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.ramp_deals._schedule import (  # noqa: E402
    SEGMENT_TYPES,
    ScheduleError,
    assert_contiguous,
    build_schedule,
    paid_segment_count,
)


def _print_table(segments):
    print(f"{len(segments)} segment(s) "
          f"({paid_segment_count(segments)} paid):\n")
    print(f"  {'#':>2}  {'type':<9}  {'start':<10}  {'end':<10}  trial")
    print(f"  {'-'*2}  {'-'*9}  {'-'*10}  {'-'*10}  {'-'*5}")
    for s in segments:
        print(f"  {s['sort_order']:>2}  {s['segment_type']:<9}  "
              f"{s['start_date']:<10}  {s['end_date']:<10}  "
              f"{'yes' if s['is_trial'] else ''}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan and validate a ramp schedule (pure — no org needed).",
    )
    parser.add_argument("--start-date", required=True,
                        help="First segment start (YYYY-MM-DD). With a trial, the "
                             "trial starts here and the first paid segment follows.")
    parser.add_argument("--segment-type", required=True,
                        help=f"Paid-segment type — one of {sorted(SEGMENT_TYPES)} "
                             "(the trial value is 'FreeTrial'; request it via "
                             "--trial-months, not here).")
    parser.add_argument("--segments", type=int, required=True,
                        help="Number of PAID segments (trial excluded).")
    parser.add_argument("--months-per-segment", type=int, default=12,
                        help="Calendar months per paid segment (ignored for "
                             "Yearly, which is always 12). Default 12.")
    parser.add_argument("--trial-months", type=int, default=0,
                        help="Leading FreeTrial length in months; 0 = no trial.")
    parser.add_argument("--json", action="store_true", help="Emit segments as JSON.")
    args = parser.parse_args(argv)

    try:
        segments = build_schedule(
            start_date=args.start_date,
            segment_type=args.segment_type,
            segment_count=args.segments,
            months_per_segment=args.months_per_segment,
            trial_months=args.trial_months,
        )
        assert_contiguous(segments)  # belt-and-suspenders self-check
    except ScheduleError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(segments, indent=2))
    else:
        _print_table(segments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
