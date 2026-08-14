# Verifying a Usage/Consumption Build

Read this when verifying a consumption build, diagnosing a suspicious result, or
adding a new invariant. Parent skill: [SKILL.md](SKILL.md).

Because usage failures are **silent** — a wrong ordering yields zero, a missing
currency input yields a plausible-but-wrong price — verification is not optional
polish. Treat "the numbers look right" as unverified.

## The three layers

| Layer | Command | Needs an org? | Catches |
|-------|---------|---------------|---------|
| Offline invariants | `python tests/test_qb_multicurrency_data.py` | No | Design-time data that the platform will reject or that rates wrongly |
| Live design + runtime | `cci task run validate_multicurrency_rates --org <cci-alias>` | Yes | Same design-time checks against the org, plus asset/entitlement shape. Runtime checks self-skip when no assets exist |
| Rated results | `sf apex run --file scripts/apex/validateRatedUsage.apex --target-org <sf-alias>` | Yes, with rated usage | `TotalAmount = OverageQuantity × NetUnitRate` (0.01 tolerance), rating actually settled, and commitment-drains-before-grant |

Plus the plan-level checks that apply to any dataset change:

```bash
python scripts/validate_sfdmu_v5_datasets.py             # v5 compliance
python scripts/ai/check_plan_readme_consistency.py       # README ↔ export.json/CSVs, repo-wide
```

⚠ Remember the CCI vs `sf` alias split: `--org` takes a **CCI** alias,
`--target-org` takes an **sf** alias or username. CCI alias `beta` maps to sf alias
`rlm-base__beta`.

## Offline invariants — the fast gate

17 checks, no org needed, runs in under a second. Run it before every commit that
touches `qb-rating`, `qb-rates`, or `qb-pricing` data.

| Invariant | Guards against |
|-----------|----------------|
| `currency_uom_prerequisite` | A rate currency with no CURRENCY unit of measure |
| `tier_rce_has_adjustment` | A Tier rate card entry with no tier adjustment — rates as zero |
| `no_orphan_rabt` | An adjustment pointing at a rate card entry that does not exist |
| `pack_products_have_no_purp` | Platform rejects a PURP on a Pack product |
| `commitment_purp_has_no_periods` | Platform rejects rating/accumulation on a commitment PURP |
| `addon_usage_resources_exist_on_anchor` | A commitment/pack resource no anchor consumes — the commitment silently does nothing |
| `every_pur_has_rate_card_entry` | An unrated product usage resource |
| `currency_coverage_uniform` | A currency-denominated entry missing a currency |
| `token_entries_not_expanded` | Token entries wrongly multiplied per currency |
| `percentages_currency_neutral` | A percentage tier converted as if it were money |
| `bounds_not_converted` | Tier *bounds* converted — they must stay identical across currencies |
| `money_conversion_sane` | Converted rates that drift from `ConversionRate`, or tiers that collapse into each other |
| `rates_derived_from_base` | A non-base rate that does not match its derived value |
| `overrides_derived_from_base` | A non-base **Override tier value** that does not match its derived value — these are money and are converted, but were unchecked by the two rules above |
| `period_ordering_descending` | `billing >= rating > accumulation` violated |
| `counts_match_readme` | Plan README file-tree counts drifting from the CSVs |
| `docs_state_the_real_count` | This page and `AGENTS.md` advertising a number of invariants that is no longer true — it counts itself, so adding a check means updating both |

Retired at 264: `accumulation_refs_aligned` compared the accumulation policy named on
`UsageResource` against the one named on ProductUsageResourcePolicy. Release 264 removed
`UsageResource.UsageResourceBillingPolicyId`, so PURP is now the only place that policy is
named — there is no second reference to disagree with it. Do not re-add it.

### Adding an invariant

The suite is a flat set of `check_*(d)` functions over pre-loaded CSV data.

1. Write `def check_<name>(d):` with a docstring stating **what the platform does**
   when the invariant is violated — quote the actual error text if there is one.
   That docstring is why the next reader trusts the check.
2. Compute the offending rows, then call
   `check("<name>", <ok>, "<detail>")`. The detail string is printed on both pass
   and fail — make the pass message state what was actually verified
   (`"no PURP on any of the 2 Pack products"`), not just `"ok"`.
3. **Register it in the tuple inside `main()`** — a function that is not listed
   never runs, and nothing warns you.
4. Confirm the count in the summary line went up (e.g. `16/16` → `17/17`).

A check that raises is reported as a failure rather than crashing the run, so a
malformed CSV surfaces as one red line instead of a traceback.

## Live verification

```bash
cci task run validate_multicurrency_rates --org <cci-alias>
```

Design-time checks mirror the offline suite against the org, scoped to the
QuantumBit SKUs. Runtime checks (`AssetRateCardEntry` currency alignment, and
per-asset entitlement shape compared across assets of the same product)
**self-skip when no assets exist**, so a clean run on an empty org is not
evidence — build assets first.

```bash
python scripts/qb_usage.py audit  --org <sf-alias>   # design-time: products, policies, rates
python scripts/qb_usage.py report --org <sf-alias>   # runtime: buckets, drawdown, rating
```

`validateRatedUsage.apex` is the assertion pass — run it after orchestration settles.
It aggregates the journals and checks the arithmetic rather than printing numbers for
a human to eyeball.

## Reading a suspicious result

Before concluding the rates are wrong:

1. **Is it zero?** That is almost always ordering, not rating —
   [SKILL.md](SKILL.md) Quick Rules 1–4.
2. **Is `OverageQuantity` non-zero?** On ordinary rows it mirrors `TierQuantity` and
   means "beyond the included allowance", **not** beyond the commitment.
3. **Did the commitment apply at all?** Check the `UsageCmtAssetRelatedObj` link
   exists. Without it, consumption drains the anchor grant at the anchor rate and
   nothing reports a problem.
4. **Which overage behaviour was configured?** `Lowest Commitment Rate` vs
   `Bounded Object Rate` is design-time only — **no runtime object records which
   applied**, so you must read the policy.
5. **Did a batch fail?** `troubleshooting/SKILL.md` → *Async rating/entitlement batch
   failed* for the `BatchJobPartFailedRecord` query.

## Pre-PR checklist

- [ ] `python tests/test_qb_multicurrency_data.py` — all checks pass
- [ ] `python scripts/validate_sfdmu_v5_datasets.py` — no new failures against the known baseline
- [ ] `python scripts/ai/check_plan_readme_consistency.py` — **0 errors repo-wide**
- [ ] New platform rule discovered? Add an invariant *and* record it in
      `revenue-cloud-data-model/domains/usage.md`
- [ ] Product loaded surgically into a live org? The full-build verification is still owed — say so explicitly
