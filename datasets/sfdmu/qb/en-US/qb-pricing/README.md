# qb-pricing Data Plan

SFDMU data plan for QuantumBit (QB) pricing configuration. Creates pricebook entries, price adjustment schedules/tiers, attribute-based adjustments, bundle-based adjustments, derived prices, cost books, and currency types.

## CCI Integration

### Flow: `prepare_pricing_data`

This plan is executed as **step 1** of the `prepare_pricing_data` flow (when `qb=true`).

| Step | Task                              | Description                                    |
|------|-----------------------------------|------------------------------------------------|
| 1    | `insert_quantumbit_pricing_data`  | Runs this SFDMU plan (single pass)             |

A separate flow, `prepare_price_adjustment_schedules`, activates PriceAdjustmentSchedule records via Apex on scratch orgs:

| Step | Task                                   | Description                                        |
|------|----------------------------------------|----------------------------------------------------|
| 1    | `activate_price_adjustment_schedules`  | Runs `activatePriceAdjustmentSchedules.apex` (scratch only) |

### Task Definition

```yaml
insert_quantumbit_pricing_data:
  class_path: tasks.rlm_sfdmu.LoadSFDMUData
  options:
    pathtoexportjson: "datasets/sfdmu/qb/en-US/qb-pricing"
```

## Data Plan Overview

The plan uses a **single SFDMU pass** with 16 objects. Three objects are `Readonly` (Product2, ProductSellingModel, AttributeDefinition) — they provide SFDMU with lookup context for parent resolution without modifying them. `PriceAdjustmentSchedule` uses an `Update` operation (not Upsert), meaning the records must already exist (auto-created by the platform when the pricebook is created).

```
Single Pass (SFDMU)                             Apex Activation (scratch only)
────────────────────────────────────            ─────────────────────────────────
Upsert/Update pricing objects            ->     activatePriceAdjustmentSchedules.apex
(Readonly parents for lookup resolution)        (activates 5 standard schedules)
```

### Objects

| #  | Object                       | Operation | External ID                                                                                             | Records |
|----|------------------------------|-----------|---------------------------------------------------------------------------------------------------------|---------|
| 1  | CurrencyType                 | Upsert    | `IsoCode`                                                                                               | 7       |
| 2  | ProrationPolicy              | Upsert    | `Name`                                                                                                  | 1       |
| 3  | ProductSellingModel          | Readonly  | `Name;SellingModelType`                                                                                 | 9       |
| 4  | AttributeDefinition          | Readonly  | `Code`                                                                                                  | 39      |
| 5  | Product2                     | Readonly  | `StockKeepingUnit`                                                                                      | 164     |
| 6  | Pricebook2                   | Upsert    | `Name;IsStandard`                                                                                       | 1       |
| 7  | CostBook                     | Upsert    | `Name;IsDefault`                                                                                        | 0       |
| 8  | PriceAdjustmentTier          | Upsert    | `PriceAdjustmentSchedule.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType;TierType;TierValue;LowerBound;CurrencyIsoCode;EffectiveFrom` | 3 |
| 9  | PriceAdjustmentSchedule      | Update    | `Name;CurrencyIsoCode;Pricebook2.Name`                                                                 | 3       |
| 10 | AttributeBasedAdjRule        | Upsert    | `Name`                                                                                                  | 4       |
| 11 | AttributeAdjustmentCondition | Upsert    | `AttributeBasedAdjRule.Name;AttributeDefinition.Code;Product.StockKeepingUnit`                          | 4       |
| 12 | AttributeBasedAdjustment     | Upsert    | `AttributeBasedAdjRule.Name;PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` | 4 |
| 13 | BundleBasedAdjustment        | Upsert    | `PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ParentProduct.StockKeepingUnit;RootBundle.StockKeepingUnit;ProductSellingModel.Name;ParentProductSellingModel.Name;RootProductSellingModel.Name;CurrencyIsoCode` | 2 |
| 14 | PricebookEntry               | Upsert    | `Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode`                   | 114     |
| 15 | PricebookEntryDerivedPrice   | Upsert    | `Pricebook.Name;PricebookEntry.Pricebook2.Name;PricebookEntry.Product2.StockKeepingUnit;PricebookEntry.ProductSellingModel.Name;Product.StockKeepingUnit;ContributingProduct.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` | 2 |
| 16 | CostBookEntry                | Upsert    | `CostBook.Name;Product.StockKeepingUnit;CurrencyIsoCode`                                               | 0       |

**Note:** CostBook and CostBookEntry have empty CSVs (0 data records) — placeholders for future cost data. `PriceAdjustmentSchedule` is an `Update` operation with a `WHERE ContractId = NULL` filter, meaning it only updates non-contract schedules that were auto-created by the platform.

