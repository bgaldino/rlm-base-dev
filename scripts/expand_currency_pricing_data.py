#!/usr/bin/env python3
"""Expand a USD-only SFDMU pricing plan into multi-currency variants.

Reads the plan's ``CurrencyType.csv`` for live conversion rates and emits, for
each base-currency (USD) row, one variant row per target currency in the
currency-scoped pricing CSVs (PricebookEntry, CostBookEntry, and the adjustment
child objects — AttributeBasedAdjustment, BundleBasedAdjustment,
PriceAdjustmentTier, PricebookEntryDerivedPrice).

``PriceAdjustmentSchedule`` is **not** expanded: there is one schedule per type
(the platform-seeded USD "Standard …" records). Every currency's adjustment
children reference that single schedule by ``PriceAdjustmentSchedule.Name`` and
are disambiguated at pricing time by their own ``CurrencyIsoCode`` — the
adjustment decision tables match on ``PriceAdjustmentScheduleId`` AND
``CurrencyIsoCode``. (Duplicating the schedule per currency breaks adjustment
lookups, because the pricing procedure pins each adjustment step to a single
schedule Id via ``find_replace`` token resolution — ``… WHERE name = 'Standard
…' LIMIT 1``.)

**Idempotent & re-runnable.** Existing generated-currency rows are stripped and
regenerated from the base rows, so you can re-run this after
``cci task run update_currency_rates_csv`` to refresh converted prices to the
current rates. USD base rows are preserved byte-for-byte; only generated rows
are (re)written.

Conversion rules
----------------
* **Monetary** fields (``PricebookEntry.UnitPrice``, ``CostBookEntry.Cost``, and
  ``Override``/``Amount``-type ``AttributeBasedAdjustment.AdjustmentValue`` /
  ``BundleBasedAdjustment.AdjustmentValue``) = ``base_amount * ConversionRate[target]
  / ConversionRate[base]`` (a USD base reduces to ``USD * ConversionRate`` since
  ``ConversionRate[USD] == 1``), rounded
  to the nearest ``--round`` step (default ``0.50``). Currencies whose
  ``CurrencyType.DecimalPlaces == 0`` (e.g. JPY) round to a whole number.
* **Percentage / formula / bound** values (BundleBasedAdjustment %,
  PriceAdjustmentTier %, PricebookEntryDerivedPrice formulas) are copied
  unchanged — only the currency changes.
* The currency is replaced **by position** inside every ``$$``-composite and
  nested-reference column (robust to SFDMU dropping empty key components), never
  a blind string swap, so product names / cost-book names are never corrupted.

Usage
-----
    python scripts/expand_currency_pricing_data.py                 # dry-run, default plan
    python scripts/expand_currency_pricing_data.py --apply
    python scripts/expand_currency_pricing_data.py --plan datasets/sfdmu/qb/ja/qb-pricing --apply
    python scripts/expand_currency_pricing_data.py --currencies GBP,EUR,AUD,CAD,CHF,JPY --round 0.5
"""
import argparse
import csv
import io
import os
import sys
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

DEFAULT_PLAN = "datasets/sfdmu/qb/en-US/qb-pricing"
DEFAULT_BASE = "USD"
DEFAULT_CURRENCIES = "GBP,EUR,AUD,CAD,CHF,JPY"
DEFAULT_ROUND = "0.5"


def _amount_adj(row):
    """AttributeBasedAdjustment / BundleBasedAdjustment: convert only currency-amount types."""
    return row.get("AdjustmentType", "") in ("Override", "Amount")


def _always(_row):
    return True


