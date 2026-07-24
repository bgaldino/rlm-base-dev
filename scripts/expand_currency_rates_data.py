#!/usr/bin/env python3
"""Expand the qb-rates plan across currencies.

Unlike prices, a usage *rate* carries its currency through its
``RateUnitOfMeasure`` — a unit in the ``CURRENCY`` UnitOfMeasureClass (``USD``,
``GBP``, ``JPY``, …). No rate object has a ``CurrencyIsoCode`` of its own, so a
GBP quote can only rate if a GBP-denominated ``RateCardEntry`` exists. This
script generates the missing per-currency entries (and their tier adjustments)
from the USD base rows.

What is expanded
----------------
* ``RateCardEntry`` rows whose ``RateUnitOfMeasure.UnitCode`` is the base
  currency. Token-denominated entries (``TOKEN-UOM``) are **not**
  currency-specific and are left untouched.
* ``RateAdjustmentByTier`` rows hanging off those entries.

Conversion rules
----------------
* ``Rate`` and ``Override``-type ``AdjustmentValue`` are money — converted via
  ``CurrencyType.ConversionRate`` (target / base).
* ``Percentage``-type ``AdjustmentValue`` is currency-neutral — copied as is.
* ``LowerBound`` / ``UpperBound`` are *consumption quantities* (minutes, TB,
  tokens), **not** money — copied as is.
* Rounding: currencies with ``DecimalPlaces == 0`` (JPY) round to a whole unit;
  otherwise 2 decimals at or above 1, and 4 decimals below 1 so small per-unit
  rates such as ``0.004`` keep their precision. A non-zero rate never rounds
  down to zero.

Existing non-base rows are **preserved** by default: the script only fills in
missing (product, rate card, usage resource, currency) combinations, so
hand-tuned or live-verified rates are never overwritten. Pass ``--regenerate``
to rebuild every non-base row from the base instead.
"""

import argparse
import csv
import io
import os
import sys
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

DEFAULT_RATES_PLAN = "datasets/sfdmu/qb/en-US/qb-rates"
DEFAULT_RATING_PLAN = "datasets/sfdmu/qb/en-US/qb-rating"
DEFAULT_PRICING_PLAN = "datasets/sfdmu/qb/en-US/qb-pricing"
DEFAULT_BASE = "USD"
DEFAULT_CURRENCIES = "GBP,EUR,AUD,CAD,CHF,JPY"

RCE_FILE = "RateCardEntry.csv"
RABT_FILE = "RateAdjustmentByTier.csv"


