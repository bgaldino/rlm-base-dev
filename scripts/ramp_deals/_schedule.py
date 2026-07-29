#!/usr/bin/env python3
"""Pure ramp-schedule mathematics — no org call, no dependency.

Turns a term + segment type + start date (+ optional trial / proration) into the
ordered table of segments a ramped quote needs. Owns the three rules that a
payload built by hand gets wrong:

  * **Calendar months, not 365 days.** ``Yearly`` means 12 *calendar* months; a
    ``== 365`` assertion fails across a leap day (PLAN.md §4.5, DO-NOT #7's
    neighbour). Month arithmetic is done by (year, month) advance + day clamp,
    never by adding ``timedelta(days=…)``.
  * **Contiguity.** "Each segment starts exactly 1 day after the previous segment
    ends" (``HELP/ind.qocal_ramp_schedule_with_trial_and_proration_segments``).
  * **The ceiling.** ≤ 12 group-ramp segments per schedule *excluding the trial*
    segment (``HELP/ind.qocal_ramp_deals_for_groups_considerations``).

Everything is a pure function over ``datetime.date`` and plain dicts. Segment
types are the live 264 values (``E9-ramp-field-summary.md``): the fourth is
``FreeTrial``, **not** ``Trial`` (a payload built with ``Trial`` is rejected).

A segment is a dict: ``{index, sort_order, segment_type, start_date, end_date,
is_trial}`` — dates as ``YYYY-MM-DD`` strings (the shape the Connect graph wants).
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import List, Optional


class ScheduleError(ValueError):
    """A schedule that violates a ramp rule — raised before any org call."""


# Live 264 / v68.0 picklist for QuoteLineGroup.SegmentType and
# QuoteLineItem.SegmentType (E9-ramp-field-summary.md). NOTE: FreeTrial, not Trial.
SEGMENT_TYPES = frozenset({"Custom", "Yearly", "FreeTrial", "Prorated"})

# The one segment type that does not count against the 12-segment ceiling.
TRIAL_SEGMENT_TYPE = "FreeTrial"

# ≤ 12 group-ramp segments per schedule, excluding the trial segment.
MAX_SEGMENTS_EXCLUDING_TRIAL = 12


def _iso(d: date) -> str:
    return d.isoformat()


def add_calendar_months(start: date, months: int) -> date:
    """Return the date ``months`` calendar months after ``start``.

    Day-of-month is clamped to the target month's length (Jan 31 + 1 month =
    Feb 28/29), matching how the platform increments ramp segment dates. This is
    deliberately NOT ``timedelta`` arithmetic — a ramp year is 12 calendar
    months, whose day count varies with leap years and month lengths.
    """
    if months < 0:
        raise ScheduleError(f"months must be >= 0, got {months}")
    # zero-based month index math, then back to 1..12
    month_index = (start.month - 1) + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def segment_end(segment_start: date, months: int) -> date:
    """End date of a segment that runs ``months`` calendar months from its start.

    The segment spans ``[start, start+months)`` in calendar terms; the stored end
    date is the **last day** of that span — i.e. the day *before* the next
    segment's start, giving contiguity with a 1-day gap-free boundary.
    """
    return add_calendar_months(segment_start, months) - timedelta(days=1)


def _coerce_date(value) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ScheduleError(f"invalid date {value!r}: {exc}") from exc
    raise ScheduleError(f"expected a date or YYYY-MM-DD string, got {type(value).__name__}")


def build_schedule(
    *,
    start_date,
    segment_type: str,
    segment_count: int,
    months_per_segment: int = 12,
    trial_months: int = 0,
) -> List[dict]:
    """Build the ordered segment table for a uniform group ramp schedule.

    Args:
        start_date: first segment's start (date or ``YYYY-MM-DD``). If a trial is
            present, the trial starts here and the first paid segment follows it.
        segment_type: one of ``SEGMENT_TYPES`` for the paid segments. ``Yearly``
            forces ``months_per_segment = 12``.
        segment_count: number of **paid** segments (the trial is separate and does
            not count toward this or the ceiling).
        months_per_segment: calendar months per paid segment (ignored for
            ``Yearly``, which is always 12).
        trial_months: length of a leading ``FreeTrial`` segment; 0 = no trial.

    Returns:
        A list of segment dicts ordered by ``sort_order`` (1-based). A trial, when
        present, is ``sort_order`` 1 and every paid segment shifts up by one.

    Raises:
        ScheduleError: unknown segment type, non-positive count, or a paid-segment
            count exceeding ``MAX_SEGMENTS_EXCLUDING_TRIAL``.
    """
    if segment_type not in SEGMENT_TYPES:
        raise ScheduleError(
            f"segment_type {segment_type!r} not in {sorted(SEGMENT_TYPES)} "
            "(note: the trial value is 'FreeTrial', not 'Trial')"
        )
    if segment_type == TRIAL_SEGMENT_TYPE:
        raise ScheduleError(
            "segment_type is the paid-segment type; request a trial via trial_months, "
            "not by setting segment_type='FreeTrial'"
        )
    if segment_count < 1:
        raise ScheduleError(f"segment_count must be >= 1, got {segment_count}")
    if segment_count > MAX_SEGMENTS_EXCLUDING_TRIAL:
        raise ScheduleError(
            f"segment_count {segment_count} exceeds the ceiling of "
            f"{MAX_SEGMENTS_EXCLUDING_TRIAL} paid segments per schedule (the trial "
            "is excluded from this count)"
        )
    if trial_months < 0:
        raise ScheduleError(f"trial_months must be >= 0, got {trial_months}")

    months = 12 if segment_type == "Yearly" else months_per_segment
    if months < 1:
        raise ScheduleError(f"months_per_segment must be >= 1, got {months_per_segment}")

    cursor = _coerce_date(start_date)
    segments: List[dict] = []
    sort_order = 1

    if trial_months > 0:
        t_end = segment_end(cursor, trial_months)
        segments.append({
            "index": len(segments),
            "sort_order": sort_order,
            "segment_type": TRIAL_SEGMENT_TYPE,
            "start_date": _iso(cursor),
            "end_date": _iso(t_end),
            "is_trial": True,
        })
        sort_order += 1
        cursor = t_end + timedelta(days=1)

    for _ in range(segment_count):
        s_end = segment_end(cursor, months)
        segments.append({
            "index": len(segments),
            "sort_order": sort_order,
            "segment_type": segment_type,
            "start_date": _iso(cursor),
            "end_date": _iso(s_end),
            "is_trial": False,
        })
        sort_order += 1
        cursor = s_end + timedelta(days=1)

    return segments


def assert_contiguous(segments: List[dict]) -> None:
    """Raise if segments are not gap-free and non-overlapping, in sort order.

    The rule: each segment starts exactly one day after the previous one ends.
    Used by both ``build_schedule`` callers (as a self-check) and ``_verify`` on a
    read-back quote, so the same definition of "valid ramp" applies to authoring
    and verification.
    """
    ordered = sorted(segments, key=lambda s: s["sort_order"])
    for prev, cur in zip(ordered, ordered[1:]):
        prev_end = _coerce_date(prev["end_date"])
        cur_start = _coerce_date(cur["start_date"])
        if cur_start != prev_end + timedelta(days=1):
            raise ScheduleError(
                f"segments not contiguous: segment ending {prev['end_date']} is "
                f"followed by one starting {cur['start_date']} "
                f"(expected {_iso(prev_end + timedelta(days=1))})"
            )


def paid_segment_count(segments: List[dict]) -> int:
    """Count of non-trial segments — the number that counts against the ceiling."""
    return sum(1 for s in segments if not s.get("is_trial"))