# filename -> (monetary column, predicate). None => copy every value unchanged (currency only).
#
# PriceAdjustmentSchedule is intentionally ABSENT: there is exactly ONE schedule
# per type (the platform-seeded USD "Standard …" records), shared by every
# currency. The per-currency adjustment children below each carry their own
# CurrencyIsoCode and reference that single schedule by Name
# (PriceAdjustmentSchedule.Name), so the schedule is never expanded per currency.
CONFIG = {
    "PricebookEntry.csv": ("UnitPrice", _always),
    "CostBookEntry.csv": ("Cost", _always),
    "AttributeBasedAdjustment.csv": ("AdjustmentValue", _amount_adj),
    "BundleBasedAdjustment.csv": ("AdjustmentValue", _amount_adj),
    "PriceAdjustmentTier.csv": (None, None),          # all AdjustmentPercentage
    "PricebookEntryDerivedPrice.csv": (None, None),   # formula-based
}


def load_currency_table(plan):
    """Return (rates: {iso: Decimal}, whole_number_currencies: set) from CurrencyType.csv."""
    path = os.path.join(plan, "CurrencyType.csv")
    if not os.path.isfile(path):
        sys.exit(f"error: {path} not found — cannot read conversion rates.")
    rates, whole = {}, set()
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            rates[r["IsoCode"]] = Decimal(r["ConversionRate"])
            if int(r["DecimalPlaces"]) == 0:
                whole.add(r["IsoCode"])
    return rates, whole


def round_amount(base_val, ccy, base, rates, whole, step):
    step_q = Decimal("1") if ccy in whole else step
    # base_val is denominated in `base`; ConversionRates are corporate-relative,
    # so the base->target cross-rate is rates[ccy] / rates[base] (rates[USD]=1.0,
    # so a USD base reduces to base_val * rates[ccy]).
    converted = base_val * rates[ccy] / rates[base]
    n = (converted / step_q).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return n * step_q


def fmt(dec):
    if dec == dec.to_integral_value():
        return str(int(dec))
    return format(dec, "f").rstrip("0").rstrip(".")


def _tokens(header):
    return header.split("$$")[-1].split("$") if "$$" in header else None


def set_currency(header, value, target, src):
    """Replace the currency segment in a composite/nested-ref cell by position from the right.

    SFDMU $$ composite keys drop empty components, so the segment count is not the
    token count. CurrencyIsoCode (and any tokens after it, e.g. an always-populated
    trailing EffectiveFrom) are present, so we index from the right and assert the
    located segment currently holds the source currency.
    """
    if header == "CurrencyIsoCode":
        return target
    toks = _tokens(header)
    if not toks or "CurrencyIsoCode" not in toks:
        return value
    if value == "":
        return value
    after = len(toks) - 1 - toks.index("CurrencyIsoCode")
    parts = value.split(";")
    idx = len(parts) - 1 - after
    if idx < 0 or parts[idx] != src:
        raise ValueError(
            f"currency segment not found: header={header!r} value={value!r} "
            f"idx={idx} expected={src!r}"
        )
    parts[idx] = target
    return ";".join(parts)


def serialize(rowdict, fieldnames):
    buf = io.StringIO()
    csv.writer(buf, lineterminator="").writerow([rowdict[fn] for fn in fieldnames])
    return buf.getvalue()


def make_variant(row, ccy, base, fieldnames, money_col, pred, rates, whole, step):
    src = row["CurrencyIsoCode"]
    v = {fn: set_currency(fn, row[fn], ccy, src) for fn in fieldnames}
    if money_col:
        raw = (row.get(money_col) or "").strip()
        if raw and pred(row):
            d = Decimal(raw)
            if d != 0:
                v[money_col] = fmt(round_amount(d, ccy, base, rates, whole, step))
    return v


