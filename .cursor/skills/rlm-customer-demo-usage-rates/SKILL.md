---
name: rlm-customer-demo-usage-rates
description: >-
  Builds or extends Revenue Cloud customer-demo usage (UsageResource, PUR), rate cards
  (RateCardEntry base vs tiered), and SFDMU plans under datasets/sfdmu/customer-template.
  Use when onboarding customer demo catalogs with usage metering, rating data loads,
  CD-DEMO rate cards, ProductUsageResource, RateAdjustmentByTier, effective dates,
  activate_rating_records / activate_rates, or customer_demo_usage flows.
---

# RLM customer demo — usage, rating, and rates

## When to read this

Apply when working on **`datasets/sfdmu/customer-template`**, **`customer_demo_usage`**, usage **Pack** SKUs, **`UsageResource`**, **`ProductUsageResource`**, **`RateCard` / `RateCardEntry`**, or extending toward **QuantumBit `qb-rating` / `qb-rates`** patterns.

**Canonical repo docs (read these for full detail):**

- `docs/references/customer-template-usage-resource.md` — **UsageResource** + **ProductUsageResource**
- `docs/references/customer-template-rate-card-entry.md` — **RateCardEntry**, Base vs Tier, effective dates
- `docs/guides/customer-demo-onboarding.md` — end-to-end step order
- `AGENTS.md` — Customer Demo Product Onboarding UX (PCM → usage → rates)

**Deeper tables and file map:** [reference.md](reference.md)

## Load order (do not reorder)

1. **`customer-template-pcm`** — `Product2` (sellable **`SF-USG-*`**, usage-definition **`SF-BLNG-*`**), **UOM / UOM class** used by meters.
2. **`customer-template-rating`** — **UsageResourceBillingPolicy** (e.g. `monthlypeak` / `monthlytotal`), **UsageResource**, **Product2** update (`UsageModelType`), **ProductUsageResource** (Insert). Pass 2 activates **UsageResource**; then run **`activate_rating_records`**.
3. **`customer-template-rates`** — **RateCard**, **PriceBookRateCard**, **RateCardEntry** (Insert, Draft); then **`activate_rates`**.

**Idempotency:** Before re-importing rating or rates, run **`delete_customer_demo_rates_data`** then **`delete_customer_demo_rating_data`** (see `cumulusci.yml` tasks). Customer plans avoid global **`deleteOldData`** on RCE so other org rate cards survive.

## Data model (mental model)

| Piece | Role |
|-------|------|
| **UsageResource** | Meter: **Category = Usage**, UOM class + default UOM, **UsageDefinitionProduct** (`SF-BLNG-*`), **UsageResourceBillingPolicy**. |
| **ProductUsageResource** | Junction: **sellable Pack SKU** (`SF-USG-*`) → **UsageResource** (`SF-UR-*`). Required for rating/rates to resolve product → meter. |
| **RateCard** + **RateCardEntry** | Prices **product × UsageResource × rate UOM** + **ProductSellingModel** + **DefaultUnitOfMeasure** (consumption) vs **RateUnitOfMeasure** (money). |

**Tier-1 customer template** does **not** load **ProductUsageResourcePolicy**, **UsageResourcePolicy**, or **RateAdjustmentByTier** — add **`qb-rating` / `qb-rates`**-style objects when needed.

## Base vs tiered rate cards

- **Base (`RateCard.Type = Base`):** Set **`Rate`**, **`RateUnitOfMeasure`**, **`RateNegotiation`** (e.g. **Negotiable**) **on the RateCardEntry**. Template: **`customer-template-rates/RateCardEntry.csv`**.
- **Tier (`RateCard.Type = Tier`):** **RateCardEntry** often has **empty `Rate`**; stepped pricing on **`RateAdjustmentByTier`** (child rows). **RABT must insert while parent RCE is Draft**; then activate. Mirror **`datasets/sfdmu/qb/en-US/qb-rates`**.

## Effective dates and activation

- **RateCardEntry.EffectiveFrom** (and **RateCard** window) must be **on or after** the card’s validity and **strictly before** the calendar day you treat as “sell / quote demo day” so rates are in force.
- **RateCardEntry** loads as **Draft** → **`activate_rates`** sets **Active**.
- **UsageResource** / **PUR** follow **`activate_rating_records`** (after SFDMU); see `scripts/apex/activateRatingRecords.apex` for token vs non-token PUR behavior.

## SFDMU v5 (critical)

- **externalId** uses **`;`** delimiters, not v4 `$$` in **export.json** (CSV may still use **`$$`** composite columns per plan).
- **Relationship-traversal externalIds** often force **Insert** + scoped delete or **`deleteOldData: true`** — see `CLAUDE.md` / `docs/references/sfdmu-composite-key-optimizations.md`. Do **not** switch Upsert → Insert + deleteOldData on existing plans without user approval and bug justification.

## Extending the template

1. Add PCM rows first (SKUs, UOMs, bundles as needed).
2. Add **UsageResource** + **PUR** rows with stable **Code** / SKU references.
3. Add **RateCardEntry** rows matching **product + UR + rate UOM**; align **ProductSellingModel.Name** with the org.
4. For tiers: add **RateCard** (Tier), **RateCardEntry** (Draft), **RateAdjustmentByTier**, then activation — copy patterns from **qb-rates** `export.json` and README.
5. Run **`python scripts/validate_sfdmu_v5_datasets.py`** on changed plan directories.

## Product2 typing

**`Product2.Type`**: org picklists typically allow **Bundle** or blank — verify before inserts; see onboarding docs and verify tasks.
