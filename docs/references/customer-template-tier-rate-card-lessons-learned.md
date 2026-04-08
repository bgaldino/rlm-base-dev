# Customer demo tier rate card — lessons learned

This note captures what we learned adding **`CD-DEMO Tier Rate Card`**, **`RateCardEntry`** (tier rows), and **`RateAdjustmentByTier`** to **`customer-template-rates`**, alongside the existing **Base** card.

## Object choice

- **Usage rate tiers** on a **`RateCard`** use **`RateAdjustmentByTier`** (children of **`RateCardEntry`**). This is the same family as **Base** **`RateCardEntry`** rows, not **`PriceAdjustmentTier`** (those belong to **`PriceAdjustmentSchedule`** / list pricing in **`qb-pricing`**).

## Load order and status

- **RABT must be inserted while the parent **`RateCardEntry`** is **`Draft`**.** The **`export.json`** object array keeps **`RateCardEntry`** before **`RateAdjustmentByTier`** in one SFDMU pass, then **`activate_rates`** moves entries (and tier behavior at runtime) to **Active** after load.
- **`RateCardEntryStatus`** on **`RateAdjustmentByTier`** CSV rows: use **`Draft`** to match the parent at insert time. Extracted org data often shows **Active** after activation; importing **Active** while the parent is still **Draft** can be rejected depending on org validation.

## SFDMU v5

- **`RateAdjustmentByTier.externalId`** uses relationship paths (**`RateCardEntry.RateCard.Name`**, etc.). **Upsert** against such keys is unreliable in v5; this plan uses **`Insert`** (same pattern as **`RateCardEntry`** in this dataset).
- **`validate_sfdmu_v5_datasets.py`** may report a **Medium** issue on the nested **`RateCardEntry.RateCard.Name`** path; with **`operation: Insert`** the load still succeeds (mirrors **`qb-rates`**).
- **Idempotency** for the customer demo is **not** **`deleteOldData: true`** on RABT (to avoid wiping unrelated tiers if keys ever overlap). Instead, run **`delete_customer_demo_rates_data`** before **`insert_customer_demo_rates_data`** so the demo **Base + Tier** cards and all dependent rows are removed in a controlled way.

## Apex delete behavior

- **`deleteQbRatesData.apex`** documents that **RABT** cannot be deleted when the parent **RCE** is **Inactive**; deleting **RCE** first **cascades** child **RABT**. **`delete_customer_demo_rates_data`** therefore **deactivates Active** demo **RCE**, then **deletes** **RCE**, then **PriceBookRateCard**, then **RateCard** — extended to both **CD-DEMO Base** and **CD-DEMO Tier** cards.

## Demo design

- **Base** and **Tier** cards can both sit on **Standard Price Book** (same pattern as **`qb-rates`**). Which card quoting or rating uses depends on org configuration and user flow; the dataset provides **flat list rates** (Base) and **stepped overrides** (Tier) for side-by-side storytelling.
- **PSM alignment:** Tier **RCE** rows must use the same **`ProductSellingModel.Name`** as **Standard PBE** for each **`SF-USG-*`** SKU as Base rows (**Term Monthly** / **TermDefined** for the Snowflake template).
- **Band units** are in the **default consumption UOM** of each line (TB, GB, credits). Keep **`LowerBound` / `UpperBound`** consistent with that UOM when you change tiers.

## See also

- [`customer-template-rate-card-entry.md`](./customer-template-rate-card-entry.md)
- [`datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md`](../../datasets/sfdmu/customer-template/en-US/customer-template-rates/README.md)
- [`datasets/sfdmu/qb/en-US/qb-rates/README.md`](../../datasets/sfdmu/qb/en-US/qb-rates/README.md)
