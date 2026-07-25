# qb-rating Data Plan

SFDMU data plan for QuantumBit (QB) usage rating design-time configuration. Creates and activates all objects required for usage-based rating on QB products, including usage resources, product-to-resource associations, grants, and policies.

> **SFDMU 5.6.4+ floor.** ProductUsageResource, ProductUsageResourcePolicy, and ProductUsageGrant use `Insert` + `deleteOldData: true` — a pre-5.6.4 workaround for relationship-traversal externalId matching (traversal-keyed Upsert failed to match target records, so re-runs duplicated). Those bugs are **fixed at/below the 5.6.4 floor**; the shipped plan keeps the workaround deliberately. Migrating these back to `Upsert` is the gated `sfdmu-v5-optimization` initiative — do not flip operations without live verification and explicit approval. **PUG is not operation-only**: its externalId triplet is intentionally non-unique across parent PURs (9 of this dataset's 11 PUG rows share 3 triplets), so it must first gain a PUR component (e.g. `ProductUsageResourceId`) before it can move to `Upsert`.

## CCI Integration

### Flow: `prepare_rating`

This plan is executed as **step 1** of the `prepare_rating` flow (when `rating=true`, `qb=true`, and `refresh=false`).

| Step | Task                     | Description                                        |
|------|--------------------------|----------------------------------------------------|
| 1    | `insert_qb_rating_data`  | Runs this SFDMU plan (2 passes)                    |
| 3    | `insert_qb_rates_data`   | Runs qb-rates plan (single pass — all objects)     |
| 5    | `activate_rating_records`| Runs `activateRatingRecords.apex`                  |
| 6    | `activate_rates`         | Runs `activateRateCardEntries.apex`                |

### Task Definition

```yaml
insert_qb_rating_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-rating"
```

## Data Plan Overview

The plan uses **2 SFDMU object sets** (Pass 1 + Pass 2) followed by **Apex activation**:

```
Pass 1 (SFDMU)                              Pass 2 (SFDMU)       Apex Activation
────────────────────────────────────────   ─────────────────     ─────────────────
Insert+deleteOldData (PUR/PURP/PUG); Upsert others  Activate UoMClass  -> activateRatingRecords.apex
                                            and UsageResource       (7-step PUR/PUG activation)
```

**PUR, PURP, and PUG idempotency (Insert+deleteOldData):** All three use `operation: Insert` with `deleteOldData: true` and **no WHERE clause**. Before the 5.6.4 floor, SFDMU v5 could not match records by relationship-traversal externalId components (even 1-hop like `Product.StockKeepingUnit`) and always inserted instead of updating, causing duplicates on re-run — the reason the shipped plan uses Insert+deleteOldData. Those traversal-match bugs are **fixed on the 5.6.4+ floor**; the workaround is retained pending the gated `sfdmu-v5-optimization` migration (see the floor note above). **PUG migration is not operation-only**: its externalId triplet is intentionally non-unique across parent PURs, so an `Upsert` move must first add a PUR component (e.g. `ProductUsageResourceId`) to the key. Mechanically, SFDMU processes deleteOldData in **reverse array order** (PUG → PURP → PUR), satisfying FK constraints (children deleted before parent). No WHERE clause means the plan is fully portable — extraction captures drift for any product in the org. PURP uses `externalId: ProductUsageResourceId` (direct FK, avoids SFDMU v5 validation error for all-multi-hop externalIds). The PURP and PUG CSVs provide `ProductUsageResource.Product.StockKeepingUnit` and `ProductUsageResource.UsageResource.Code` as two separate columns (no `$$` composite) so SFDMU can resolve `ProductUsageResourceId` without triggering the SOQL injection bug.

### Pass 1 — Insert/Upsert with Draft Status

All records are created in `Draft` status. SFDMU resolves lookups across objects using composite external IDs.

| # | Object                       | Operation | External ID                                          | Records |
|---|------------------------------|-----------|------------------------------------------------------|---------|
| 1 | UnitOfMeasure                | Upsert    | `UnitCode`                                           | 18      |
| 2 | UnitOfMeasureClass           | Upsert    | `Code`                                               | 5       |
| 3 | UsageResourceBillingPolicy   | Upsert    | `Code`                                               | 5       |
| 4 | UsageResource                | Upsert    | `Code`                                               | 7       |
| 5 | Product2                     | Update    | `StockKeepingUnit`                                   | 10       |
| 6 | UsageGrantRenewalPolicy      | Upsert    | `Code`                                               | 1       |
| 7 | UsageGrantRolloverPolicy     | Upsert    | `Code`                                               | 1       |
| 8 | UsageOveragePolicy           | Upsert    | `Name`                                               | 2       |
| 9 | UsageCommitmentPolicy        | Upsert    | `Name`                                               | 2       |
| 10| ProductUsageResource         | Insert¹   | `Product.StockKeepingUnit;UsageResource.Code`        | 25      |
| 11| UsagePrdGrantBindingPolicy   | Upsert    | `Name;Product2.StockKeepingUnit`                     | 4       |
| 12| RatingFrequencyPolicy        | Upsert    | `RatingPeriod`                                       | 2       |
| 13| ProductUsageResourcePolicy   | Insert¹   | `ProductUsageResourceId`                             | 23      |
| 14| ProductUsageGrant            | Insert¹   | `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode` | 12      |

¹ Insert+deleteOldData (no WHERE). Pre-5.6.4, SFDMU v5 could not match by relationship-traversal externalId (Upsert inserted duplicates); **fixed on the 5.6.4+ floor**, retained pending the gated migration. PUG additionally needs a PUR component added to its (intentionally non-unique) externalId before any Upsert move — not operation-only. deleteOldData runs in reverse array order (PUG→PURP→PUR) to satisfy FK constraints.

**Currency units feed multicurrency rating (2026-07-24):** `UnitOfMeasure` carries **7 `CURRENCY`-class units** — `USD`, `GBP`, `EUR`, `AUD`, `CAD`, `CHF`, `JPY`. These are what denominate a rate: no rate object has a `CurrencyIsoCode`, so a `RateCardEntry` expresses its currency through its `RateUnitOfMeasure`, and a non-USD quote cannot rate without the matching unit here. Add a currency unit **before** expanding `qb-rates` — `scripts/expand_currency_rates_data.py` refuses to run if one is missing. `JPY` is the only unit with `RoundingMethod=Nearest` / `Scale=1` (whole-yen amounts); the other six are plain 2-decimal units. Note the units' own `CurrencyIsoCode` is `USD` throughout — that field is not the mechanism, `UnitCode` is. See the qb-rates README for the expansion rules.

**Full delete+insert cycle:** PUR, PURP, and PUG all use `deleteOldData: true` with no WHERE clause. Every run deletes ALL records of each type and re-inserts from CSV — no duplicate risk, fully portable. The PURP and PUG CSVs use two separate traversal columns (`ProductUsageResource.Product.StockKeepingUnit` + `ProductUsageResource.UsageResource.Code`) for FK resolution; no `$$` composite column (which caused a SOQL injection bug in the deleteOldData DELETE phase).

**Pack add-on products (2026-07-24):** `QB-TOKENS-PACK` (QuantumBit Tokens Pack) and `QB-DAT-THPT` (Additional Data Throughput) are `UsageModelType=Pack` add-ons that top up an anchor product's usage bucket. Each carries a `ProductUsageResource` and a `ProductUsageGrant` (**5,000 tokens; 100 GB**), and QB-DAT-THPT also has a Base Rate Card entry (in `qb-rates`). QB-DAT-THPT's `UsageDefinitionProduct` is the dedicated `QB-DATA-THPT-BLNG` throughput definition (matching `UR-DATAXFR`), so throughput usage draws down the correct bucket.

> ⛔ **A Pack product cannot have a `ProductUsageResourcePolicy` — platform-enforced.** Inserting one fails with `INVALID_INPUT: "We can't save the pack usage model type record. Change the product usage model type from Pack to another valid option and try again."` (live-verified 2026-07-24 on a fresh build; the two Pack PURP rows this plan previously carried were silently dropped on every load, leaving PURP at 19/21). **The policy belongs on the non-Pack product that consumes the resource, not on the pack.** So the throughput policy (**Monthly** rating / **`dailytotal`** aggregation — see the period-ordering rule below; Daily rating with monthly accumulation would invert it and fail the Create Empty Summaries batch) now lives on the anchor **`QB-DB` + `UR-DATAXFR`** PURP, alongside QB-DB's existing UR-CPUTIME and UR-DATASTORAGE policies; QB-DB also gains the matching Base Rate Card entry. The token pack needs no PURP of its own — `QB-TOKEN` already has policies on the non-Pack products (`QB-DB-TOKEN`, `QB-CMT-TKN-*`).

⚠️ **Placeholder to confirm:** the throughput rate (**0.10 USD/GB**, used by both the QB-DB and QB-DAT-THPT Base entries). Both packs have never been sold (0 assets); wire-up needs a live sell→consume→rate pass to verify before relying on it. QB-DB intentionally has **no** base `ProductUsageGrant` for `UR-DATAXFR` — the anchor includes 0 GB and the pack funds all throughput.

> ⛔ **A commitment product's `ProductUsageResourcePolicy` may carry ONLY a `UsageCommitmentPolicy` — platform-enforced.** Setting either period field on a PURP whose product is `UsageModelType` **Commit / CommitmentQuantity / CommitmentSpend** fails with `INVALID_INPUT: "This field must be empty when the product associated with the product usage resource is one of the commitment usage model types.: [RatingFrequencyPolicyId]"` — and the identical message for `[UsageAggregationPolicyId]`. Live-verified 2026-07-24 on `pr308` by inserting all 10 rows three ways: rating+agg+commit rejected, agg+commit rejected, **commit-only accepted 10/10**.
>
> **A commitment does not rate anything itself — it discounts the *anchor's* rating**, so rating frequency and accumulation belong on the anchor's resources (`QB-DB`, `QB-DB-TOKEN`). This is the same shape as the Pack rule above: the policy lives on the product that actually consumes.
>
> Ten commit PURP rows briefly shipped with `rating=Monthly` + accumulation and were **silently dropped on every load**, leaving the org with 10 of the 20 rows this plan declares — while the CSV, the validator and the plan-consistency check all looked clean. Guarded offline now by `tests/test_qb_multicurrency_data.py::check_commitment_purp_has_no_periods`.

### Pass 2 — Activate UnitOfMeasureClass and UsageResource

| # | Object             | Operation | External ID | Records |
|---|--------------------|-----------|-------------|---------|
| 1 | UnitOfMeasureClass | Update    | `Code`      | 5       |
| 2 | UsageResource      | Update    | `Code`      | 5       |

Only UoMClass and UsageResource are activated in SFDMU Pass 2. PUR and PUG activation requires the Apex script (`activate_rating_records`) which enforces a strict dependency order — Token PURs must be Active before non-Token usage PURs, and all PURs must be Active before PUGs.

## Schema: ProductUsageResource (PUR) and product relationship

Org describe confirms: on **ProductUsageResource**, `ProductId` has `relationshipName: Product` (not Product2). So in SOQL we use **Product.StockKeepingUnit** and **UsageResource.Code** on PUR, and **ProductUsageResource.Product.StockKeepingUnit** when traversing from PURP/PUG. UsagePrdGrantBindingPolicy uses **Product2**.StockKeepingUnit (it has Product2Id). RatingFrequencyPolicy uses **Product**.StockKeepingUnit (relationshipName: Product).

PUR, PURP, and PUG all use `operation: Insert` with `deleteOldData: true` (no WHERE clause). PURP uses `externalId: ProductUsageResourceId` (direct FK — avoids SFDMU v5 validation error for all-multi-hop externalIds). The PURP and PUG CSVs have two separate traversal columns (`ProductUsageResource.Product.StockKeepingUnit` and `ProductUsageResource.UsageResource.Code`) for FK resolution — no `$$` composite (which caused a SOQL injection bug in the deleteOldData DELETE phase).

## Apex Activation Script

**File:** `scripts/apex/activateRatingRecords.apex`

PUR and PUG activation follows a strict 7-step dependency order:

| Step | What                                      | Why                                                                |
|------|-------------------------------------------|--------------------------------------------------------------------|
| 1    | UnitOfMeasureClass -> Active              | Safety net (Pass 2 should already do this)                         |
| 2    | UsageResource -> Active                   | Safety net (Pass 2 should already do this, including QB-TOKEN)     |
| 2.5  | Delete childless duplicate Draft PURs     | Defensive step — PUR now uses Insert+deleteOldData so duplicates should never exist; this is a safety net for any edge cases |
| 3    | Pre-populate TokenResourceId on Draft PURs| Ensures clear+activate works in Step 5 (see below)                 |
| 4    | Token PUR -> Active                       | Must precede Step 5; products with Token PURs require them Active before usage PURs can activate |
| 5    | ALL non-Token PUR -> clear+activate       | TokenResourceId=null + Status='Active' in single DML               |
| 6    | ProductUsageGrant -> Active               | Depends on parent PUR being active                                 |

**Step 3 explained:** Some PURs (QB-DB;UR-\*, QB-QTY-CMT;UR-\*) don't get `TokenResourceId` auto-populated at SFDMU insert time. The clear+activate workaround in Step 5 only prevents auto-population when `TokenResourceId` changes from a non-null value to null -- a null-to-null assignment is a no-op that doesn't block auto-population. Step 3 pre-populates `TokenResourceId` from `UsageResource.TokenResourceId` on these Draft PURs so that Step 5's clear is a real change.

The script is **idempotent** — all activation steps filter on `Status != 'Active'`. Step 2.5 is now a safety-net no-op (PUR uses Insert+deleteOldData, so no duplicates should exist). Re-running on an already-activated org is a safe no-op.

## Products and Usage Model Types

| Product SKU        | Usage Model Type   | Description                              |
|--------------------|--------------------|------------------------------------------|
| QB-DB              | Anchor             | QuantumDB — anchor product with token    |
| QB-DB-TOKEN        | Token              | QuantumDB Token product                  |
| QB-DAT-THPT        | (standard)         | Data Throughput — standalone usage        |
| QB-TOKENS-PACK     | TokenPack          | Token pack (one-time purchase)           |
| QB-CMT-TKN-EACH    | CommitmentToken    | Commit token — each-based pricing        |
| QB-CMT-TKN-FLAT    | CommitmentToken    | Commit token — flat-rate pricing         |
| QB-CMT-TKN-BND     | CommitmentToken    | Commit token — flat rate, **bounded** overage |
| QB-CMT-TKN-TIER    | CommitmentToken    | Commit token — tier-based pricing        |
| QB-QTY-CMT         | CommitmentQuantity | Quantity commitment (CPU/Storage)        |
| QB-MTY-CMT         | CommitmentSpend    | Monetary commitment (USD currency)       |

## Usage Resources

| Code               | Category | UoM Class       | Default UoM | Billing Policy    |
|--------------------|----------|-----------------|-------------|-------------------|
| QB-TOKEN           | Token    | Token_UoM_Class | TOKEN-UOM   | monthlytotal      |
| UR-CPUTIME         | Usage    | TIME            | m (Minutes) | monthlytotal      |
| UR-DATASTORAGE     | Usage    | DATAVOL         | TB          | monthlypeak       |
| UR-DATAXFR         | Usage    | DATAVOL         | GB          | monthlytotal      |
| UR-USD             | Currency | CURRENCY        | USD         | monthlytotal      |
| UR-CPUTIME-TKN     | Usage    | TIME            | m (Minutes) | monthlytotal      |
| UR-DATASTORAGE-TKN | Usage    | DATAVOL         | TB          | monthlypeak       |

## ProductUsageResource (PUR) Mapping

22 records mapping products to their usage resources:

| Product          | Resource            | Notes                                       |
|------------------|---------------------|---------------------------------------------|
| QB-DB            | UR-DATASTORAGE      | Usage PUR (TokenResourceId auto-populated)  |
| QB-DB            | UR-CPUTIME          | Usage PUR (TokenResourceId auto-populated)  |
| QB-DB            | UR-DATAXFR          | Usage PUR — carries the throughput policy (see Pack note) |
| QB-DAT-THPT      | UR-DATAXFR          | Pack PUR — grant only, no policy (Pack cannot hold a PURP) |
| QB-TOKENS-PACK   | QB-TOKEN            | Token pack                                  |
| QB-DB-TOKEN      | QB-TOKEN            | Token PUR                                    |
| QB-DB-TOKEN      | UR-DATASTORAGE-TKN  | Usage PUR — dedicated token resource        |
| QB-DB-TOKEN      | UR-CPUTIME-TKN      | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-EACH  | QB-TOKEN            | Token PUR                                    |
| QB-CMT-TKN-EACH  | UR-DATASTORAGE-TKN  | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-EACH  | UR-CPUTIME-TKN      | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-FLAT  | QB-TOKEN            | Token PUR                                    |
| QB-CMT-TKN-FLAT  | UR-CPUTIME-TKN      | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-FLAT  | UR-DATASTORAGE-TKN  | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-BND   | QB-TOKEN            | Token PUR — Bounded Object Rate              |
| QB-CMT-TKN-BND   | UR-CPUTIME-TKN      | Usage PUR — Bounded Object Rate              |
| QB-CMT-TKN-BND   | UR-DATASTORAGE-TKN  | Usage PUR — Bounded Object Rate              |
| QB-CMT-TKN-TIER  | QB-TOKEN            | Token PUR                                    |
| QB-CMT-TKN-TIER  | UR-DATASTORAGE-TKN  | Usage PUR — dedicated token resource        |
| QB-CMT-TKN-TIER  | UR-CPUTIME-TKN      | Usage PUR — dedicated token resource        |
| QB-QTY-CMT       | UR-DATASTORAGE      | Commitment qty (no token allowed)           |
| QB-QTY-CMT       | UR-CPUTIME          | Commitment qty (no token allowed)           |
| QB-MTY-CMT       | UR-USD              | Monetary commitment (currency)              |
| QB-MTY-CMT       | UR-CPUTIME          | Usage PUR — the anchor's resource, discounted |
| QB-MTY-CMT       | UR-DATASTORAGE      | Usage PUR — the anchor's resource, discounted |

## ProductUsageGrant (PUG) Summary

11 grant records across 5 usage definition products:

| Usage Definition Product | Type   | Resource          | Quantity | Validity       |
|--------------------------|--------|-------------------|----------|----------------|
| QB-CPU-BLNG              | Grant  | QB-DB;UR-CPUTIME            | 0     | 1 Month |
| QB-CPU-BLNG              | Commit | QB-QTY-CMT;UR-CPUTIME       | 1000  | 1 Month |
| QB-DATA-STORAGE-BLNG     | Grant  | QB-DB;UR-DATASTORAGE        | 5     | 1 Month |
| QB-DATA-STORAGE-BLNG     | Commit | QB-QTY-CMT;UR-DATASTORAGE   | 1000  | 1 Month |
| QB-DATA-THPT-BLNG        | Grant  | QB-DAT-THPT;UR-DATAXFR      | 5     | 1 Month |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-FLAT;QB-TOKEN    | 1000  | 1 Month |
| QB-TOKEN-DEF             | Grant  | QB-DB-TOKEN;QB-TOKEN        | 100000| None    |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-TIER;QB-TOKEN    | 1000  | 1 Month |
| QB-TOKEN-DEF             | Commit | QB-CMT-TKN-EACH;QB-TOKEN    | 1000  | 1 Month |
| QB-TOKEN-DEF             | Grant  | QB-TOKENS-PACK;QB-TOKEN     | 500   | 1 Month |
| RES-USD-DEF              | Commit | QB-MTY-CMT;UR-USD           | 5000  | 1 Month |

## API 260 Known Issues

### TokenResourceId Auto-Population

The platform auto-populates `TokenResourceId` on non-Token PURs during ANY DML (insert or update) when their `UsageResource` has a Token association (`UsageResource.TokenResourceId` is set). This is independent of QB-TOKEN's Status -- it is driven by the UsageResource relationship field. Affected resources: the token variants `UR-CPUTIME-TKN` / `UR-DATASTORAGE-TKN` (`TokenResource.Code = QB-TOKEN`); the base `UR-CPUTIME` / `UR-DATASTORAGE` resources carry no token association.

### Activation Conflict and Clear+Activate Workaround

When activating a PUR (`Status='Active'`), the platform auto-populates `TokenResourceId` during the same DML. This then fails because "TokenResourceId can't be edited when the PUR is Active." The workaround sets `TokenResourceId=null` AND `Status='Active'` in a single DML update, which prevents auto-population.

**Critical nuance:** The clear+activate only works when `TokenResourceId` changes from a **non-null** value to null. A null-to-null "clear" is a no-op and does NOT prevent auto-population. This is why Step 3 of the Apex script pre-populates `TokenResourceId` on Draft PURs where it is missing -- ensuring Step 4's clear is a real field change.

### Monetary Commitment Usage PURs — the anchor's own resources

The CommitmentSpend product (`QB-MTY-CMT`) carries Usage-category PURs alongside its Currency PUR (`QB-MTY-CMT;UR-USD`):

- `QB-MTY-CMT;UR-CPUTIME` — the anchor's compute resource, discounted 5%
- `QB-MTY-CMT;UR-DATASTORAGE` — the anchor's storage resource, discounted 10%

**A commitment must name the resources its anchor actually consumes.** Usage is only ever recorded against an anchor, so a discount attached to a resource no anchor holds can never match anything. `QB-QTY-CMT` has always reused `QB-DB`'s `UR-CPUTIME` / `UR-DATASTORAGE`; the spend commitment now does the same. What makes it a *spend* commitment is its wallet — the `UR-USD` Currency PUR holding the committed amount — not the resource it discounts.

> **History (2026-07-25).** This product previously carried dedicated `UR-CPUTIME-MTY` / `UR-DATASTORAGE-MTY` resources (`Category=Usage`, `TokenResource.Code = UR-USD`), mirroring how the `-TKN` variants are backed by `QB-TOKEN`. The token model works because a matching anchor exists — `QB-DB-TOKEN` carries the `-TKN` resources — but no anchor ever carried the `-MTY` ones, so QB-MTY-CMT's tier adjustments were valid, currency-complete data that no usage could reach. The two resources are retired (UsageResource 9 → 7) and 28 rate rows repointed. The original rationale — that reusing the `-TKN` variants would trigger a `TokenResourceId` activation conflict — still holds and is why the plain, token-free `UR-CPUTIME` / `UR-DATASTORAGE` are the right target rather than the `-TKN` pair.
>
> Guarded by `tests/test_qb_multicurrency_data.py::check_addon_usage_resources_exist_on_anchor`, whose allowlist is now empty: any commitment or pack resource that no anchor consumes fails the suite.
>
> ⚠️ Still unverifiable end to end — CommitmentSpend entitlements never leave PENDING (see below), so this repoint is correct by construction but has not been proven live.

### CommitmentQuantity / CommitmentSpend entitlements never leave PENDING

Live-verified 2026-07-24 on `pr308`. A `UsageModelType=Commit` (token) commitment
assetizes cleanly — 3 `TransactionUsageEntitlement` rows all `PROCESSED`, its own
`UsageEntitlementAccount`, 6 `UsageEntitlementBucket` rows. Under identical
conditions (same selling model, same backdating, same `UsageCmtAssetRelatedObj`
junction to an anchor), `CommitmentQuantity` (QB-QTY-CMT) and `CommitmentSpend`
(QB-MTY-CMT) produce:

| | Commit (token) | CommitmentQuantity / CommitmentSpend |
|---|---|---|
| `EntitlementProcessingStatus` | PROCESSED | **PENDING** |
| commitment `UsageEntitlementAccount` | created | **none** |
| `UsageEntitlementBucket` | 6 | **0** |

Nothing errors — no `BatchJobPartFailedRecord`, no failed async job. Both
documented remediations return `isSuccess: true` and change nothing:
the `retriggerEntlCreaProc` invocable ("Retriggers entitlement creation process
for unprocessed assets") and `refreshUsageEntitlementBucket` (the action behind
the **Call Entitlement Refresh Service** flow that the help requires for
backdated assets). The order items are field-identical across all three; the only
difference is `Product2.UsageModelType`.

Until this is resolved, only the three token `Commit` products are demonstrable
end to end.

### Anchor Products Require Token PUR

Products with `UsageModelType='Anchor'` (e.g., QB-DB) require a Token PUR (`QB-DB;QB-TOKEN`) to be active before their non-Token PURs can be activated. This was not required in API 258.

### Currency PUR Dependency

CommitmentSpend products (QB-MTY-CMT) require their Currency-category PUR (`QB-MTY-CMT;UR-USD`) to be Active before any Usage-category PURs can be activated.

### Drawdown order and bases: commitment first (discounted), then grant (raw), then overage

Live-verified 2026-07-25 on `pr308`, reconciled to the last decimal. A spike month
of 3× the standard profile — 15,000 CPU min + 150 TB = **76,500 raw tokens** —
against a `QB-DB-TOKEN` anchor (10,000-token grant) with a linked
`QB-CMT-TKN-FLAT` commitment (25,000 tokens, flat 10%):

| | |
|---|---|
| commitment bucket | drawn in **discounted** tokens — 27,777.78 raw × 0.90 = exactly 25,000 |
| anchor grant | drawn in **raw** tokens — 8,500 compute + 1,500 storage = exactly 10,000 |
| overage | 75,000 − 36,277.78 = 38,722.22 raw, × 0.90 = **34,850** tokens @ 0.5 = **17,425 USD** |

Three rules fall out, and each one breaks a demo if assumed away:

1. **The commitment drains before the anchor grant.** The grant is the *last* line
   of defence, not the first — with a commitment in force and balance remaining, the
   grant is untouched (Infinitech: commitment −17,850, grant 10,000 intact).
2. **The two buckets use different bases.** The commitment decrements by the
   *discounted* quantity; the grant decrements by the *raw* quantity. A grant is an
   included allowance, not a discount — usage it absorbs is never discounted at all,
   which is why the storage line above shows `OverageUnits = 0` and no discount.
3. **`UsageCommitmentPolicy` decides whether the discount survives into overage.**
   Live A/B, same product and same 76,500-token spike, one field apart:

   | | `Lowest Commitment Rate` | `Bounded Object Rate` |
   |---|---|---|
   | debited to buckets | 36,277.78 | 36,277.78 *(identical)* |
   | overage tokens | **34,850** (38,722.22 × 0.90) | **38,722.22** (raw) |
   | billed @ 0.5 | **17,425 USD** | **19,361.11 USD** |

   The drawdown is unaffected — both exhaust the 25,000 commitment and the 10,000
   grant identically. Only the overage differs: `Lowest Commitment Rate` carries the
   discount past the commitment boundary, `Bounded Object Rate` stops it there and
   reverts to the standard anchor rate. Worth exactly 1,936.11 USD here, the 10% the
   customer forfeits. Every QB commit product ships with `'Lowest Rate'`; the
   `'Bounded Object Rate'` record exists but is referenced by nothing.

> ⚠️ **The commitment rate policy is a GLOBAL design-time switch, not a per-deal
> term.** No runtime object snapshots it — not `TransactionUsageEntitlement`,
> `UsageEntitlementAccount`, `UsageEntitlementBucket`, `UsageRatableSummary`, nor
> `AssetRateCardEntry`. It is read from `ProductUsageResourcePolicy` at rating time,
> so changing it alters every deal on that product, including anything that re-rates
> later, and **no record shows which policy produced a given result**. Completed
> periods are safe (their rated values are frozen), which is the only reason the A/B
> above is stable. Unlike `Product2.UsageModelType`, the policy *can* be swapped
> while the PUR is Active.
>
> **`QB-CMT-TKN-BND` exists for exactly this reason.** It is a byte-for-byte clone of
> `QB-CMT-TKN-FLAT` — same 25,000-token grant, same 10% discount on both token
> resources, same Term Annual selling model, same prices in all 7 currencies — except
> its three `ProductUsageResourcePolicy` rows carry `Bounded Object Rate`. Sell FLAT
> and BND side by side and the identical spike bills 17,425 vs 19,361.11 USD. Without
> a second product this is a "flip one field between demos" story that breaks the
> moment two people demo in the same org.
>
> Live-verified as a real catalog product (not a policy flip): sold through
> quote → order → asset, linked to a `QB-DB-TOKEN` anchor, and rated at
> **19,361.111111 USD** on the 76,500-token spike — matching the policy-flip result
> to the last decimal, with both buckets exhausted identically.
>
> ⚠️ The **total** overage is deterministic; the **per-resource split is not**. Two
> bounded runs of the same spike attributed the anchor grant differently — one
> debited storage's 1,500 and put 38,722.22 of compute into overage, the other gave
> compute the whole grant (25,000 ÷ 0.9 + 10,000 = 37,777.78) and pushed all 1,500 of
> storage to overage. Same 38,722.22 total, same bill. Do not write a demo script
> that asserts a particular per-resource debit.
>
> Both sit in the **Consumption** component group (`QB-PCG-USAGE`) of the QuantumBit
> Complete Solution bundle — FLAT at sequence 20, BND at 25.

Read `UsageSummary.ConsumptionUnits` / `DebitedUnits` / `OverageUnits` to decompose a
period; `UsageEntitlementBucket.ConsumedEntitlement` gives the per-bucket totals.
Note `UsageRatableSummary.OverageQuantity` mirrors `TierQuantity` on ordinary rows —
it means "quantity charged beyond the included allowance", not "beyond the
commitment", so it is not on its own evidence that a commitment was exceeded.

### The drawdown lands only when a period COMPLETES

The current billing period stays open, so a spike booked into it sits at
`InProgress` with buckets untouched and no final rating — it looks like a
full-discount, no-drawdown result. Book demo usage into a **past** period. Combined
with the rule below, a backdated demo gets exactly one attempt per account:
**build → consume into the target past period → orchestrate**, because the first
orchestration pass on an account closes every past period empty.

### Record usage BEFORE orchestrating that period — a closed summary never reopens

Live-verified 2026-07-24 on `pr308`, and the single most common way a usage demo
silently produces zeroes.

`Create Empty Summaries` runs at assetization and seeds one `UsageSummary` per
resource per accumulation period in state `New`. A journal is absorbed only
while its period's summary is still open — `New` or `UsageSummaryInProgress`.
**Once the period reaches `RatableSummaryComplete` / `LiableSummaryComplete` it
never reopens**, and a journal that arrives afterwards stays `Pending`
*forever*: never aggregated, never rated, and nothing reports an error. The
rated summary just reads `TierQuantity = 0, TotalAmount = 0`.

The proof: six accounts were given identical June-15 usage. Five had already had
an orchestration pass close out June, and every one of their journals stranded
at `Pending` permanently. The sixth (`Helvetia Cloud`) had been built *after*
that pass, so its June summaries were still open — its journals aggregated and
rated correctly. Re-consuming the five inside the still-open July period then
worked for all of them, confirming the gate is period **completion**, not the
first orchestration pass.

**So the order is per period, and it matters:**

```
build asset  →  record usage  →  run orchestration   (repeat per period)
```

There is no supported way to reopen a completed period. Recovery is to consume
in a period that is still open, or to rebuild on an account whose periods have
never been closed out. Note that `refreshUsageEntitlementBucket` does *not* do
this — it refreshes entitlement buckets for backdated assets, not summaries.

### Period Ordering: Billing >= Rating > Accumulation

The platform requires the three usage periods **in descending order**, and
*equal is not descending*. With all three set to `Monthly` the **Create Empty
Summaries** batch fails every `UsageEntitlementAccount`:

```
Summary Creation Exception: Specify values for the Billing Period, Rating Period
and Usage Accumulation Period parameters in descending order for the usage
resource related to the usage entitlement account ID: ...
```

That failure blocks the whole pipeline — no `UsageSummary`, so no rating, no
billing. The three periods come from three different places:

| Period | Source | QB value |
|--------|--------|----------|
| Billing | `UsageEntitlementAccount.BillingPeriodUnit/Term` (runtime) | Monthly |
| Rating | `RatingFrequencyPolicy.RatingPeriod` | Monthly |
| Accumulation | `UsageResourceBillingPolicy.UsageAccumulationPeriod` | **Daily** |

Accumulation must be **strictly shorter** than rating, which is why the
`dailytotal` / `dailypeak` policies exist and why every QB usage resource points
at one. The `monthlytotal` / `monthlypeak` rows are retained as reference data
for a future model that bills quarterly or annually — pointing a monthly-billed
resource at them reintroduces the failure.

**Two references, one authority.** The accumulation policy is named in *both*
`UsageResource.UsageResourceBillingPolicy.Code` and
`ProductUsageResourcePolicy.UsageAggregationPolicy.Code`. Runtime snapshots the
**`UsageResource`** value onto the `TransactionUsageEntitlement`, so fixing only
the PURP reference leaves the resource default broken while looking correct.
Keep both aligned; `tests/test_qb_multicurrency_data.py::period_ordering_descending`
checks both paths.

`TransactionUsageEntitlement.UsageAggregationPolicyId` is **not writeable**, so
existing entitlements cannot be repointed — a design-time change reaches runtime
only via the policy record itself or a newly created asset.

## File Structure

```
qb-rating/
├── export.json                          # SFDMU data plan (2 passes)
├── README.md                            # This file
│
│  Source CSVs (Pass 1 - Draft status)
├── UnitOfMeasure.csv                    # 18 records
├── UnitOfMeasureClass.csv               # 5 records
├── UsageResourceBillingPolicy.csv       # 5 records
├── UsageResource.csv                    # 7 records
├── Product2.csv                         # 10 records (Update only)
├── UsageGrantRenewalPolicy.csv          # 1 record
├── UsageGrantRolloverPolicy.csv         # 1 record
├── UsageOveragePolicy.csv               # 2 records
├── UsageCommitmentPolicy.csv            # 2 records
├── ProductUsageResource.csv             # 25 records
├── UsagePrdGrantBindingPolicy.csv       # 4 records
├── RatingFrequencyPolicy.csv            # 2 records (Monthly, Daily)
├── ProductUsageResourcePolicy.csv       # 23 records
├── ProductUsageGrant.csv                # 12 records
│
│  Source CSVs (Pass 2 - Activate)
├── objectset_source/
│   └── object-set-2/
│       ├── UnitOfMeasureClass.csv       # 5 records (Status > Active)
│       └── UsageResource.csv            # 5 records (Status > Active)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Data Extraction

This plan supports **bidirectional** operation: in addition to importing data (CSV > org), it can extract data from any org into portable CSVs.

### Extraction via CCI

```bash
# These commands use the CCI default org. To target a specific org, add --org <org>.
cci task run extract_qb_rating_data

# Or use the extract_rating flow to extract both rating and rates
cci flow run extract_rating

# Or run all QB extract tasks (includes rating)
cci flow run run_qb_extracts
```

To run the idempotency test for this plan: `cci task run test_qb_rating_idempotency --org <org>`. To run all QB idempotency tests: `cci flow run run_qb_idempotency_tests --org <org>`. Tasks are in the **Data Management - Extract** and **Data Management - Idempotency** groups. The rating idempotency test uses **extraction roundtrip** — loads from source CSVs, extracts from the org, post-processes, and re-imports — requiring a Draft-only org state. See [Idempotency](#idempotency) for prerequisites.

### Extraction via SFDMU Directly

```bash
sf sfdmu run --sourceusername <org-alias> --targetusername CSVFILE -p datasets/sfdmu/qb/en-US/qb-rating --noprompt --verbose
```

### Post-Processing Extracted CSVs

Raw SFDMU extraction output contains `Active` status values and may have different column ordering. Use the post-processor to convert:

```bash
# Diff only (compare extraction against current plan)
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --diff-only

# Process and write import-ready CSVs
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --output-dir <output-dir>

# Process and update the plan in place
python3 scripts/post_process_extraction.py <extraction-dir> datasets/sfdmu/qb/en-US/qb-rating --copy-to-plan
```

The post-processor:
- Rewrites `Status` fields from `Active`/`Inactive` to `Draft`
- Aligns column order to match the existing plan CSVs
- Aligns composite key columns (individual relationship fields preferred over legacy `$$` notation)
- Generates `objectset_source/` CSVs for Pass 2
- Produces a diff report comparing extraction against the current plan

### Dual-Purpose SOQL Queries

The SOQL queries in `export.json` include both raw ID fields (e.g., `ProductId`) and relationship traversal fields (e.g., `Product.StockKeepingUnit` for PUR records). During **import**, SFDMU uses the traversal fields for lookup resolution. During **extraction**, SFDMU populates these fields with human-readable values (names, codes, SKUs) instead of raw Salesforce IDs, producing portable CSVs.

## Idempotency

The plan is **fully idempotent**: every run deletes ALL PUR, PURP, and PUG records (deleteOldData, no WHERE) and re-inserts from CSV. Consecutive runs always produce PUR=22, PURP=20, PUG=11. No duplicate risk.

The idempotency test (`test_qb_rating_idempotency`) uses **extraction roundtrip** (`use_extraction_roundtrip: true`): loads from source CSVs → extracts from org → post-processes → re-imports from the processed dir, confirming no record count increase. Extraction output is persisted to `datasets/sfdmu/extractions/qb-rating/<timestamp>/`.

**Prerequisite — Draft-only org state**: SFDMU's `deleteOldData` sends a direct REST DELETE. Salesforce rejects deletion of Active PURs and PUGs (the entire batch fails; Active records stay while new Drafts are inserted on top, doubling counts). Before running the idempotency test, all PURs and PUGs must be in Draft status or absent. If `prepare_rating` has been run, clean up first:

```bash
cci task run delete_qb_rates_data   # deactivate + delete rates (reference PURs via FK)
cci task run delete_qb_rating_data  # deactivate + delete PUG → PURP → PUR via Apex
```

**qb-rates note**: `test_qb_rates_idempotency` uses `use_extraction_roundtrip: false` (load-twice without extraction). SFDMU v5 cannot extract 2-hop traversal fields used as components of RABT's composite externalId (`RateCardEntry.RateCard.Name`, `RateUnitOfMeasure.UnitCode`, `UsageResource.Code`) — extraction produces `#N/A` for those components, breaking FK resolution on re-import.

**Full reset and idempotency test (org already has qb-pcm and qb-billing loaded; uses CCI default org):**

```bash
# 1. Delete rates first (they reference PURs), then rating
cci task run delete_qb_rates_data
cci task run delete_qb_rating_data

# 2. Load rating + rates and activate
cci flow run prepare_rating   # ensure options rating=true, rates=true, qb=true match your project config

# 3. Clean up Active records created by prepare_rating (required before idempotency tests)
cci task run delete_qb_rates_data
cci task run delete_qb_rating_data

# 4. Run idempotency tests from clean Draft state
cci task run test_qb_rating_idempotency
cci task run test_qb_rates_idempotency
```

## Cleanup / Re-run

Two cleanup scripts are available:

```bash
# Full cleanup — deletes PUG, PURP, PUR, and policies in reverse dependency order (uses CCI default org)
# Named task (runs scripts/apex/deleteQbRatingData.apex)
cci task run delete_qb_rating_data

# Legacy cleanup — similar scope, different implementation (no named task)
cci task run execute_anon -o path scripts/apex/cleanupRatingRecords.apex
```

These scripts delete PUG, PURP, PUR, binding policies, frequency policies, overage policies, and commitment policies in reverse dependency order. They do **not** delete UoM, UoMClass, UsageResource, or UsageResourceBillingPolicy (managed by qb-billing/qb-pcm).

## Dependencies

This plan depends on the following having been loaded first:

- **qb-pcm** — Product2 records (referenced by SKU), UnitOfMeasure, UnitOfMeasureClass
- **qb-billing** — UsageResourceBillingPolicy, UsageResource (base records)

This plan is a prerequisite for:

- **qb-rates** — RateCardEntry references ProductUsageResource, UsageResource, and Product2 records created here

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found** (excluding standard OwnerId on UsageResource). All reference fields on rating objects are single-target lookups.

### Self-Referencing Fields

| Object         | Field             | Notes                                                    |
|----------------|-------------------|----------------------------------------------------------|
| **UsageResource** | `TokenResourceId` | Self-ref to UsageResource — already handled in plan     |

This self-reference is well-understood and documented in the API 260 Known Issues section above. SFDMU handles it correctly because the token UsageResource records (QB-TOKEN) are inserted first (no parent ref), then usage resources that reference QB-TOKEN are inserted. The Apex activation script handles the complex TokenResourceId pre-population and clear+activate sequence.

### New Fields Found in 260 (Not in Current SOQL)

| Object                       | Field                    | Type      | Updateable | Notes                                                |
|------------------------------|--------------------------|-----------|------------|-------------------------------------------------------|
| **ProductUsageGrant**        | `ProductSellingModelId`  | REFERENCE | Yes        | Lookup to ProductSellingModel — selling model context for grant |
| **ProductUsageResourcePolicy** | `ProductSellingModelId`| REFERENCE | Yes        | Lookup to ProductSellingModel — selling model context for policy |
| **RatingFrequencyPolicy**    | `RatingDelayDurationUnit`| PICKLIST  | Yes        | Unit for rating delay (currently `RatingDelayDuration` is in SOQL without its unit) |
| **UsageCommitmentPolicy**    | `CommitmentRate`         | PICKLIST  | Yes        | Commitment fulfilled rate — controls overage behavior  |

### Field Coverage Audit

| Object                       | Status | Notes                                                        |
|------------------------------|--------|--------------------------------------------------------------|
| UnitOfMeasure                | ✅     | All updateable fields present                                |
| UnitOfMeasureClass           | ✅     | All updateable fields present                                |
| UsageResourceBillingPolicy   | ✅     | All fields present (Code, Name, Status, methods, period)     |
| UsageResource                | ✅     | All fields present including TokenResourceId self-ref        |
| Product2                     | ✅     | Update only (UsageModelType) — correct                       |
| UsageGrantRenewalPolicy      | ✅     | All fields present                                           |
| UsageGrantRolloverPolicy     | ✅     | All fields present                                           |
| UsageOveragePolicy           | ✅     | All fields present (Name, OverageChargeable)                 |
| UsageCommitmentPolicy        | ✅     | `CommitmentRate` now in SOQL (`SELECT Name, CommitmentRate`) |
| ProductUsageResource         | ✅     | All fields present                                           |
| UsagePrdGrantBindingPolicy   | ✅     | All fields present                                           |
| RatingFrequencyPolicy        | ⚠️     | Missing `RatingDelayDurationUnit` (unit for delay duration)  |
| ProductUsageResourcePolicy   | ⚠️     | Missing `ProductSellingModelId` (new lookup)                 |
| ProductUsageGrant            | ⚠️     | Missing `ProductSellingModelId` (new lookup)                 |

### Impact Assessment

- **`ProductUsageGrant.ProductSellingModelId`** and **`ProductUsageResourcePolicy.ProductSellingModelId`**: These new lookups allow associating grants and policies with specific selling models. **High priority** — enables selling-model-specific usage grant configuration, which is a key 260 rating feature.
- **`RatingFrequencyPolicy.RatingDelayDurationUnit`**: Complements the existing `RatingDelayDuration` field with its unit (currently only duration value is captured). **Medium priority** — incomplete without the unit.
- **`UsageCommitmentPolicy.CommitmentRate`**: Controls commitment fulfillment rate behavior. **Resolved** — the SOQL now captures `CommitmentRate` alongside `Name`.

### Cross-Object Dependencies

| Lookup Target              | Source         | Status     |
|----------------------------|----------------|------------|
| Product2                   | qb-pcm         | Update only|
| UnitOfMeasure              | qb-pcm/this    | Upsert     |
| UnitOfMeasureClass         | qb-pcm/this    | Upsert     |
| UsageResourceBillingPolicy | qb-billing/this| Upsert     |
| UsageResource              | This plan      | Upsert     |
| UsageGrantRenewalPolicy    | This plan      | Upsert     |
| UsageGrantRolloverPolicy   | This plan      | Upsert     |
| UsageOveragePolicy         | This plan      | Upsert     |
| UsageCommitmentPolicy      | This plan      | Upsert     |
| RatingFrequencyPolicy      | This plan      | Upsert     |
| ProductSellingModel        | qb-pcm         | Not in plan (new ref) |

**Note:** The new `ProductSellingModelId` lookup on ProductUsageGrant and ProductUsageResourcePolicy references ProductSellingModel from qb-pcm. If these fields are populated, a Readonly ProductSellingModel entry may need to be added to this plan for lookup resolution.

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

| Object                     | Field  | isUnique | isIdLookup | Current ExternalId Uses It? |
|----------------------------|--------|----------|------------|------------------------------|
| UsageResource              | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageResourceBillingPolicy | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageGrantRenewalPolicy    | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UsageGrantRolloverPolicy   | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |
| UnitOfMeasureClass         | `Code` | **Yes**  | Yes        | ✅ Yes (`Code`)              |

All schema-unique fields are already correctly used as externalIds.

### Fields NOT Schema-Unique but Used as ExternalId

| Object                  | Current ExternalId                  | Name AutoNum | isUnique | Risk |
|-------------------------|-------------------------------------|-------------|----------|------|
| UnitOfMeasure           | `UnitCode`                          | No*         | No*      | OK — likely platform-enforced when RLM enabled (verify) |
| UsageOveragePolicy      | `Name`                              | No          | No       | Low — 2 records |
| UsageCommitmentPolicy   | `Name`                              | No          | No       | Low — 1 record |
| UsagePrdGrantBindingPolicy | `Name;Product2.SKU`              | No          | No       | Low — 1 record |
| RatingFrequencyPolicy   | `RatingPeriod`                      | **Yes**     | No       | ⚠️ Picklist — only unique if 1 policy per period |

### Portability Concern: RatingFrequencyPolicy

`RatingFrequencyPolicy.RatingPeriod` is a **picklist** used as the sole externalId. This only works if there is exactly one policy per rating period value. Currently there are 2 records (RatingPeriod = `Monthly` and `Daily`, each period unique), so it works. But if multiple policies per period are needed in the future, a composite key would be required (e.g., `RatingPeriod;Product.StockKeepingUnit;UsageResource.Code`).

**Required `Name` (2026-07-23 fix):** `RatingFrequencyPolicy.Name` is a **required `Text(255)`** field (`nillable=false`, **not** auto-numbered — org describe confirmed). The CSV must supply it; the two rows are `Monthly Rating Frequency` and `Daily Rating Frequency` (the latter added for the QB-DAT-THPT throughput pack). Omitting `Name` makes the `RatingFrequencyPolicy` insert fail with *"Required fields are missing: [Name]"*, which then **silently cascades**: `ProductUsageResourcePolicy` (PURP) rows that reference `RatingFrequencyPolicy.RatingPeriod=Monthly` resolve to `#N/A`, and **Anchor** usage-model products (`QB-DB`, `QB-DB-TOKEN`) *require* `RatingFrequencyPolicyId` — so their PURP inserts are rejected with *"Complete this field when the product… is of Anchor usage model type."* Non-Anchor products (Commit/CommitmentSpend/CommitmentQuantity) leave RFP blank and are unaffected. `Name` is data-only; `RatingPeriod` remains the externalId.

### Auto-Numbered Name Fields

| Object                       | Name Field Type          | Current ExternalId                                     | Assessment |
|------------------------------|--------------------------|--------------------------------------------------------|------------|
| ProductUsageResource         | `ProductUsageResourceNum` (auto-num) | `Product.StockKeepingUnit;UsageResource.Code` (Insert+deleteOldData — v5 can't match by traversal externalId) | ✅ Good |
| ProductUsageGrant            | `ProductUsageGrantNum` (auto-num) | 3-field composite: `UsageDefinitionProduct.StockKeepingUnit;UnitOfMeasureClass.Code;UnitOfMeasure.UnitCode` (Insert+deleteOldData) | ✅ Good |
| ProductUsageResourcePolicy   | `ProductUsageResourcePolicyNum` (auto-num) | `ProductUsageResourceId` (direct FK, 1:1 with PUR) + `deleteOldData:true` | ✅ Good — SFDMU v5 safe pattern for all-multi-hop externalIds |
| RatingFrequencyPolicy        | Auto-num                 | `RatingPeriod`                                          | ⚠️ Picklist only (see above) |

### Composite Key Complexity

| Object                       | Key Fields | Complexity | Simplification? |
|------------------------------|-----------|------------|-----------------|
| UnitOfMeasure                | 1 (`UnitCode`) | Simple | No |
| UnitOfMeasureClass           | 1 (`Code`) | Simple | No — schema-unique |
| UsageResource                | 1 (`Code`) | Simple | No — schema-unique |
| ProductUsageResource         | 2 (Product.StockKeepingUnit + UsageResource.Code) | Low | No — junction natural key |
| UsagePrdGrantBindingPolicy   | 2 (Name + Product2.SKU) | Low | No |
| ProductUsageResourcePolicy   | 1 (`ProductUsageResourceId` + `deleteOldData`) | Medium | No — SFDMU v5 requires direct field; `$$` composite caused SOQL injection |
| ProductUsageGrant            | **5** fields | **High** | No — all 5 required for uniqueness (grant per product per UoM per PUR) |

## Optimization Opportunities

1. **Add `ProductSellingModelId` to PUG and PURP SOQL**: New 260 field for selling-model-specific usage grants and policies. May require adding ProductSellingModel as Readonly in this plan.
2. ~~**Add `CommitmentRate` to UsageCommitmentPolicy SOQL**~~: Resolved — `CommitmentRate` is now in the query
3. **Add `RatingDelayDurationUnit` to RatingFrequencyPolicy SOQL**: Completes the delay duration configuration
4. **Investigate RatingFrequencyPolicy externalId**: If more policies per period are expected, switch to a composite key
5. **Fix `excludeIdsFromCSVFiles`**: Currently set to `"false"` — change to `"true"` for portability (same concern as qb-tax)
6. **Coordinate LegalEntity fields**: If qb-billing or qb-tax add LegalEntity geo/email fields, this plan's upstream dependencies should be kept in sync

## Known Limitations / Future Work

### TODO: Multi-Shape / Overlay Support

**Current limitation**: This plan uses `deleteOldData: true` with no WHERE clause on PUR, PURP, and PUG. That means each plan run deletes **all** records of each type and re-inserts only what is in these CSVs. The plan assumes it is the sole owner of all rating data on the org. Loading a second data shape (e.g., a different product family's rating config) on the same org will cause the first shape's records to be wiped on the next run of either plan.

**Requirements to investigate**:
1. **Fresh build from scratch with multiple shapes** — support composing any number of data shapes on the same org without shapes overwriting each other. Each shape should be independently loadable and re-runnable without affecting sibling shapes.
2. **Drift capture per shape** — extract modifications made to an org and identify drift against the shape's baseline CSVs. Must work even when multiple shapes coexist.
3. **Test and approval workflow** — verify extracted drift (diff against baseline), present for review, then decide:
   - **Merge into base shape**: update the shape's source CSVs and commit.
   - **Configure as overlay in a downstream CCI project**: keep the base shape unchanged and add shape-specific overrides in a child project.
4. **Downstream CCI overlay pattern** — investigate how to configure shape variants as overlays (additional plans, post-load Apex, or plan extensions) in downstream CCI projects that inherit this base.

**Alternatives to investigate**:
- **WHERE-clause scoped plans**: Filter deleteOldData by a discriminator (e.g., product family SKU prefix). SFDMU does not natively support dynamic WHERE on deleteOldData — would require pre-filtering CSVs or a wrapper task.
- **Shape-discriminated externalIds**: Tag each PUR/PUG with a shape identifier, scope deletes to only that shape's records.
- **Upsert-based approach**: Would eliminate the deleteOldData all-or-nothing problem, but requires SFDMU v5 traversal-externalId bug fixes (Bugs 2 & 3) or a workaround.
- **CCI project inheritance overlay**: Each shape defined as a separate plan in its own CCI project that extends this base, loaded in sequence after the base plan.
