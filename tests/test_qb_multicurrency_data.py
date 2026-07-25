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
* ``commitment_purp_has_no_periods`` — the platform REJECTS a rating frequency
  or aggregation policy on the PURP of a commitment product; a commitment
  discounts the anchor's rating rather than rating anything itself. Ten such
  rows shipped and silently failed to load, leaving the org with 10 of the 20
  PURP rows the plan declares.
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
* ``rates_derived_from_base`` — every non-base rate must equal the generator's
  derived value exactly. ``money_conversion_sane`` deliberately tolerates
  0.2x–5x for hand-tuned demo rates, which let six hand-seeded GBP/JPY
  placeholders (e.g. GBP storage at the unconverted USD 10 instead of 7.48)
  survive an expansion and rate wrong in a live org.
* ``period_ordering_descending`` — the platform requires Billing >= Rating >
  Accumulation. Three equal Monthly periods fail the "Create Empty Summaries"
  batch with "Specify values for the Billing Period, Rating Period and Usage
  Accumulation Period parameters in descending order", which blocks the entire
  usage-rating pipeline: no UsageSummary, no rating, no billing.
"""
import csv
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RATING = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-rating")
RATES = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-rates")
PRICING = os.path.join(REPO_ROOT, "datasets/sfdmu/qb/en-US/qb-pricing")

BASE_CURRENCY = "USD"
TOKEN_UOM = "TOKEN-UOM"

# Product2.UsageModelType values the platform treats as "commitment" — their
# ProductUsageResourcePolicy rows may carry a UsageCommitmentPolicy and nothing
# else (no rating frequency, no aggregation).
COMMITMENT_MODEL_TYPES = {"Commit", "CommitmentQuantity", "CommitmentSpend"}

# ProductUsageResources intentionally shipped without a rate card entry.
# UR-USD is Category=Currency (the monetary-commitment wallet) — it holds the
# committed amount rather than being consumed, so it is rated through the
# anchor's UR-CPUTIME / UR-DATASTORAGE instead. Deliberate, not a gap.
ALLOWED_PUR_WITHOUT_RCE = {("QB-MTY-CMT", "UR-USD")}

# Commitment/pack usage resources knowingly not present on any anchor.
#
# Empty by design. QB-MTY-CMT once carried dedicated UR-CPUTIME-MTY /
# UR-DATASTORAGE-MTY resources that existed on no anchor, making its discounts
# unreachable; it now reuses the anchor's UR-CPUTIME / UR-DATASTORAGE the way
# QB-QTY-CMT always has. Adding an entry here means shipping rate data that no
# usage can ever hit, so it should be a conscious, documented choice.
ALLOWED_ADDON_RESOURCES_WITHOUT_ANCHOR = set()

# Rates deliberately NOT derived from the base currency — e.g. a bespoke local
# price rather than a conversion. Keyed (product, rate card, resource, currency).
# Empty by design: every entry here is a rate that will not track a
# CurrencyType.ConversionRate change, so adding one should be a conscious choice.
ALLOWED_RATE_DEVIATIONS = set()

# The billing period is a RUNTIME value (UsageEntitlementAccount.BillingPeriodUnit),
# not design-time data, so it cannot be read from a CSV. Every QB selling model
# bills monthly; if a quarterly/annual model is added this must become per-product.
BILLING_PERIOD = "Monthly"

# Ordering rank for period comparison. Higher = longer period.
PERIOD_RANK = {"Daily": 1, "Weekly": 2, "Monthly": 3, "Quarterly": 4,
               "Yearly": 5, "Annual": 5}

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
        "urbp": read(RATING, "UsageResourceBillingPolicy.csv"),
        "rfp": read(RATING, "RatingFrequencyPolicy.csv"),
        "resource": read(RATING, "UsageResource.csv"),
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


def check_commitment_purp_has_no_periods(d):
    """A commitment product's PURP may carry ONLY a UsageCommitmentPolicy.

    The platform rejects both period fields on any PURP whose product is a
    commitment usage model type:

        INVALID_INPUT, This field must be empty when the product associated
        with the product usage resource is one of the commitment usage model
        types.: [RatingFrequencyPolicyId]

    ...and the same message for [UsageAggregationPolicyId]. A commitment does
    not rate anything itself; it discounts the ANCHOR's rating, so the anchor's
    resources own the rating and accumulation periods. Ten such rows shipped
    with rating=Monthly + accumulation and silently failed to load on every
    build, leaving the org with half the PURP rows the plan declares.
    """
    commits = {r["StockKeepingUnit"] for r in d["product"]
               if r["UsageModelType"] in COMMITMENT_MODEL_TYPES}
    bad = []
    for row in d["purp"]:
        sku = row["ProductUsageResource.Product.StockKeepingUnit"]
        if sku not in commits:
            continue
        carried = [f for f, col in (("rating", "RatingFrequencyPolicy.RatingPeriod"),
                                    ("accumulation", "UsageAggregationPolicy.Code"))
                   if (row.get(col) or "").strip()]
        if carried:
            res = row["ProductUsageResource.UsageResource.Code"]
            bad.append(f"{sku}/{res} carries {'+'.join(carried)}")
    check("commitment_purp_has_no_periods", not bad,
          f"{len(bad)} row(s) the platform will reject: " + "; ".join(bad[:3]) if bad
          else f"no rating/accumulation on any PURP of the {len(commits)} commitment products")


def check_addon_usage_resources_exist_on_anchor(d):
    """A commitment or pack discounts/tops up the ANCHOR's consumption.

    Usage is only ever recorded against an anchor asset, so a Category=Usage
    resource on a commitment or pack can only ever match consumption if the same
    resource also exists on some Anchor product. A resource that exists nowhere
    else is unreachable: its rate adjustments are live, valid, currency-complete
    data that no usage can ever hit.

    QB-MTY-CMT shipped with its own UR-CPUTIME-MTY / UR-DATASTORAGE-MTY clones
    while every anchor consumes UR-CPUTIME / UR-DATASTORAGE, so its 5%/10%
    monetary-commitment discounts were unreachable in principle.

    Wallet resources are exempt: Category=Token (the token balance) and
    Category=Currency (the monetary-commitment spend wallet, UR-USD) are held by
    the commitment itself and are not consumed directly.
    """
    category = {r["Code"]: r["Category"] for r in d["resource"]}
    model = {r["StockKeepingUnit"]: r["UsageModelType"] for r in d["product"]
             if r.get("UsageModelType")}

    by_sku = {}
    for r in d["pur"]:
        by_sku.setdefault(r["Product.StockKeepingUnit"], set()).add(r["UsageResource.Code"])
    anchor_res = set()
    for sku, m in model.items():
        if m == "Anchor":
            anchor_res |= by_sku.get(sku, set())

    orphans = []
    for sku, m in sorted(model.items()):
        if m not in COMMITMENT_MODEL_TYPES and m != "Pack":
            continue
        for res in sorted(by_sku.get(sku, set())):
            if (category.get(res) == "Usage" and res not in anchor_res
                    and (sku, res) not in ALLOWED_ADDON_RESOURCES_WITHOUT_ANCHOR):
                orphans.append(f"{sku}/{res}")
    known = len(ALLOWED_ADDON_RESOURCES_WITHOUT_ANCHOR)
    check("addon_usage_resources_exist_on_anchor", not orphans,
          f"{len(orphans)} unreachable resource(s) — no anchor consumes them: "
          + ", ".join(orphans) if orphans
          else f"every commitment/pack usage resource is consumed by an anchor "
               f"({known} recorded gap(s) allowed)")


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


def _derive(usd_value, ccy, rates, decimals):
    """Mirror scripts/expand_currency_rates_data.py rounding exactly."""
    converted = Decimal(str(usd_value)) * rates[ccy] / rates[BASE_CURRENCY]
    if decimals[ccy] == 0:
        # Whole-unit currencies (JPY) round to a whole unit, but a *rate* is often
        # sub-unit; rounding those up would flatten tiers, so keep 2dp below 1.
        step = Decimal("1") if abs(converted) >= 1 else Decimal("0.01")
    else:
        step = Decimal("0.01") if abs(converted) >= 1 else Decimal("0.0001")
    q = converted.quantize(step, rounding=ROUND_HALF_UP)
    return step if q == 0 else q


def check_rates_derived_from_base(d):
    """Every non-base rate must equal its derived value exactly.

    money_conversion_sane tolerates 0.2x-5x for hand-tuned rates; that window let
    an unconverted GBP copy of a USD rate (1.34x) ship and rate wrong in a live
    org. Nothing here is hand-tuned today, so require exact derivation and make
    any exception explicit via ALLOWED_RATE_DEVIATIONS.
    """
    rates = {r["IsoCode"]: Decimal(r["ConversionRate"]) for r in d["currency"]}
    decimals = {r["IsoCode"]: int(r["DecimalPlaces"]) for r in d["currency"]}
    base_rows = {rce_key(r): r for r in d["rce"]
                 if r["RateUnitOfMeasure.UnitCode"] == BASE_CURRENCY and r["Rate"].strip()}

    problems = []
    for r in d["rce"]:
        uom = r["RateUnitOfMeasure.UnitCode"]
        if uom in (BASE_CURRENCY, TOKEN_UOM) or uom not in rates or not r["Rate"].strip():
            continue
        src = base_rows.get(rce_key(r))
        if not src:
            continue
        key = rce_key(r) + (uom,)
        if key in ALLOWED_RATE_DEVIATIONS:
            continue
        expect = _derive(src["Rate"], uom, rates, decimals)
        if Decimal(r["Rate"]) != expect:
            problems.append(f"{'/'.join(rce_key(r))} {uom}: {r['Rate']} != derived {expect}")

    check("rates_derived_from_base", not problems,
          f"{len(problems)} underived rate(s): " + "; ".join(problems[:3]) if problems
          else "every non-base rate matches its derived value")


def check_period_ordering_descending(d):
    """Billing >= Rating > Accumulation, or the summary batch rejects the record.

    The platform demands the three periods "in descending order". Three equal
    Monthly values do NOT satisfy it: with all three Monthly the Create Empty
    Summaries batch fails every UsageEntitlementAccount and no usage is ever
    summarised or rated. Accumulation must be strictly shorter than rating.

    Runtime reads the accumulation policy from UsageResource, NOT from the
    ProductUsageResourcePolicy row, so both paths are checked -- fixing only the
    PURP reference leaves the resource default broken while looking correct.
    """
    accum_period = {r["Code"]: r["UsageAccumulationPeriod"] for r in d["urbp"]}
    rating_period = {r["Name"]: r["RatingPeriod"] for r in d["rfp"]}
    resource_policy = {r["Code"]: (r.get("UsageResourceBillingPolicy.Code") or "").strip()
                       for r in d["resource"]}

    billing_rank = PERIOD_RANK[BILLING_PERIOD]
    problems = []

    for row in d["purp"]:
        rating = (row.get("RatingFrequencyPolicy.RatingPeriod") or "").strip()
        agg = (row.get("UsageAggregationPolicy.Code") or "").strip()
        if not rating and not agg:
            continue  # commitment-only row: carries no periods to order
        sku = row["ProductUsageResource.Product.StockKeepingUnit"]
        res = row["ProductUsageResource.UsageResource.Code"]

        # Both accumulation sources must satisfy the rule.
        for label, code in (("purp", agg), ("resource", resource_policy.get(res, ""))):
            if not code:
                continue
            period = accum_period.get(code)
            if period is None:
                problems.append(f"{sku}/{res} [{label}]: unknown policy {code!r}")
                continue
            if not rating:
                problems.append(f"{sku}/{res} [{label}]: accumulation {period} but no rating period")
                continue
            r_rank, a_rank = PERIOD_RANK.get(rating, 0), PERIOD_RANK.get(period, 0)
            if not (billing_rank >= r_rank > a_rank):
                problems.append(
                    f"{sku}/{res} [{label}]: billing={BILLING_PERIOD} rating={rating} "
                    f"accumulation={period} ({code}) — not descending")

    check("period_ordering_descending", not problems,
          f"{len(problems)} violation(s): " + "; ".join(problems[:3]) if problems
          else "billing >= rating > accumulation for every policy row")


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
               check_commitment_purp_has_no_periods,
               check_addon_usage_resources_exist_on_anchor,
               check_every_pur_has_rate_card_entry,
               check_currency_coverage_uniform,
               check_token_entries_not_expanded,
               check_percentages_currency_neutral,
               check_bounds_not_converted,
               check_money_conversion_sane,
               check_rates_derived_from_base,
               check_period_ordering_descending,
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
