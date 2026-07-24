#!/usr/bin/env python3
"""Offline invariant tests for the QuantumBit multicurrency usage-rating data.

Self-contained — no pytest required (matches this repo's lightweight test
convention; see tests/test_context_plan_validator.py). Run from the repo root
with base Python:

    python tests/test_qb_multicurrency_data.py

Exits 0 when all checks pass, 1 otherwise. Reads only the committed CSVs in
``datasets/sfdmu/qb/en-US/{qb-rating,qb-rates,qb-pricing}`` — no org needed, so
this is safe to run in CI and as a pre-merge gate.

Each check corresponds to a defect that actually shipped (or nearly did) during
the multicurrency work, so the suite is a regression net rather than a
restatement of the data:

* ``tier_rce_has_adjustment``  — a Tier-type RateCardEntry with no
  RateAdjustmentByTier makes ``activate_rates`` fail the whole build with
  "Specify at least one tier adjustment for a Rate Card Entry of type tier".
* ``pack_products_have_no_purp`` — the platform REJECTS a
  ProductUsageResourcePolicy on a ``UsageModelType=Pack`` product
  (INVALID_INPUT). Two such rows silently failed to load on every build.
* ``every_pur_has_rate_card_entry`` — a ProductUsageResource with no rate card
  entry raises "No effective rate card entry available" in the Usage Product
  Validator (QB-CMT-TKN-FLAT shipped this way).
* ``currency_uom_prerequisite`` — a rate is denominated by its
  RateUnitOfMeasure, so a per-currency RateCardEntry cannot load unless a
  matching ``CURRENCY``-class UnitOfMeasure exists in qb-rating.
* ``currency_coverage_uniform`` — a currency missing an entry cannot rate at
  all; there is no runtime conversion from the USD row.
* ``percentages_currency_neutral`` / ``bounds_not_converted`` — percentage
  adjustments and tier bounds (consumption quantities) must never be converted.
* ``money_conversion_sane`` — converted money must track
  CurrencyType.ConversionRate, and tiered rates must stay distinct after
  rounding (whole-yen rounding once flattened four JPY tiers onto ¥1).
"""
import csv
import os
import sys
from decimal import Decimal

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RATING = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-rating")
RATES = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-rates")
PRICING = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-pricing")

BASE_CURRENCY = "USD"
TOKEN_UOM = "TOKEN-UOM"

# ProductUsageResources intentionally shipped without a rate card entry.
# UR-USD is Category=Currency (the monetary-commitment wallet); its commit
# discounts live on the -MTY usage resources instead. Deliberate, not a gap.
ALLOWED_PUR_WITHOUT_RCE = {("QB-MTY-CMT", "UR-USD")}

RESULTS = []


# ----------------------------------------------------------------------
# Harness
# ----------------------------------------------------------------------
def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def read(plan, filename):
    path = os.path.join(plan, filename)
    if not os.path.isfile(path):
        return None
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load():
    d = {
        "uom": read(RATING, "UnitOfMeasure.csv"),
        "product": read(RATING, "Product2.csv"),
        "pur": read(RATING, "ProductUsageResource.csv"),
        "purp": read(RATING, "ProductUsageResourcePolicy.csv"),
        "rce": read(RATES, "RateCardEntry.csv"),
        "rabt": read(RATES, "RateAdjustmentByTier.csv"),
        "currency": read(PRICING, "CurrencyType.csv"),
    }
    missing = [k for k, v in d.items() if v is None]
    if missing:
        print(f"FATAL: could not read CSVs for: {', '.join(missing)}")
        sys.exit(2)
    return d


def currency_units(uom_rows):
    return {r["UnitCode"] for r in uom_rows if r["UnitOfMeasureClass.Code"] == "CURRENCY"}


def rce_key(row):
    """(product, rate card name, usage resource) — identity ignoring currency."""
    return (row["Product.StockKeepingUnit"],
            row["RateCard.$$Name$Type"].split(";")[0],
            row["UsageResource.Code"])


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------
def check_currency_uom_prerequisite(d):
    """Every currency used as a rate UoM must exist as a CURRENCY-class unit."""
    units = currency_units(d["uom"])
    used = {r["RateUnitOfMeasure.UnitCode"] for r in d["rce"]} - {TOKEN_UOM}
    missing = sorted(used - units)
    check("currency_uom_prerequisite", not missing,
          f"rate UoMs with no CURRENCY UnitOfMeasure: {missing}" if missing
          else f"all {len(used)} rate currencies have a CURRENCY unit")


def check_tier_rce_has_adjustment(d):
    """A Tier-type RateCardEntry with no adjustment breaks activate_rates."""
    keyed = {(r["Product.StockKeepingUnit"], r["UsageResource.Name"],
              r["RateUnitOfMeasure.Name"]) for r in d["rabt"]}
    bad = [(r["Product.StockKeepingUnit"], r["UsageResource.Name"], r["RateUnitOfMeasure.Name"])
           for r in d["rce"]
           if r["RateCard.$$Name$Type"].split(";")[-1] == "Tier"
           and (r["Product.StockKeepingUnit"], r["UsageResource.Name"],
                r["RateUnitOfMeasure.Name"]) not in keyed]
    check("tier_rce_has_adjustment", not bad,
          f"{len(bad)} Tier RCE(s) with no tier adjustment: {bad[:4]}" if bad
          else "every Tier rate card entry has >=1 adjustment")