## Apex Activation Script

**File:** `scripts/apex/activatePriceAdjustmentSchedules.apex`

Activates 5 standard PriceAdjustmentSchedule records by name:
- Standard Attribute Based Adjustment
- Standard Bundle Based Adjustment
- Standard Price Adjustment Tier
- Standard Tier Based Adjustment
- Standard Volume Based Adjustment

This script only runs on **scratch orgs** (gated by `when: org_config.scratch` in the flow).

## Key Object Groups

### Currency and Proration (Objects 1-2)

Currency types (7 currencies including USD, CAD, EUR, etc.) and proration policy.

### Pricebooks and Entries (Objects 6, 14)

One non-standard pricebook with 114 pricebook entries mapping products to selling models with unit prices and currency.

### Price Adjustments (Objects 8-9, 10-12, 13)

- **PriceAdjustmentSchedule** (Update): Updates existing auto-created schedules
- **PriceAdjustmentTier**: Tier-based pricing rules
- **AttributeBasedAdjRule/Condition/Adjustment**: Rules for attribute-driven price modifications
- **BundleBasedAdjustment**: Bundle-specific pricing adjustments

### Derived Pricing (Object 15)

PricebookEntryDerivedPrice records that compute prices from contributing products via formulas.

## Composite External IDs

Several objects use complex multi-field composite keys:

| Object                       | Key Components | CSV `$$` Column |
|------------------------------|----------------|-----------------|
| ProductSellingModel          | Name + SellingModelType | Yes       |
| Pricebook2                   | Name + IsStandard | Yes            |
| CostBook                     | Name + IsDefault | Yes             |
| PriceAdjustmentTier          | 9-field composite | Yes            |
| PriceAdjustmentSchedule      | Name + CurrencyIsoCode + Pricebook2.Name | Yes |
| AttributeAdjustmentCondition | 3-field composite | Yes            |
| AttributeBasedAdjustment     | 5-field composite | Yes            |
| BundleBasedAdjustment        | 8-field composite | Yes            |
| PricebookEntry               | 4-field composite | Yes            |
| PricebookEntryDerivedPrice   | 8-field composite | Yes            |
| CostBookEntry                | 3-field composite | Yes            |

Nested `$$` columns are used for parent lookup resolution (e.g., `PriceAdjustmentSchedule.$$Name$CurrencyIsoCode$Pricebook2.Name`, `ProductSellingModel.$$Name$SellingModelType`).

## Portability

### PORTABILITY ISSUE: `AttributeBasedAdjRule.Name`

`AttributeBasedAdjRule` uses timestamp-based auto-generated names as its external ID:

```
Rule_1724814105445
Rule_1724814147720
Rule_1724814176583
Rule_1724814263993
```

These names are **not portable** across orgs — they are generated at insert time and will differ between environments. This affects:
- `AttributeBasedAdjRule` itself (externalId: `Name`)
- `AttributeAdjustmentCondition` (externalId includes `AttributeBasedAdjRule.Name`)
- `AttributeBasedAdjustment` (externalId includes `AttributeBasedAdjRule.Name`)

**Recommended fix:** Replace `Name` with a stable, human-readable alternative field, or rename the rules to descriptive values. Needs investigation to determine if `AttributeBasedAdjRule` has a `DeveloperName` or `Code` field that could be used instead.

### Other External IDs

All other external IDs use portable fields:
- `IsoCode` for CurrencyType
- `StockKeepingUnit` for Product2 references
- `Name` for ProrationPolicy, Pricebook2 (human-readable)
- `Code` for AttributeDefinition
- Composite keys built from the above portable fields

## Dependencies

**Upstream:**
- **qb-pcm** — Product2 (SKU), ProductSellingModel (Name;SellingModelType), ProrationPolicy, AttributeDefinition (Code)

**Downstream:**
- None directly — pricing is consumed at runtime by the quoting/ordering engine

## File Structure

