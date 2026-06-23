"""Config spec load / validate / merge for the demo data generator.

A run is described by a list of :class:`ScenarioSpec` -- each spec is one
account/product shape repeated ``count`` times. With no config file the tool
synthesizes a single spec from CLI flags + built-in defaults, so it runs against
a fresh org with zero configuration; a ``--config`` file lets one run mix several
shapes (e.g. billable-account ``post`` orders + pipeline-only-account
``quote``-only pipeline data, in any combination of accounts available in the
target org).

Specs here are *un-resolved*: they carry account *names* and product *SKUs*, not
org ids. ``generate.py`` resolves them against discovery so this module stays a
pure parse/validate/merge layer with no org dependency.

Precedence (most specific wins):

    per-scenario field  >  CLI flag  >  config ``defaults``  >  built-in default

CLI flags override the broad ``defaults`` block; an explicit per-scenario value
is the most specific intent and wins over everything. ``--with-opportunity`` is a
store_true flag, so it can only *enable* (never force-disable) -- pin
``with_opportunity: false`` per scenario in config to opt a scenario out.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from .term import END_DATE_UNITS, VALID_TERM_UNITS, EndDateOverride, Term

log = logging.getLogger("txn_data_harness.config")

# YAML conveniences -> canonical PricingTermUnit. ``Years`` is the only alias
# we accept (per plan); anything else is rejected with a clear error.
_TERM_UNIT_ALIASES = {"Years": "Annual"}

# Defensive upper bound on `term: N`. Real demos won't exceed a handful of
# years; this catches typos like `term: 360` (months mistakenly multiplied).
_MAX_TERM_COUNT = 120

# Built-in defaults (lowest precedence). target_stage caps/resolution happen in
# generate.py against the resolved account -- this is just the requested stage.
_BUILTIN_DEFAULTS: dict[str, Any] = {
    "target_stage": "post",
    "with_opportunity": False,
    "opportunity_stage": None,
    "account": None,
    "product": None,
    "quantity": 1,
    "count": 1,
    "discount": None,
}

_VALID_STAGES = {
    "opportunity", "quote", "order", "activate", "usage", "invoice", "post",
}

# QuoteLineItem picklists (verified live against a Revenue Cloud R262 scratch
# org, API v67.0). Some term products carry a proration policy that requires
# both at place time.
_VALID_PERIOD_BOUNDARIES = {
    "AlignToCalendar", "Anniversary", "DayOfPeriod", "LastDayOfPeriod",
}
_VALID_BILLING_FREQUENCIES = {
    "MilestonePlan", "Monthly", "Quarterly", "Semi-Annual", "Annual",
}


class ConfigError(RuntimeError):
    """The config file is malformed or contains an invalid value."""


@dataclass
class UsageSpec:
    """Opt-in usage-consumption shape for a usage-based product line.

    Carries unresolved user intent: a ``UsageResource.Code`` (or ``None`` to use
    all of the product's bindings), per-row quantity range, journals-per-line
    count range, and an ``ActivityDate`` spread window. Bound to concrete
    resource/UoM ids at ``resolve_spec`` time once discovery has fetched the
    product's usage bindings.

    ``unit_of_measure`` overrides the resource's default UoM by ``UnitCode``;
    it requires an explicit ``resource`` (otherwise it's ambiguous which of a
    product's bindings the override applies to).
    """

    quantity: tuple[float, float]
    records_per_line: tuple[int, int]
    days_back: int = 0
    resource: Optional[str] = None
    unit_of_measure: Optional[str] = None


@dataclass
class ProductOption:
    """One product in a scenario's **pool**, with its own quantity/discount.

    A scenario places a random non-empty subset of its pool as quote lines (so a
    two-entry pool yields one OR both lines per transaction). ``sku`` ``None`` =>
    auto-discover the preferred product. ``quantity`` is an inclusive
    ``(min, max)`` integer range drawn **per line** (a scalar becomes ``(x, x)``);
    ``discount`` is the line-discount **percent**, same ``(min, max)`` shape, or
    ``None`` for no discount.
    """

    sku: Optional[str]
    quantity: tuple[int, int]
    discount: Optional[tuple[float, float]] = None
    # Proration period start (``PeriodBoundary``) + billing cadence
    # (``BillingFrequency``). Required at place time for products carrying a
    # proration policy (e.g. QB-LIC-CLOUD); not derivable from the selling model,
    # so set per product. ``None`` => omit from the line.
    period_boundary: Optional[str] = None
    billing_frequency: Optional[str] = None
    # Opt-in usage consumption; ``None`` => no TransactionJournals emitted.
    usage: Optional[UsageSpec] = None
    # Subscription term override. ``None`` => fall back to the scenario default
    # then the resolved PSM's PricingTerm. A bare-int config lands as
    # ``Term(N, None)`` here; the runner promotes ``unit`` from the resolved PSM.
    term: Optional[Term] = None
    # ProductSellingModel.Name pin for SKUs with multiple active PBEs (one per
    # selling model). ``None`` => let ``resolve_product`` fail loudly if the
    # SKU is ambiguous, rather than silently picking one.
    selling_model: Optional[str] = None
    # Explicit EndDate override. ``None`` => let the platform derive EndDate
    # from StartDate + SubscriptionTerm/Unit (the default Branch A behavior).
    # Set => the harness writes EndDate on the line, which the platform honors
    # and prorates PricingTermCount against (~0.27% drift vs derived EndDate
    # in the worst case). Requires a TermDefined product with a `term:` also
    # set -- co-term shorthand is incoherent without a cadence.
    end_date: Optional[EndDateOverride] = None


@dataclass
class ScenarioSpec:
    """One un-resolved transaction shape, run ``count`` times.

    ``account`` ``None`` => auto-discover the default billing-ready account.
    ``products`` is the line **pool** (always >= 1 entry); each transaction
    places a random non-empty subset of it (see :class:`ProductOption`).
    """

    account: Optional[str]
    products: list[ProductOption]
    target_stage: str
    with_opportunity: bool
    opportunity_stage: Optional[str]
    count: int
    # Inclusive ``(lo, hi)`` range the quote's line StartDate is drawn from, per
    # transaction -- the knob for spreading quotes over time. ``None`` => the
    # lifecycle defaults each line StartDate to today. A single date is drawn once
    # per transaction and applied to all of that quote's lines.
    start_date: Optional[tuple[date, date]] = None
    # Scenario-level subscription term default applied to every line that
    # doesn't pin its own ``term``. ``None`` => fall back to each resolved PSM's
    # declared PricingTerm.
    term: Optional[Term] = None
    # Scenario-level EndDate override applied to every TermDefined line that
    # doesn't pin its own ``end_date``. Co-term shorthand: a scenario can pin
    # one EndDate so all of a quote's lines end on the same calendar anchor.
    end_date: Optional[EndDateOverride] = None


def _load_file(path: str) -> dict:
    if not os.path.exists(path):
        raise ConfigError(f"config file not found: {path}")
    with open(path) as f:
        text = f.read()
    # JSON is a YAML subset; PyYAML parses both, but only import it when needed.
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - yaml is a hard dep in practice
        raise ConfigError(
            "PyYAML is required to read --config files (pip install pyyaml)"
        ) from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"could not parse config {path}: {exc}") from exc
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"config {path} must be a mapping at the top level")
    return data


def _cli_overrides(args: Any) -> dict[str, Any]:
    """Pick the CLI flags the user explicitly set (None == not set).

    ``with_opportunity`` is store_true: only a True value is treated as an
    override (a flag can't express "force false").
    """
    overrides: dict[str, Any] = {}
    if getattr(args, "target_stage", None) is not None:
        overrides["target_stage"] = args.target_stage
    if getattr(args, "account", None) is not None:
        overrides["account"] = args.account
    if getattr(args, "product", None) is not None:
        overrides["product"] = args.product
    if getattr(args, "opportunity_stage", None) is not None:
        overrides["opportunity_stage"] = args.opportunity_stage
    if getattr(args, "count", None) is not None:
        overrides["count"] = args.count
    if getattr(args, "with_opportunity", False):
        overrides["with_opportunity"] = True
    return overrides


def _coerce_discount(value: Any, where: str) -> Optional[tuple[float, float]]:
    """Normalize a discount into an inclusive ``(min, max)`` percent range.

    Accepts a scalar (``10`` -> ``(10, 10)``) or a 2-element list/tuple
    (``[5, 25]`` -> ``(5.0, 25.0)``). Returns ``None`` for an unset discount.
    Percents must be within ``0..100`` and ``min <= max``.
    """
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ConfigError(
                f"{where}: discount range must have exactly 2 values [min, max]"
            )
        lo, hi = value
    else:
        lo = hi = value
    try:
        lo, hi = float(lo), float(hi)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{where}: discount must be number(s)") from exc
    if lo > hi:
        raise ConfigError(f"{where}: discount min ({lo}) > max ({hi})")
    if lo < 0 or hi > 100:
        raise ConfigError(f"{where}: discount percent must be within 0..100")
    return (lo, hi)


def _coerce_term_unit(value: Any, where: str) -> str:
    """Normalize a PricingTermUnit value with the one allowed alias.

    Salesforce picklists are case-sensitive on write; the harness mirrors
    that strictness rather than silently lower/title-casing input.
    """
    if not isinstance(value, str):
        raise ConfigError(f"{where}: term.unit must be a string")
    canon = _TERM_UNIT_ALIASES.get(value, value)
    if canon not in VALID_TERM_UNITS:
        raise ConfigError(
            f"{where}: term.unit must be one of "
            f"{', '.join(sorted(VALID_TERM_UNITS))} (got {value!r}; "
            f"only alias is 'Years' -> 'Annual')"
        )
    return canon


def _coerce_term(value: Any, where: str) -> Optional[Term]:
    """Normalize a ``term`` config into a :class:`Term`.

    Two shapes:

    * Bare positive int (``term: 36``) -> ``Term(36, None)``. The runner
      promotes ``unit`` from the resolved PSM's ``PricingTermUnit`` once the
      PBE is known, since the platform binds the line to a PBE whose model
      already declares a unit.
    * Mapping (``term: {count: 3, unit: Annual}``) -> ``Term(3, "Annual")``.
      The runner enforces ``unit == psm.pricing_term_unit`` post-resolution
      (after ``Years -> Annual`` aliasing) and raises ``ConfigError`` on a
      mismatch; switching PSMs is never implicit.
    """
    if value is None:
        return None
    if isinstance(value, bool):  # Python: True/False are ints. Reject explicitly.
        raise ConfigError(f"{where}: term must be an int or a mapping (got bool)")
    if isinstance(value, int):
        if value < 1:
            raise ConfigError(f"{where}: term must be >= 1 (got {value})")
        if value > _MAX_TERM_COUNT:
            raise ConfigError(
                f"{where}: term must be <= {_MAX_TERM_COUNT} (got {value}); "
                f"typo? remember the unit comes from the selling model"
            )
        return Term(count=value, unit=None)
    if isinstance(value, dict):
        if "count" not in value:
            raise ConfigError(f"{where}: term mapping requires 'count'")
        try:
            count = int(value["count"])
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"{where}: term.count must be an integer") from exc
        if count < 1:
            raise ConfigError(f"{where}: term.count must be >= 1 (got {count})")
        if count > _MAX_TERM_COUNT:
            raise ConfigError(
                f"{where}: term.count must be <= {_MAX_TERM_COUNT} (got {count})"
            )
        unit_raw = value.get("unit")
        unit = _coerce_term_unit(unit_raw, where) if unit_raw is not None else None
        return Term(count=count, unit=unit)
    raise ConfigError(
        f"{where}: term must be an int or a mapping {{count, unit}} "
        f"(got {type(value).__name__})"
    )


# Defensive upper bound on a relative end_date offset. Sized so that no realistic
# multi-year subscription (max term 120 of any unit) gets clipped, but a typo
# like ``"3650d"`` is caught.
_MAX_END_DATE_OFFSET = 365 * 20  # 20 years in days
_MAX_END_DATE_MONTHS = 12 * 20   # 20 years in calendar months


def _parse_relative_end_date(token: str, where: str) -> EndDateOverride:
    """Parse a ``"<int><unit>"`` token into an :class:`EndDateOverride`.

    Units: ``d`` (days), ``mo`` (calendar months), ``q`` (quarters = 3 mo),
    ``y`` (years = 12 mo). The bare ``"m"`` suffix is rejected as ambiguous --
    the user must spell ``"mo"``.
    """
    # Longest suffix first so ``"mo"`` matches before ``"o"`` would.
    for suffix in ("mo", "d", "q", "y"):
        if token.endswith(suffix):
            digits = token[: -len(suffix)]
            break
    else:
        if token.endswith("m"):
            raise ConfigError(
                f"{where}: end_date unit 'm' is ambiguous -- use 'mo' for months "
                f"(got {token!r})"
            )
        raise ConfigError(
            f"{where}: end_date relative offset must end in one of "
            f"{', '.join(sorted(END_DATE_UNITS))} (got {token!r})"
        )
    try:
        count = int(digits)
    except ValueError as exc:
        raise ConfigError(
            f"{where}: end_date offset must be <int><unit> (got {token!r})"
        ) from exc
    if count <= 0:
        raise ConfigError(
            f"{where}: end_date offset must be positive (got {token!r}); "
            f"end_date only supports forward offsets from StartDate"
        )
    if suffix == "d":
        if count > _MAX_END_DATE_OFFSET:
            raise ConfigError(
                f"{where}: end_date offset {count}d exceeds {_MAX_END_DATE_OFFSET}d "
                f"(20 years); typo?"
            )
        return EndDateOverride(days=count)
    months = {"mo": count, "q": count * 3, "y": count * 12}[suffix]
    if months > _MAX_END_DATE_MONTHS:
        raise ConfigError(
            f"{where}: end_date offset {token} exceeds {_MAX_END_DATE_MONTHS} "
            f"months (20 years); typo?"
        )
    return EndDateOverride(months=months)


def _coerce_end_date(value: Any, where: str) -> Optional[EndDateOverride]:
    """Normalize an ``end_date`` config into an :class:`EndDateOverride`.

    Accepts:

      * ``None`` -> ``None`` (platform derives EndDate from StartDate+Term).
      * Absolute ISO date: ``"2027-01-14"`` or a YAML-parsed ``date``.
      * Bare positive int: ``364`` -> 364 days forward from StartDate.
      * Suffixed string: ``"12mo"``, ``"1y"``, ``"3q"``, ``"364d"``.

    Rejected:

      * Negative offsets / zero (forward-only by design).
      * Ambiguous ``"12m"`` (must spell ``"12mo"``).
      * Any other unit suffix.

    The override is resolved against the line's drawn StartDate at lifecycle
    time -- carried unresolved here so a scenario-level ``end_date`` co-terms
    every line on a quote to the same calendar anchor.
    """
    if value is None:
        return None
    if isinstance(value, bool):  # Python: True/False are ints. Reject explicitly.
        raise ConfigError(f"{where}: end_date must not be a bool")
    if isinstance(value, date):  # PyYAML parses bare YYYY-MM-DD as a date.
        return EndDateOverride(absolute=value)
    if isinstance(value, int):
        if value <= 0:
            raise ConfigError(
                f"{where}: end_date offset must be positive (got {value}); "
                f"end_date only supports forward offsets from StartDate"
            )
        if value > _MAX_END_DATE_OFFSET:
            raise ConfigError(
                f"{where}: end_date offset {value} days exceeds "
                f"{_MAX_END_DATE_OFFSET} (20 years); typo?"
            )
        return EndDateOverride(days=value)
    if isinstance(value, str):
        tok = value.strip()
        if not tok:
            raise ConfigError(f"{where}: end_date must not be empty")
        # Absolute ISO date string.
        try:
            return EndDateOverride(absolute=date.fromisoformat(tok))
        except ValueError:
            pass  # not an ISO date -- try the relative-offset path.
        return _parse_relative_end_date(tok, where)
    raise ConfigError(
        f"{where}: end_date must be an ISO date, an int (days), or "
        f"<int><unit> (d/mo/q/y); got {type(value).__name__}"
    )


def _coerce_quantity(value: Any, where: str) -> tuple[int, int]:
    """Normalize a quantity into an inclusive ``(min, max)`` integer range.

    Accepts a scalar (``5`` -> ``(5, 5)``) or a 2-element list/tuple
    (``[1, 10]`` -> ``(1, 10)``). Both bounds must be integers >= 1 and
    ``min <= max``.
    """
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ConfigError(
                f"{where}: quantity range must have exactly 2 values [min, max]"
            )
        lo, hi = value
    else:
        lo = hi = value
    def as_int(raw: Any, label: str) -> int:
        if isinstance(raw, float) and not raw.is_integer():
            raise ConfigError(f"{where}: quantity {label} must be an integer")
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"{where}: quantity must be integer(s)") from exc

    lo, hi = as_int(lo, "min"), as_int(hi, "max")
    if lo > hi:
        raise ConfigError(f"{where}: quantity min ({lo}) > max ({hi})")
    if lo < 1:
        raise ConfigError(f"{where}: quantity must be >= 1 (got {lo})")
    return (lo, hi)


def _coerce_float_range(value: Any, where: str, field: str) -> tuple[float, float]:
    """Normalize a numeric range into ``(lo, hi)`` floats. Scalar => ``(x, x)``."""
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ConfigError(
                f"{where}: {field} range must have exactly 2 values [min, max]"
            )
        lo, hi = value
    else:
        lo = hi = value
    try:
        lo, hi = float(lo), float(hi)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{where}: {field} must be number(s)") from exc
    if lo > hi:
        raise ConfigError(f"{where}: {field} min ({lo}) > max ({hi})")
    if lo < 0:
        raise ConfigError(f"{where}: {field} must be >= 0 (got {lo})")
    return (lo, hi)


def _coerce_int_range(
    value: Any, where: str, field: str, *, minimum: int = 1
) -> tuple[int, int]:
    """Normalize a non-negative int range. Scalar => ``(x, x)``."""
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ConfigError(
                f"{where}: {field} range must have exactly 2 values [min, max]"
            )
        lo, hi = value
    else:
        lo = hi = value

    def as_int(raw: Any, label: str) -> int:
        if isinstance(raw, float) and not raw.is_integer():
            raise ConfigError(f"{where}: {field} {label} must be an integer")
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"{where}: {field} must be integer(s)") from exc

    lo, hi = as_int(lo, "min"), as_int(hi, "max")
    if lo > hi:
        raise ConfigError(f"{where}: {field} min ({lo}) > max ({hi})")
    if lo < minimum:
        raise ConfigError(f"{where}: {field} must be >= {minimum} (got {lo})")
    return (lo, hi)


def _coerce_usage(raw: Any, where: str) -> Optional[UsageSpec]:
    """Build a :class:`UsageSpec` from a product entry's ``usage:`` block."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: 'usage' must be a mapping")
    if "quantity" not in raw:
        raise ConfigError(f"{where}: usage requires 'quantity' (number or [min, max])")
    if "records_per_line" not in raw:
        raise ConfigError(
            f"{where}: usage requires 'records_per_line' (int or [min, max])"
        )

    quantity = _coerce_float_range(raw["quantity"], where, "usage.quantity")
    records = _coerce_int_range(
        raw["records_per_line"], where, "usage.records_per_line", minimum=1
    )
    days_raw = raw.get("days_back", 0)
    try:
        days_back = int(days_raw)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{where}: usage.days_back must be an integer") from exc
    if days_back < 0:
        raise ConfigError(f"{where}: usage.days_back must be >= 0 (got {days_back})")

    resource = raw.get("resource")
    if resource is not None and not isinstance(resource, str):
        raise ConfigError(f"{where}: usage.resource must be a string code")
    uom = raw.get("unit_of_measure")
    if uom is not None and not isinstance(uom, str):
        raise ConfigError(f"{where}: usage.unit_of_measure must be a string UnitCode")
    if uom is not None and resource is None:
        raise ConfigError(
            f"{where}: usage.unit_of_measure requires an explicit usage.resource"
        )

    return UsageSpec(
        quantity=quantity,
        records_per_line=records,
        days_back=days_back,
        resource=resource,
        unit_of_measure=uom,
    )


def _parse_date_token(value: Any, where: str) -> date:
    """Resolve one date token to a concrete ``date``.

    Accepts ``today``, a relative day offset (``+30`` / ``-15`` / ``+30d`` ==
    today +/- N days), or an ISO ``YYYY-MM-DD`` string. Used for both ends of a
    ``start_date`` range and for a ``around:`` anchor.
    """
    if isinstance(value, date):  # PyYAML parses bare YYYY-MM-DD as a date
        return value
    if not isinstance(value, str):
        raise ConfigError(f"{where}: date must be a string (got {value!r})")
    tok = value.strip()
    if tok.lower() == "today":
        return date.today()
    if tok and tok[0] in "+-":
        digits = tok[1:-1] if tok.lower().endswith("d") else tok[1:]
        try:
            days = int(digits)
        except ValueError as exc:
            raise ConfigError(
                f"{where}: relative date must be +N / -N / +Nd (got {value!r})"
            ) from exc
        from datetime import timedelta
        return date.today() + timedelta(days=(-days if tok[0] == "-" else days))
    try:
        return date.fromisoformat(tok)
    except ValueError as exc:
        raise ConfigError(
            f"{where}: date must be ISO YYYY-MM-DD, 'today', or +/-N (got {value!r})"
        ) from exc


def _coerce_start_date(value: Any, where: str) -> Optional[tuple[date, date]]:
    """Normalize a ``start_date`` spec into an inclusive ``(lo, hi)`` date range.

    A concrete date is drawn uniformly from ``[lo, hi]`` per transaction (so a
    range spreads quotes over time). Accepts:

      * unset / ``None`` -> ``None`` (lifecycle defaults the line StartDate to today)
      * exact: ``"2026-03-15"`` / ``today`` / ``"+30"`` -> ``(d, d)``
      * range list: ``["2026-01-01", "2026-03-31"]`` -> ``(lo, hi)``
      * range map: ``{from: ..., to: ...}`` -> ``(lo, hi)``
      * window map: ``{around: <anchor>, plus_or_minus: N}`` -> ``(anchor-N, anchor+N)``
        (``around`` defaults to today; ``plus_or_minus`` is a day count >= 0)
    """
    if value is None:
        return None
    if isinstance(value, dict):
        if "around" in value or "anchor" in value:
            anchor = _parse_date_token(
                value.get("around", value.get("anchor", "today")), where)
            pm_raw = value.get("plus_or_minus", value.get("pm", 0))
            try:
                pm = int(pm_raw)
            except (TypeError, ValueError) as exc:
                raise ConfigError(
                    f"{where}: start_date plus_or_minus must be an integer"
                ) from exc
            if pm < 0:
                raise ConfigError(f"{where}: start_date plus_or_minus must be >= 0")
            from datetime import timedelta
            return (anchor - timedelta(days=pm), anchor + timedelta(days=pm))
        if "from" in value or "to" in value:
            lo = _parse_date_token(value["from"], where) if "from" in value else date.today()
            hi = _parse_date_token(value["to"], where) if "to" in value else lo
        else:
            raise ConfigError(
                f"{where}: start_date map needs 'around'/'anchor' or 'from'/'to'"
            )
    elif isinstance(value, (list, tuple)):
        if len(value) != 2:
            raise ConfigError(
                f"{where}: start_date range must have exactly 2 values [from, to]"
            )
        lo = _parse_date_token(value[0], where)
        hi = _parse_date_token(value[1], where)
    else:
        d = _parse_date_token(value, where)
        return (d, d)
    if lo > hi:
        raise ConfigError(
            f"{where}: start_date range start ({lo}) is after end ({hi})"
        )
    return (lo, hi)


def _coerce_enum(
    value: Any, where: str, field: str, valid: set[str]
) -> Optional[str]:
    """Validate an optional picklist value against ``valid`` (None => omit)."""
    if value is None:
        return None
    if not isinstance(value, str) or value not in valid:
        raise ConfigError(
            f"{where}: {field} must be one of {', '.join(sorted(valid))} (got {value!r})"
        )
    return value


def _coerce_product_option(
    raw: Any, where: str, default_qty: Any, default_discount: Any
) -> ProductOption:
    """Build one :class:`ProductOption` from a ``products[]`` entry (a mapping).

    Per-entry ``quantity``/``discount`` win over the scenario-level fallbacks
    (``default_qty``/``default_discount``), mirroring how a scenario field wins
    over ``defaults``. ``period_boundary``/``billing_frequency`` are per-product
    only (no scenario-level fallback) -- they're product-specific proration knobs.
    """
    if not isinstance(raw, dict) or not raw.get("sku"):
        raise ConfigError(f"{where}: each product needs an 'sku'")
    qty = raw["quantity"] if "quantity" in raw else default_qty
    disc = raw["discount"] if "discount" in raw else default_discount
    selling_model = raw.get("selling_model")
    if selling_model is not None and not isinstance(selling_model, str):
        raise ConfigError(f"{where}: selling_model must be a string")
    return ProductOption(
        sku=raw["sku"],
        quantity=_coerce_quantity(qty, where),
        discount=_coerce_discount(disc, where),
        period_boundary=_coerce_enum(
            raw.get("period_boundary"), where, "period_boundary",
            _VALID_PERIOD_BOUNDARIES),
        billing_frequency=_coerce_enum(
            raw.get("billing_frequency"), where, "billing_frequency",
            _VALID_BILLING_FREQUENCIES),
        usage=_coerce_usage(raw.get("usage"), where),
        term=_coerce_term(raw.get("term"), where),
        selling_model=selling_model,
        end_date=_coerce_end_date(raw.get("end_date"), where),
    )


def _coerce_spec(merged: dict[str, Any], where: str) -> ScenarioSpec:
    stage = merged.get("target_stage") or "post"
    if stage not in _VALID_STAGES:
        raise ConfigError(
            f"{where}: invalid target_stage '{stage}' "
            f"(valid: {', '.join(sorted(_VALID_STAGES))})"
        )

    try:
        count = int(merged.get("count", 1))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{where}: count must be an integer") from exc
    if count < 1:
        raise ConfigError(f"{where}: count must be >= 1 (got {count})")

    # Scenario-level quantity/discount are the fallback each product entry
    # inherits unless it sets its own; `product:` is shorthand for a one-entry
    # pool. `products:` is the pool a transaction draws a random subset from.
    default_qty = merged.get("quantity", 1)
    default_discount = merged.get("discount")
    products_raw = merged.get("products")
    if products_raw:
        if not isinstance(products_raw, list):
            raise ConfigError(f"{where}: 'products' must be a list")
        products = [
            _coerce_product_option(p, f"{where}.products[{i}]", default_qty, default_discount)
            for i, p in enumerate(products_raw)
        ]
    else:
        # No explicit pool: a single (possibly auto-discovered) product line.
        # Scenario-level proration knobs apply to this one line if set.
        products = [
            ProductOption(
                sku=merged.get("product"),
                quantity=_coerce_quantity(default_qty, where),
                discount=_coerce_discount(default_discount, where),
                period_boundary=_coerce_enum(
                    merged.get("period_boundary"), where, "period_boundary",
                    _VALID_PERIOD_BOUNDARIES),
                billing_frequency=_coerce_enum(
                    merged.get("billing_frequency"), where, "billing_frequency",
                    _VALID_BILLING_FREQUENCIES),
            )
        ]

    return ScenarioSpec(
        account=merged.get("account"),
        products=products,
        target_stage=stage,
        with_opportunity=bool(merged.get("with_opportunity", False)),
        opportunity_stage=merged.get("opportunity_stage"),
        count=count,
        start_date=_coerce_start_date(merged.get("start_date"), where),
        term=_coerce_term(merged.get("term"), where),
        end_date=_coerce_end_date(merged.get("end_date"), where),
    )


def load_scenarios(args: Any) -> list[ScenarioSpec]:
    """Resolve the run into a list of un-resolved scenario specs.

    No ``--config`` -> one spec from CLI flags + built-ins. With ``--config``,
    each entry under ``scenarios:`` becomes a spec (layered defaults < config
    ``defaults`` < CLI < per-scenario); a config with no ``scenarios:`` yields a
    single spec from the merged defaults, honoring ``volume.scenarios`` as count.
    """
    cli = _cli_overrides(args)
    config_path = getattr(args, "config", None)

    if not config_path:
        merged = {**_BUILTIN_DEFAULTS, **cli}
        return [_coerce_spec(merged, "cli")]

    data = _load_file(config_path)
    config_defaults = data.get("defaults") or {}
    if not isinstance(config_defaults, dict):
        raise ConfigError("config 'defaults' must be a mapping")
    base = {**_BUILTIN_DEFAULTS, **config_defaults, **cli}

    scenarios = data.get("scenarios")
    if scenarios is None:
        # No explicit scenarios: one merged spec; volume.scenarios sets count
        # unless CLI --count overrode it.
        volume = data.get("volume") or {}
        if "count" not in cli and isinstance(volume, dict) and volume.get("scenarios"):
            base = {**base, "count": volume["scenarios"]}
        return [_coerce_spec(base, "defaults")]

    if not isinstance(scenarios, list) or not scenarios:
        raise ConfigError("config 'scenarios' must be a non-empty list")
    specs: list[ScenarioSpec] = []
    for i, raw in enumerate(scenarios):
        if not isinstance(raw, dict):
            raise ConfigError(f"scenarios[{i}] must be a mapping")
        # Per-scenario fields win over CLI/defaults, EXCEPT account/product which
        # a CLI override should not silently rewrite across a multi-account
        # config; only let CLI override those when the scenario didn't pin them.
        merged = {**base, **raw}
        specs.append(_coerce_spec(merged, f"scenarios[{i}]"))
    return specs