def check_no_orphan_rabt(d):
    """Every tier adjustment must point at a rate card entry that exists."""
    rce_ids = {r[list(r)[0]] for r in d["rce"]}
    parent_col = list(d["rabt"][0])[8]
    orphans = [r[parent_col] for r in d["rabt"] if r[parent_col] not in rce_ids]
    check("no_orphan_rabt", not orphans,
          f"{len(orphans)} adjustment(s) with a missing parent: {orphans[:3]}" if orphans
          else f"all {len(d['rabt'])} adjustments resolve to a rate card entry")


def check_pack_products_have_no_purp(d):
    """Platform rejects a ProductUsageResourcePolicy on a Pack product."""
    packs = {r["StockKeepingUnit"] for r in d["product"] if r["UsageModelType"] == "Pack"}
    bad = sorted({r["ProductUsageResource.Product.StockKeepingUnit"] for r in d["purp"]
                  if r["ProductUsageResource.Product.StockKeepingUnit"] in packs})
    check("pack_products_have_no_purp", not bad,
          f"Pack product(s) carrying a PURP (platform will reject): {bad}" if bad
          else f"no PURP on any of the {len(packs)} Pack products")


def check_every_pur_has_rate_card_entry(d):
    """A PUR with no rate card entry fails the Usage Product Validator."""
    have = {(r["Product.StockKeepingUnit"], r["UsageResource.Code"]) for r in d["rce"]}
    missing = sorted({(r["Product.StockKeepingUnit"], r["UsageResource.Code"]) for r in d["pur"]}
                     - have - ALLOWED_PUR_WITHOUT_RCE)
    check("every_pur_has_rate_card_entry", not missing,
          f"PUR(s) with no rate card entry: {missing}" if missing
          else "every product usage resource has a rate (allowed exceptions aside)")


def check_currency_coverage_uniform(d):
    """Each currency-denominated entry must exist in every target currency."""
    units = currency_units(d["uom"])
    by_key = {}
    for r in d["rce"]:
        uom = r["RateUnitOfMeasure.UnitCode"]
        if uom == TOKEN_UOM:
            continue
        by_key.setdefault(rce_key(r), set()).add(uom)
    gaps = {k: sorted(units - v) for k, v in by_key.items() if units - v}
    check("currency_coverage_uniform", not gaps,
          f"{len(gaps)} entry/entries missing currencies, e.g. "
          f"{list(gaps.items())[:2]}" if gaps
          else f"all {len(by_key)} currency-denominated entries cover all {len(units)} currencies")


def check_token_entries_not_expanded(d):
    """Token-denominated rates are in tokens, not money — never per-currency."""
    by_key = {}
    for r in d["rce"]:
        if r["RateUnitOfMeasure.UnitCode"] == TOKEN_UOM:
            by_key.setdefault(rce_key(r), 0)
            by_key[rce_key(r)] += 1
    dupes = {k: v for k, v in by_key.items() if v != 1}
    check("token_entries_not_expanded", not dupes,
          f"token-denominated entries duplicated: {dupes}" if dupes
          else f"all {len(by_key)} token-denominated entries are single-currency")


def check_percentages_currency_neutral(d):
    """A percentage discount is the same number in every currency."""
    groups = {}
    for r in d["rabt"]:
        if r["AdjustmentType"] != "Percentage" or r["RateUnitOfMeasure.Name"] == "Tokens":
            continue
        k = (r["Product.StockKeepingUnit"], r["UsageResource.Name"],
             r["LowerBound"], r["UpperBound"])
        groups.setdefault(k, set()).add(r["AdjustmentValue"])
    drift = {k: sorted(v) for k, v in groups.items() if len(v) > 1}
    check("percentages_currency_neutral", not drift,
          f"percentage values differ across currencies: {list(drift.items())[:2]}" if drift
          else f"all {len(groups)} percentage tiers identical across currencies")


def check_bounds_not_converted(d):
    """LowerBound/UpperBound are consumption quantities, never money."""
    groups = {}
    for r in d["rabt"]:
        k = (r["Product.StockKeepingUnit"], r["UsageResource.Name"], r["AdjustmentType"],
             r["RateUnitOfMeasure.Name"])
        groups.setdefault(k, []).append((r["LowerBound"], r["UpperBound"]))
    # Compare each currency's set of bounds for a product/resource against the base.
    by_pr = {}
    for (prod, res, atype, uom), bounds in groups.items():
        if uom == "Tokens":
            continue
        by_pr.setdefault((prod, res, atype), {})[uom] = sorted(bounds)
    drift = {k: v for k, v in by_pr.items() if len({tuple(b) for b in v.values()}) > 1}
    check("bounds_not_converted", not drift,
          f"tier bounds differ across currencies: {list(drift)[:2]}" if drift
          else f"tier bounds identical across currencies for {len(by_pr)} group(s)")


