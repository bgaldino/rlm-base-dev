# RateCardEntry — customer template and base vs tiered pricing

This reference explains how **`RateCardEntry`** ties a **rate card** to **product**, **usage resource**, **product selling model**, and **units of measure**, and how that differs for **Base** vs **Tier** (and related) rate cards. It complements **`ProductUsageResource`** (product ↔ meter) and the **`customer-template-rates`** plan. Start here; extend with **`qb-rates`** when you need tiers or attribute-style cards.

## What a RateCardEntry stitches

Each **`RateCardEntry`** row is keyed in data loads by **product SKU + rate card + usage resource + rate UOM** (see `export.json` **`externalId`**). Conceptually it binds:

| Binding | CSV / fields | Notes |
|--------|----------------|-------|
| **Rate card** | `RateCard.Name` + **`RateCard.Type`** (`Base`, `Tier`, `Attribute`, …) | Parent scope and card-level **EffectiveFrom** / **EffectiveTo**. |
| **Sellable product** | `Product.StockKeepingUnit` | Same **Pack** SKUs wired via **`ProductUsageResource`** to **`UsageResource`** in rating. |
| **Usage resource** | `UsageResource.Code` | Must match active **`UsageResource`** (and PUR) from the rating plan. |
| **Selling model** | `ProductSellingModel.Name` (and org **SellingModelType** must match the named PSM) | **Must match the same `ProductSellingModel` as the product’s Standard `PricebookEntry`** (same SKU as in `scripts/customer-demo/customer-pricebook-entries.csv`). If the PBE uses **Term Monthly** / **TermDefined** for **`SF-USG-*`**, every **`RateCardEntry`** for those products must use that PSM — not **One-Time** — or quotes and rating will disagree. |
| **Consumption UOM** | **`DefaultUnitOfMeasure`** + **`DefaultUnitOfMeasureClass`** | What usage is measured in for this line (e.g. TB, GB, credits). |
| **Rate (money) UOM** | **`RateUnitOfMeasure`** + **`RateUnitOfMeasureClass`** | Currency or token UOM for the **Rate** column (often **USD** / **Currency**). |

**Base rate cards:** the **list price semantics** for that row live **on the RateCardEntry**: **`Rate`**, **`RateUnitOfMeasure`**, and **`RateNegotiation`** (e.g. **Negotiable**). The Snowflake **`customer-template-rates`** **`RateCardEntry.csv`** rows are all **Base** examples.

**Product selling model alignment (critical):** Before saving **`RateCardEntry.csv`**, confirm **`ProductSellingModel.Name`** (and the corresponding **`SellingModelType`** in the org) matches **`PSMName`** / **`PSMSellingModelType`** for that **SKU** in **`customer-pricebook-entries.csv`**. Usage Pack SKUs (**`SF-USG-*`**) in the template use **Term Monthly** (**TermDefined**), not One-Time.

**Tier (and similar non-base) rate cards:** the **RateCardEntry** still defines **which product × resource × rate UOM × selling model** the tier ladder applies to, but the **stepped prices** are usually expressed on **child** records — in this repo, **`RateAdjustmentByTier`** (adjustment type, value, **LowerBound** / **UpperBound**, effective dates). Tier examples often leave **`Rate`** empty on the **Tier** **`RateCardEntry`** and supply **`Override`** / **`Percentage`** rows per band in **`RateAdjustmentByTier.csv`**. See **`datasets/sfdmu/qb/en-US/qb-rates/README.md`** (“Tier Rate Card Entries” and “Rate Adjustments by Tier”).

**Platform constraint:** **`RateAdjustmentByTier`** must be inserted while the parent **`RateCardEntry`** is **`Draft`**. The **qb-rates** plan loads RCE as **Draft**, inserts RABT, then **`activate_rates`** sets entries to **Active** (see same README).

**Attribute**-type rate cards appear in QuantumBit as a separate **`RateCard.Type`**; treat them as an advanced variant — same idea (parent RCE + related adjustments as defined by product), but use **`qb-rates`** and org docs when you go past tiered usage.

## Effective dates (rate card vs entry)

- **`RateCard.EffectiveFrom` / `EffectiveTo`** bound the card’s validity window.
- **`RateCardEntry.EffectiveFrom` / `EffectiveTo`** should fall **inside** (or align with) that window so the entry is valid when the card applies.
- For demos and quotes you intend to run **on a chosen “sell” date**, set **entry (and card) `EffectiveFrom` to a calendar day strictly before that sell date** so rates are already in force when users price lines. Template CSVs use fixed historical dates (e.g. **2024-01-01**); refresh them if your demo “today” moves before the chosen from-date.
- After load, run **`activate_rates`** so **`Status`** moves **Draft → Active** (`scripts/apex/activateRateCardEntries.apex`).

## Customer template vs full QB

| Area | **customer-template-rates** | **qb-rates** |
|------|------------------------------|--------------|
| Rate card type | **Base** (**CD-DEMO Base Rate Card**) + **Tier** (**CD-DEMO Tier Rate Card**) | **Base**, **Tier**, **Attribute** |
| Child adjustments | **`RateAdjustmentByTier`** on Tier card only | **`RateAdjustmentByTier`** |
| Idempotency | Scoped delete task + Insert RCE/RABT (no **`deleteOldData`**) | **Insert** + **`deleteOldData: true`** on RCE/RABT/PBRC (see qb README) |

Tier lessons learned: [`customer-template-tier-rate-card-lessons-learned.md`](./customer-template-tier-rate-card-lessons-learned.md).

## See also

- `docs/references/customer-template-tier-rate-card-lessons-learned.md`
- `datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`
- `docs/references/customer-template-usage-resource.md` — **`UsageResource`** and **`ProductUsageResource`**
- `datasets/sfdmu/qb/en-US/qb-rates/README.md` — full matrix, RABT, activation order
- `docs/guides/customer-demo-onboarding.md` — catalog + usage + rates step order
