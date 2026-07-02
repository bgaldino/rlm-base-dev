"""Subscription term value objects.

A standalone module so ``config.py`` (pure parse/validate), ``discovery.py``
(org introspection), ``models.py`` (resolved state), and ``lifecycle.py``
(REST payloads) can all reference the same ``Term`` shape without any of
them pulling in another's responsibilities.

``unit`` carries one of the four real ``ProductSellingModel.PricingTermUnit``
picklist values (verified against the bundled ``ProductSellingModel.csv`` and
a Revenue Cloud R262 scratch org). ``None`` is the sentinel a bare-int
``term: N`` from YAML lands in -- the runner resolves it to the bound PSM's
unit once the PBE is known.

:class:`EndDateOverride` carries an explicit ``EndDate`` request a scenario
can pin on a line. Resolved against the line's drawn ``StartDate`` at
lifecycle time so a scenario-level ``end_date`` co-terms every line on the
quote to the same calendar anchor.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

# Canonical PricingTermUnit picklist values. Case-sensitive on write.
VALID_TERM_UNITS: frozenset[str] = frozenset(
    {"Months", "Annual", "Quarterly", "Semi-Annual"}
)

# Supported relative-offset units for ``end_date`` config. Bare ints are days
# (consistent with how ``start_date`` treats relative offsets).
#
#   d  -> day
#   mo -> calendar month (day-clamped for short months: Jan 31 + 1mo = Feb 28/29)
#   q  -> quarter = 3 calendar months
#   y  -> year = 12 calendar months
#
# ``m`` is intentionally rejected -- ambiguous between minutes/months/meters.
# The user must spell ``mo``.
END_DATE_UNITS: frozenset[str] = frozenset({"d", "mo", "q", "y"})


@dataclass(frozen=True)
class Term:
    """A subscription term expressed as ``(count, PricingTermUnit)``.

    ``unit`` is ``None`` only while a bare-int ``term: N`` config value is
    in flight from parse-time to PBE-resolution-time; everywhere else the
    unit is one of :data:`VALID_TERM_UNITS`.
    """

    count: int
    unit: Optional[str]

    @staticmethod
    def is_valid_unit(unit: Optional[str]) -> bool:
        return unit in VALID_TERM_UNITS


def _add_months(start: date, months: int) -> date:
    """Calendar-correct month add with day clamp for short target months.

    ``Jan 31 + 1`` lands on ``Feb 28`` (or ``Feb 29`` in a leap year);
    ``Aug 31 + 1`` lands on ``Sep 30``. Negative ``months`` is not supported
    (end_date is forward-only per design).
    """
    if months < 0:
        raise ValueError(f"_add_months: negative months not supported (got {months})")
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)


@dataclass(frozen=True)
class EndDateOverride:
    """An explicit ``EndDate`` a scenario can pin on a line.

    Exactly one of ``absolute`` / ``days`` / ``months`` is set; the other two
    are ``None``. ``q`` and ``y`` units collapse to ``months`` (3 / 12) at
    parse time so the resolver only needs two branches.

    Resolved against the line's drawn ``StartDate`` in
    :meth:`resolve`; carried unresolved through config/models/manifest so the
    same override round-trips through ``cli step`` resume.
    """

    absolute: Optional[date] = None
    days: Optional[int] = None
    months: Optional[int] = None

    def resolve(self, start: date) -> date:
        """Apply this override to ``start`` and return a concrete ``EndDate``."""
        if self.absolute is not None:
            return self.absolute
        if self.days is not None:
            return start + timedelta(days=self.days)
        if self.months is not None:
            return _add_months(start, self.months)
        raise ValueError(
            "EndDateOverride has no resolved form -- absolute/days/months all None"
        )

    def to_dict(self) -> dict:
        """Serialize for manifest round-trip. Exactly one key is present."""
        if self.absolute is not None:
            return {"absolute": self.absolute.isoformat()}
        if self.days is not None:
            return {"days": self.days}
        if self.months is not None:
            return {"months": self.months}
        raise ValueError("EndDateOverride has no value to serialize")

    @classmethod
    def from_dict(cls, raw: dict) -> "EndDateOverride":
        if "absolute" in raw:
            return cls(absolute=date.fromisoformat(raw["absolute"]))
        if "days" in raw:
            return cls(days=int(raw["days"]))
        if "months" in raw:
            return cls(months=int(raw["months"]))
        raise ValueError(f"EndDateOverride dict missing absolute/days/months: {raw!r}")