def check_money_conversion_sane(d):
    """Converted money must track ConversionRate and stay tier-distinct."""
    rates = {r["IsoCode"]: Decimal(r["ConversionRate"]) for r in d["currency"]}
    decimals = {r["IsoCode"]: int(r["DecimalPlaces"]) for r in d["currency"]}
    problems = []

    # (a) Base rates: each currency within one rounding step of the converted base.
    base_rows = {rce_key(r): r for r in d["rce"]
                 if r["RateUnitOfMeasure.UnitCode"] == BASE_CURRENCY and r["Rate"].strip()}
    for r in d["rce"]:
        uom = r["RateUnitOfMeasure.UnitCode"]
        if uom in (BASE_CURRENCY, TOKEN_UOM) or not r["Rate"].strip():
            continue
        src = base_rows.get(rce_key(r))
        if not src or uom not in rates:
            continue
        expect = Decimal(src["Rate"]) * rates[uom] / rates[BASE_CURRENCY]
        actual = Decimal(r["Rate"])
        if expect == 0:
            continue
        # Generous tolerance: hand-set demo rates are allowed to deviate, but a
        # wrong-magnitude value (e.g. an unconverted copy in a 100x currency)
        # is caught.
        ratio = actual / expect
        if not (Decimal("0.2") <= ratio <= Decimal("5")):
            problems.append(f"{rce_key(r)} {uom}: {actual} vs converted ~{expect:.4f}")

    # (b) Tiered Override rates must not collapse onto one another after rounding.
    tiers = {}
    for r in d["rabt"]:
        if r["AdjustmentType"] != "Override":
            continue
        k = (r["Product.StockKeepingUnit"], r["UsageResource.Name"], r["RateUnitOfMeasure.Name"])
        tiers.setdefault(k, set()).add(r["AdjustmentValue"])
    base_counts = {}
    for (prod, res, uom), vals in tiers.items():
        base_counts.setdefault((prod, res), {})[uom] = len(vals)
    for (prod, res), by_uom in base_counts.items():
        n_base = by_uom.get(BASE_CURRENCY)
        if n_base is None:
            continue
        for uom, n in by_uom.items():
            if n < n_base:
                problems.append(
                    f"{prod}/{res} {uom}: {n} distinct override tiers vs {n_base} in {BASE_CURRENCY} "
                    f"(rounding collapsed tiers)")

    check("money_conversion_sane", not problems,
          "; ".join(problems[:3]) if problems
          else "converted rates track ConversionRate and tiers stay distinct")


def check_counts_match_readme(d):
    """Row counts are the numbers the plan READMEs advertise."""
    actual = {"RateCardEntry": len(d["rce"]), "RateAdjustmentByTier": len(d["rabt"]),
              "UnitOfMeasure": len(d["uom"]), "ProductUsageResourcePolicy": len(d["purp"]),
              "ProductUsageResource": len(d["pur"])}
    problems = []
    for plan, names in ((RATES, ("RateCardEntry", "RateAdjustmentByTier")),
                        (RATING, ("UnitOfMeasure", "ProductUsageResourcePolicy",
                                  "ProductUsageResource"))):
        readme = os.path.join(plan, "README.md")
        if not os.path.isfile(readme):
            continue
        text = open(readme, encoding="utf-8").read()
        for n in names:
            token = f"{n}.csv"
            for line in text.splitlines():
                if token in line and "#" in line:
                    digits = "".join(c if c.isdigit() else " " for c in line.split("#", 1)[1])
                    nums = [int(x) for x in digits.split()]
                    if nums and actual[n] not in nums:
                        problems.append(f"{n}: README says {nums[0]}, CSV has {actual[n]}")
                    break
    check("counts_match_readme", not problems, "; ".join(problems) if problems
          else "plan README file-tree counts match the CSVs")


# ----------------------------------------------------------------------
def main():
    d = load()
    for fn in (check_currency_uom_prerequisite,
               check_tier_rce_has_adjustment,
               check_no_orphan_rabt,
               check_pack_products_have_no_purp,
               check_every_pur_has_rate_card_entry,
               check_currency_coverage_uniform,
               check_token_entries_not_expanded,
               check_percentages_currency_neutral,
               check_bounds_not_converted,
               check_money_conversion_sane,
               check_counts_match_readme):
        try:
            fn(d)
        except Exception as exc:  # a check that blows up is a failure, not a crash
            check(fn.__name__.replace("check_", ""), False, f"check raised {type(exc).__name__}: {exc}")

    width = max(len(n) for n, _, _ in RESULTS)
    failed = 0
    print("qb multicurrency data invariants\n" + "=" * (width + 60))
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
        failed += 0 if ok else 1
    print("=" * (width + 60))
    print(f"{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