def process(plan, fname, money_col, pred, base, targets, rates, whole, step, apply):
    path = os.path.join(plan, fname)
    if not os.path.isfile(path):
        print(f"  {fname:34s} (absent — skipped)")
        return 0
    raw = open(path, newline="").read().splitlines()
    header_line, data_raw = raw[0], [l for l in raw[1:] if l != ""]
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if len(rows) != len(data_raw):
        sys.exit(f"{fname}: line/row misalignment ({len(rows)} vs {len(data_raw)}) — embedded newline?")

    out, base_count, sample = [header_line], 0, []
    for raw_line, row in zip(data_raw, rows):
        ccy = row["CurrencyIsoCode"]
        if ccy in targets:
            continue  # previously generated — dropped, regenerated below
        out.append(raw_line)  # base (or any non-target) row preserved verbatim
        if ccy == base:
            base_count += 1
            for t in targets:
                v = make_variant(row, t, base, fieldnames, money_col, pred, rates, whole, step)
                out.append(serialize(v, fieldnames))
                if money_col and len(sample) < 2 and t in ("GBP", "JPY"):
                    sample.append((row.get(money_col), t, v[money_col]))
    if apply:
        open(path, "w", newline="").write("\n".join(out) + "\n")
    added = base_count * len(targets)
    tag = f"   e.g. {sample}" if sample else ("   (currency-only copy)" if money_col is None else "")
    print(f"  {fname:34s} base={base_count:4d}  +{added:4d} -> {base_count * (len(targets) + 1):5d} total{tag}")
    return added


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", default=DEFAULT_PLAN, help=f"SFDMU plan dir (default: {DEFAULT_PLAN})")
    ap.add_argument("--base", default=DEFAULT_BASE, help=f"Base currency to expand from (default: {DEFAULT_BASE})")
    ap.add_argument("--currencies", default=DEFAULT_CURRENCIES,
                    help=f"Comma-separated target currencies (default: {DEFAULT_CURRENCIES})")
    ap.add_argument("--round", dest="step", default=DEFAULT_ROUND,
                    help=f"Rounding step for non-whole currencies (default: {DEFAULT_ROUND})")
    ap.add_argument("--apply", action="store_true", help="Write changes (default: dry-run)")
    args = ap.parse_args(argv)

    base = args.base.strip().upper()
    targets = [c.strip().upper() for c in args.currencies.split(",") if c.strip()]
    # --round must be a positive, finite number: round_amount divides by the step,
    # so 0 (or a non-numeric / non-finite value) would raise DivisionByZero / corrupt
    # output on the first monetary row. Fail fast with a clear message instead.
    try:
        step = Decimal(args.step)
    except (InvalidOperation, ValueError):
        sys.exit(f"error: --round {args.step!r} is not a valid number")
    if not step.is_finite() or step <= 0:
        sys.exit(f"error: --round must be a positive, finite number (got {args.step!r})")
    # Fail fast on inputs that would silently corrupt the CSVs under --apply:
    # a target equal to the base drops every base row (see process(): `if ccy in
    # targets: continue`) before it can generate variants, and duplicate targets
    # emit duplicate SFDMU external-id keys.
    if base in targets:
        sys.exit(f"error: base currency {base} must not appear in --currencies targets ({targets})")
    dupes = sorted({c for c in targets if targets.count(c) > 1})
    if dupes:
        sys.exit(f"error: duplicate target currencies in --currencies: {dupes}")
    rates, whole = load_currency_table(args.plan)
    if base not in rates:
        sys.exit(f"error: base currency {base} has no ConversionRate in {args.plan}/CurrencyType.csv "
                 f"(the base must be present so its cross-rate can be resolved)")
    missing = [c for c in targets if c not in rates]
    if missing:
        sys.exit(f"error: no ConversionRate for {missing} in {args.plan}/CurrencyType.csv")

    print(f"Plan: {args.plan}")
    print("Rates: " + ", ".join(f"{c}={rates[c]}{' [whole]' if c in whole else ''}" for c in targets))
    print(f"{'APPLYING' if args.apply else 'DRY-RUN'} (base={base}, round={step}):")
    total = sum(
        process(args.plan, fname, mc, pr, base, targets, rates, whole, step, args.apply)
        for fname, (mc, pr) in CONFIG.items()
    )
    print(f"Total generated rows: {total}")
    if not args.apply:
        print("(dry-run — re-run with --apply to write)")


if __name__ == "__main__":
    main()