def load_currency_table(pricing_plan):
    """Return (rates, decimals) keyed by ISO code from CurrencyType.csv."""
    path = os.path.join(pricing_plan, "CurrencyType.csv")
    if not os.path.isfile(path):
        sys.exit(f"error: {path} not found — cannot read conversion rates.")
    rates, decimals = {}, {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            rates[r["IsoCode"]] = Decimal(r["ConversionRate"])
            decimals[r["IsoCode"]] = int(r["DecimalPlaces"])
    return rates, decimals


def load_currency_units(rating_plan):
    """Return the set of UnitCodes belonging to the CURRENCY UoM class."""
    path = os.path.join(rating_plan, "UnitOfMeasure.csv")
    if not os.path.isfile(path):
        sys.exit(f"error: {path} not found — cannot identify currency units.")
    with open(path, newline="") as fh:
        return {r["UnitCode"] for r in csv.DictReader(fh)
                if r["UnitOfMeasureClass.Code"] == "CURRENCY"}


def fmt(d):
    """Render a Decimal without scientific notation or trailing-zero noise."""
    s = format(d.normalize(), "f")
    return s


def convert_money(raw, ccy, base, rates, decimals):
    """Convert a money string from `base` to `ccy`, or return it unchanged if blank."""
    raw = (raw or "").strip()
    if not raw:
        return raw
    try:
        d = Decimal(raw)
    except InvalidOperation:
        return raw
    if d == 0:
        return raw
    converted = d * rates[ccy] / rates[base]
    if decimals[ccy] == 0:
        # Whole-unit currencies (JPY): amounts round to a whole unit, but a
        # *rate* is often sub-unit (¥0.65/minute). Rounding those to a whole yen
        # would flatten every tier of a tiered rate onto the same value and
        # destroy the tiering, so keep 2 decimals below 1.
        step = Decimal("1") if abs(converted) >= 1 else Decimal("0.01")
    else:
        # Below 1 keep 4 decimals so small per-unit rates (0.004) stay distinct.
        step = Decimal("0.01") if abs(converted) >= 1 else Decimal("0.0001")
    q = converted.quantize(step, rounding=ROUND_HALF_UP)
    if q == 0:
        q = step  # never collapse a real rate to zero
    return fmt(q)


def read_csv(path):
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        return rd.fieldnames, list(rd)


def write_csv(path, fieldnames, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    with open(path, "w", newline="") as fh:
        fh.write(buf.getvalue())


def swap_segment(composite, index, value):
    """Replace one ';'-delimited segment of an SFDMU composite key."""
    parts = composite.split(";")
    if index >= len(parts):
        return composite
    parts[index] = value
    return ";".join(parts)


def expand_rate_card_entries(plan, base, targets, rates, decimals, regenerate):
    path = os.path.join(plan, RCE_FILE)
    fields, rows = read_csv(path)
    key_col = fields[0]  # $$Product$RateCard.Name$UsageResource.Code$RateUoM.UnitCode
    if regenerate:
        rows = [r for r in rows if r["RateUnitOfMeasure.UnitCode"] not in targets]
    existing = {r[key_col] for r in rows}
    base_rows = [r for r in rows if r["RateUnitOfMeasure.UnitCode"] == base]
    added = []
    for src in base_rows:
        for ccy in targets:
            new = dict(src)
            new[key_col] = swap_segment(src[key_col], 3, ccy)
            if new[key_col] in existing:
                continue  # preserve what is already there
            new["RateUnitOfMeasure.UnitCode"] = ccy
            new["RateUnitOfMeasure.Name"] = ccy
            new["Rate"] = convert_money(src["Rate"], ccy, base, rates, decimals)
            added.append(new)
            existing.add(new[key_col])
    rows.extend(added)
    rows.sort(key=lambda r: r[key_col])
    write_csv(path, fields, rows)
    return len(base_rows), added, len(rows)


def expand_rate_adjustments(plan, base, targets, rates, decimals, regenerate):
    path = os.path.join(plan, RABT_FILE)
    fields, rows = read_csv(path)
    key_col = fields[0]   # $$Product$RateCard.Name$RateUoM.UnitCode$Resource$LB$UB
    rce_col = fields[8]   # RateCardEntry.$$Product$RateCard.Name$Resource$RateUoM.UnitCode
    if regenerate:
        rows = [r for r in rows if r["RateUnitOfMeasure.Name"] not in targets]
    existing = {r[key_col] for r in rows}
    base_rows = [r for r in rows if r["RateUnitOfMeasure.Name"] == base]
    added = []
    for src in base_rows:
        for ccy in targets:
            new = dict(src)
            new[key_col] = swap_segment(src[key_col], 2, ccy)
            if new[key_col] in existing:
                continue
            new[rce_col] = swap_segment(src[rce_col], 3, ccy)
            new["RateUnitOfMeasure.Name"] = ccy
            new["RateUnitOfMeasureName"] = ccy
            # Percentage adjustments are currency-neutral; only Override is money.
            # LowerBound/UpperBound are consumption quantities — never converted.
            if src["AdjustmentType"] == "Override":
                new["AdjustmentValue"] = convert_money(
                    src["AdjustmentValue"], ccy, base, rates, decimals)
            added.append(new)
            existing.add(new[key_col])
    rows.extend(added)
    rows.sort(key=lambda r: r[key_col])
    write_csv(path, fields, rows)
    return len(base_rows), added, len(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", default=DEFAULT_RATES_PLAN,
                    help=f"qb-rates plan dir (default: {DEFAULT_RATES_PLAN})")
    ap.add_argument("--rating-plan", default=DEFAULT_RATING_PLAN,
                    help=f"qb-rating plan dir, for the currency UoMs (default: {DEFAULT_RATING_PLAN})")
    ap.add_argument("--pricing-plan", default=DEFAULT_PRICING_PLAN,
                    help=f"plan dir holding CurrencyType.csv (default: {DEFAULT_PRICING_PLAN})")
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help=f"Base currency to expand from (default: {DEFAULT_BASE})")
    ap.add_argument("--currencies", default=DEFAULT_CURRENCIES,
                    help=f"Comma-separated target currencies (default: {DEFAULT_CURRENCIES})")
    ap.add_argument("--regenerate", action="store_true",
                    help="Rebuild every non-base row from the base instead of preserving existing ones")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = ap.parse_args(argv)

    base = args.base.strip().upper()
    targets = [c.strip().upper() for c in args.currencies.split(",") if c.strip()]
    if base in targets:
        sys.exit(f"error: base currency {base} must not appear in --currencies ({targets})")
    dupes = sorted({c for c in targets if targets.count(c) > 1})
    if dupes:
        sys.exit(f"error: duplicate target currencies: {dupes}")

    rates, decimals = load_currency_table(args.pricing_plan)
    missing_rate = [c for c in [base] + targets if c not in rates]
    if missing_rate:
        sys.exit(f"error: no ConversionRate for {missing_rate} in {args.pricing_plan}/CurrencyType.csv")

    # A rate can only be denominated in a currency that exists as a CURRENCY-class
    # UnitOfMeasure — without it the generated RateCardEntry cannot resolve its
    # RateUnitOfMeasure and the load fails.
    units = load_currency_units(args.rating_plan)
    missing_uom = [c for c in [base] + targets if c not in units]
    if missing_uom:
        sys.exit(f"error: no CURRENCY UnitOfMeasure for {missing_uom} in "
                 f"{args.rating_plan}/UnitOfMeasure.csv — add it before expanding rates.")

    print(f"Plan: {args.plan}")
    print("Rates: " + ", ".join(
        f"{c}={rates[c]}{' [whole]' if decimals[c] == 0 else ''}" for c in targets))
    mode = "REGENERATE" if args.regenerate else "PRESERVE existing"
    print(f"{'APPLYING' if args.apply else 'DRY-RUN'} (base={base}, {mode}):")

    if not args.apply:
        # Work on copies so a dry-run never touches the tree.
        import shutil, tempfile
        tmp = tempfile.mkdtemp()
        work = os.path.join(tmp, "plan")
        shutil.copytree(args.plan, work)
    else:
        work = args.plan

    n_base, rce_added, rce_total = expand_rate_card_entries(
        work, base, targets, rates, decimals, args.regenerate)
    print(f"  {RCE_FILE:28s} base={n_base:3d}  +{len(rce_added):3d} -> {rce_total:4d} total")
    for a in rce_added[:4]:
        print(f"      e.g. {a[list(a)[0]]}  rate={a['Rate'] or '(tier-driven)'}")
    if len(rce_added) > 4:
        print(f"      … {len(rce_added) - 4} more")

    n_base, rabt_added, rabt_total = expand_rate_adjustments(
        work, base, targets, rates, decimals, args.regenerate)
    print(f"  {RABT_FILE:28s} base={n_base:3d}  +{len(rabt_added):3d} -> {rabt_total:4d} total")
    ovr = [a for a in rabt_added if a["AdjustmentType"] == "Override"]
    for a in ovr[:3]:
        print(f"      e.g. {a[list(a)[0]]}  {a['AdjustmentType']}={a['AdjustmentValue']}")

    print(f"Total generated rows: {len(rce_added) + len(rabt_added)}")
    if not args.apply:
        print("(dry-run — re-run with --apply to write)")


if __name__ == "__main__":
    main()