```
qb-pricing/
├── export.json                          # SFDMU data plan (single pass, 16 objects)
├── README.md                            # This file
│
│  Source CSVs — Currency and Proration
├── CurrencyType.csv                     # 7 records
├── ProrationPolicy.csv                  # 1 record
│
│  Source CSVs — Readonly Parents (lookup context)
├── ProductSellingModel.csv              # 9 records (Readonly)
├── AttributeDefinition.csv              # 39 records (Readonly)
├── Product2.csv                         # 164 records (Readonly)
│
│  Source CSVs — Pricebooks
├── Pricebook2.csv                       # 1 record
├── PricebookEntry.csv                   # 114 records
├── PricebookEntryDerivedPrice.csv       # 2 records
│
│  Source CSVs — Price Adjustments
├── PriceAdjustmentSchedule.csv          # 3 records (Update only)
├── PriceAdjustmentTier.csv              # 3 records
│
│  Source CSVs — Attribute-Based Adjustments
├── AttributeBasedAdjRule.csv            # 4 records (PORTABILITY ISSUE)
├── AttributeAdjustmentCondition.csv     # 4 records
├── AttributeBasedAdjustment.csv         # 4 records
│
│  Source CSVs — Bundle Adjustments
├── BundleBasedAdjustment.csv            # 2 records
│
│  Source CSVs — Cost Books (placeholders)
├── CostBook.csv                         # 0 records (placeholder)
├── CostBookEntry.csv                    # 0 records (placeholder)
│
│  SFDMU Runtime (gitignored)
├── source/                              # SFDMU-generated source snapshots
└── target/                              # SFDMU-generated target snapshots
```

## Idempotency

This plan should be idempotent via SFDMU's Upsert/Update operations with composite external IDs. The `Readonly` objects ensure parent lookup resolution without modification.

**Potential issue:** `PriceAdjustmentSchedule` uses `Update` operation — if the schedules don't exist yet (e.g., fresh org before pricebook creation), the update will find no matching records. Verify that platform auto-creates these schedules when the pricebook is created.

**Not yet validated** — idempotency testing against a 260 org is pending.

## 260 Schema Analysis (Confirmed via Org Describe)

Schema was queried against a 260 scratch org. Findings below.

### Polymorphic Fields

**None found.** All reference fields on pricing objects are single-target lookups.

### Self-Referencing Fields

**None found.** No pricing objects reference themselves.

### New Fields Found in 260 (Not in Current SOQL)

| Object                | Field              | Type     | Updateable | Notes                                               |
|-----------------------|--------------------|----------|------------|------------------------------------------------------|
| **AttributeBasedAdjRule** | `UsageType`    | PICKLIST | Yes        | Usage type categorization — likely needed for usage-rated pricing |

### Field Coverage Audit

All other objects have **complete field coverage** — every updateable, non-system field in the 260 schema is included in the current SOQL queries:

| Object                       | Status | Notes                                              |
|------------------------------|--------|----------------------------------------------------|
| CurrencyType                 | ✅     | All 4 updateable fields present                    |
| ProrationPolicy              | ✅     | All 4 fields present (all read-only after create)  |
| Pricebook2                   | ✅     | All updateable fields; `IsArchived` correctly omitted (read-only) |
| CostBook                     | ✅     | All 4 updateable fields present                    |
| PriceAdjustmentTier          | ✅     | All updateable + read-only formula fields present   |
| PriceAdjustmentSchedule      | ✅     | All updateable fields; `ContractId` correctly filtered |
| AttributeBasedAdjRule        | ⚠️     | Missing `UsageType` (see above)                    |
| AttributeAdjustmentCondition | ✅     | All fields present; `UsageType` is read-only here   |
| AttributeBasedAdjustment     | ✅     | All fields present (many read-only formula fields)  |
| BundleBasedAdjustment        | ✅     | All fields present (many read-only formula fields)  |
| PricebookEntry               | ✅     | `UseStandardPrice` omitted (typically false, minor) |
| PricebookEntryDerivedPrice   | ✅     | All fields present                                  |
| CostBookEntry                | ✅     | All fields present                                  |

### Cross-Object Dependencies

All lookup targets are either included in the plan (as Upsert or Readonly) or exist from upstream plans:

| Lookup Target          | Source Plan | Status     |
|------------------------|-------------|------------|
| Product2               | qb-pcm      | Readonly   |
| ProductSellingModel    | qb-pcm      | Readonly   |
| AttributeDefinition    | qb-pcm      | Readonly   |
| CostBook               | This plan   | Upsert     |
| Pricebook2             | This plan   | Upsert     |
| PriceAdjustmentSchedule| This plan   | Update     |
| AttributeBasedAdjRule  | This plan   | Upsert     |
| PricebookEntry         | This plan   | Upsert     |
| Contract               | N/A         | Filtered out via WHERE |

## External ID / Composite Key Analysis (Confirmed via Org Describe)

### Schema-Enforced Unique Fields

No pricing-specific objects have schema-enforced unique fields (`isUnique=true`). All externalIds rely on convention-unique values (human-readable Names, Codes from upstream plans).

### Auto-Numbered Name Fields (Portability Assessment)

| Object                       | Name Auto-Num | Current ExternalId                                     | Assessment |
|------------------------------|---------------|--------------------------------------------------------|------------|
| PriceAdjustmentTier          | **Yes**       | 9-field composite (PAS.Name + Product.SKU + PSM.Name + ...) | ✅ Good — comprehensive composite |
| AttributeAdjustmentCondition | **Yes**       | `ABR.Name;AttrDef.Code;Product.SKU`                   | ⚠️ Depends on ABR.Name (timestamp) |
| AttributeBasedAdjustment     | **Yes**       | `ABR.Name;PAS.Name;Product.SKU;PSM.Name;Currency`     | ⚠️ Depends on ABR.Name (timestamp) |
| BundleBasedAdjustment        | **Yes**       | 8-field composite                                       | ✅ Good — all parent refs |
| PricebookEntryDerivedPrice   | **Yes**       | 8-field composite                                       | ✅ Good — all parent refs |
| CostBookEntry                | **Yes**       | `CostBook.Name;Product.SKU;CurrencyIsoCode`            | ✅ Good — all parent refs |

### Portability Issue: AttributeBasedAdjRule Name Cascade

`AttributeBasedAdjRule.Name` is **not auto-numbered** but contains **timestamp-based values** (e.g., `Rule_1724814105445`). The schema confirms:
- `Name`: `autoNum=false`, `unique=false`, `idLookup=true`, `updateable=true`
- `UsageType`: only other non-system field (new in 260)

There is **no alternative unique field** — `AttributeBasedAdjRule` has no `Code`, `DeveloperName`, or other candidate. The only fix is to **rename the Name values** to something human-readable and portable (e.g., `GPU-Memory-Size-Rule`, `Storage-Type-Rule`).

This timestamp Name cascades to 2 dependent objects:
- `AttributeAdjustmentCondition.externalId` includes `AttributeBasedAdjRule.Name`
- `AttributeBasedAdjustment.externalId` includes `AttributeBasedAdjRule.Name`

### Composite Key Complexity

| Object                       | Key Fields | Complexity | Simplification? |
|------------------------------|-----------|------------|-----------------|
| CurrencyType                 | 1 (`IsoCode`) | Simple | No |
| ProrationPolicy              | 1 (`Name`) | Simple | No |
| Pricebook2                   | 2 (`Name;IsStandard`) | Low | No — `Name` alone isn't unique (Standard + custom can share names) |
| CostBook                     | 2 (`Name;IsDefault`) | Low | No |
| PriceAdjustmentSchedule      | 3 (`Name;Currency;PB.Name`) | Medium | No — Name alone may not be unique across pricebooks |
| PriceAdjustmentTier          | **9** fields | **Very High** | Possible — investigate if a subset guarantees uniqueness |
| AttributeBasedAdjustment     | 5 fields | High | No — multi-dimensional adjustment targeting |
| BundleBasedAdjustment        | **8** fields | **Very High** | No — bundle hierarchy requires all dimensions |
| PricebookEntry               | 4 fields | Medium | No — PBE is Product+PB+PSM+Currency |
| PricebookEntryDerivedPrice   | **8** fields | **Very High** | Possible — contributing product may be enough to narrow |
| CostBookEntry                | 3 fields | Medium | No |

**PriceAdjustmentTier** has the most complex key (9 fields). Investigate whether `PriceAdjustmentSchedule.Name;LowerBound;TierType;CurrencyIsoCode` would be sufficient as a simpler unique combination.

## Optimization Opportunities

1. **Fix `AttributeBasedAdjRule` portability**: Rename timestamp-based `Name` values to human-readable names — no alternative unique field exists
2. **Add `UsageType` to `AttributeBasedAdjRule` SOQL**: New 260 field not in current query
3. **Investigate PriceAdjustmentTier key simplification**: Test whether a 4-5 field subset of the 9-field key is sufficient for uniqueness
4. **Investigate PricebookEntryDerivedPrice key simplification**: Test whether fewer fields uniquely identify derived prices
5. **Extraction available**: Use `extract_qb_pricing_data` (Data Management - Extract). Run all extracts: `cci flow run run_qb_extracts --org <org>`. Idempotency: `test_qb_pricing_idempotency` / `cci flow run run_qb_idempotency_tests --org <org>`.
6. **Verify CostBook availability**: Confirm CostBook and CostBookEntry objects exist in 260 or remove the placeholders
7. **Consider activation flow integration**: The `prepare_price_adjustment_schedules` flow is separate from `prepare_pricing_data` — consider whether they should be combined
8. **Consistency**: Uses `objectSets` wrapper — consider switching to flat `objects` array for consistency with qb-pcm
