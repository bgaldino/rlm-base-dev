# customer-template-pricing

Attribute-based pricing plan for customer demo catalogs. Implements attribute-driven **Percentage** price adjustments on API platform products using the three-object RLM pricing chain:

```
AttributeBasedAdjRule → AttributeAdjustmentCondition → AttributeBasedAdjustment
```

---

## What This Plan Does

API Model Tier (`OAI-MODEL-TIER`) is a price-impacting attribute on the two API platform SKUs. When a buyer configures their model tier during quoting, the platform evaluates all `AttributeBasedAdjRule` records associated with the product and its `PriceAdjustmentSchedule`, finds the matching condition, and applies the corresponding `AttributeBasedAdjustment` percentage adjustment.

### Pricing Table

| SKU | Tier | Adjustment |
|---|---|---|
| `OAI-API-DEV` | Frontier | +25% (monthly) |
| `OAI-API-ENT` | Efficient | −15% (annual) |
| `OAI-API-ENT` | Frontier | +30% (annual) |

Professional is the default tier (no rule; uses Standard PricebookEntry list price).

---

## Architecture — 2-Phase Load

AAC and ABA records **cannot be loaded via SFDMU** due to an FK resolution bug (see Lesson 7 below). The load is split into two CCI tasks:

| Phase | Task | Mechanism | Objects |
|---|---|---|---|
| 1 | `insert_customer_demo_pricing_data` | SFDMU | `AttributeBasedAdjRule` Upsert |
| 2 | `insert_customer_demo_pricing_adjustments` | Apex | `AttributeAdjustmentCondition` Insert, `AttributeBasedAdjustment` Insert |

---

## Objects Loaded

| Object | Operation | Count | ExternalId |
|---|---|---|---|
| `AttributeBasedAdjRule` | Upsert (SFDMU) | 3 | `Name` |
| `AttributeAdjustmentCondition` | Insert (Apex) | 3 | n/a — Apex, not SFDMU |
| `AttributeBasedAdjustment` | Insert (Apex) | 3 | n/a — Apex, not SFDMU |

**Readonly CSVs in `export.json`** (`Product2`, `AttributeDefinition`, `ProductSellingModel`, `PriceAdjustmentSchedule`, `AttributeBasedAdjRule`) are present for reference only — they are not queried for the Apex phase. The SFDMU phase only loads ABRs.

---

## CumulusCI Tasks

```bash
# Load attribute-based pricing (steps 8–9b of prepare_customer_demo_catalog)
cci task run delete_customer_demo_pricing_data --org <alias>
cci task run insert_customer_demo_pricing_data --org <alias>
cci task run insert_customer_demo_pricing_adjustments --org <alias>

# Verify
cci task run customer_demo_verify_catalog --org <alias>
```

---

## Order of Operations

**Within `prepare_customer_demo_catalog`:**

```
Step 2:  insert_customer_demo_pcm_data           (Product2, attributes, classifications)
Step 7:  customer_demo_recreate_pricebook_via_api  (Standard PBE with PSM)
Step 8:  delete_customer_demo_pricing_data        (scoped Apex delete of ABR+ABA)
Step 9:  insert_customer_demo_pricing_data        (SFDMU: ABR Upsert)
Step 9b: insert_customer_demo_pricing_adjustments (Apex: AAC+ABA Insert)
Step 10: customer_demo_verify_catalog
```

**Why pricing runs after pricebook (step 7):** `AttributeBasedAdjustment` doesn't FK to `PricebookEntry`, so technically pricing can load any time after Product2 and AttributeDefinition exist. Placing it after pricebook keeps the logical flow: "list prices first, then adjustments."

**Why delete runs before insert (step 8):** `AttributeAdjustmentCondition` and `AttributeBasedAdjustment` use Insert (not Upsert) because their externalIds are all-relationship-traversal — SFDMU Bug 3 would cause Upsert to always insert and never match. The Apex insert script is idempotent (skips if records already exist), but running the delete first keeps re-runs clean.

**Why delete is scoped (Apex, not DeleteSFDMUData):** `DeleteSFDMUData` deletes **all** records of Insert-operation object types. If QB pricing data coexists in the same org, this would wipe those records too. The Apex script scopes deletion to `WHERE Name LIKE 'OAI-%'`.

---

## Lessons Learned (Debugging Notes)

These pitfalls were discovered during development and are documented here for future implementors.

### 1. Two-ObjectSet Architecture is Required for Fresh Parent Inserts

**Problem:** When `AttributeBasedAdjRule` is Upserted in the same `objectSet` as `AttributeAdjustmentCondition` and `AttributeBasedAdjustment` Inserts, the child inserts fail silently.

**Root cause:** SFDMU builds its parent FK lookup map during **STAGE 2** (before the UPDATE phase). If ABR records don't exist yet at STAGE 2 query time (because they were deleted before the run), the FK map for ABR is empty. When SFDMU later tries to insert ABA (which references ABR), it crashes with `COMMAND_UNEXPECTED_ERROR`.

**Nominal fix:** Two `objectSets`: Set 1 ABR Upsert only; Set 2 Readonly parents + AAC/ABA Insert. However, see Lesson 7 below — even the two-objectSet approach has a SFDMU limitation for AAC/ABA.

### 2. SFDMU Parallelizes objectSet Data Fetching (Cross-objectSet Race Condition)

**Problem:** In a single `export.json` with two objectSets, SFDMU fetches Readonly query results for **all objectSets simultaneously** during STAGE 2 — before Set 1's Upserts are committed. This means the Readonly ABR fetch in Set 2 can return 0 records if Set 1's ABR inserts haven't yet landed in the org.

**Workaround:** Run ABR loading as a separate CCI task (`insert_customer_demo_pricing_data`) that completes before the AAC/ABA task starts. However, even with separate sequential tasks, Lesson 7 applies.

### 3. SELECT Queries Must Use Direct ID Fields, Not Relationship-Traversal

**Problem:** SFDMU crashes with `COMMAND_UNEXPECTED_ERROR` during AAC Insert when the SELECT query uses traversal fields like `AttributeBasedAdjRule.Name`, `AttributeDefinition.Code`, `Product.StockKeepingUnit`.

SFDMU logs: `Referenced field removed from the script query. It will be added automatically if required.` When SFDMU removes these fields, it also loses the FK context for the INSERT phase.

**Fix:** Use direct ID fields in the SELECT:
```sql
-- CORRECT
SELECT AttributeBasedAdjRuleId, AttributeDefinitionId, BooleanValue,
       DateValue, DateTimeValue, DoubleValue, IntegerValue, Operator, ProductId, StringValue
FROM AttributeAdjustmentCondition
```

### 4. AAC CSV Column Count — Empty Fields Require Explicit Commas

The `AttributeAdjustmentCondition` CSV has 11 columns. Five value-type columns (BooleanValue, DateTimeValue, DateValue, DoubleValue, IntegerValue) are empty for string-value conditions. Missing even one comma causes `Operator` to land in the wrong column.

**Column layout (11 total):**
```
1.  $$AttributeBasedAdjRule.Name$AttributeDefinition.Code$Product.StockKeepingUnit
2.  AttributeBasedAdjRule.Name
3.  AttributeDefinition.Code
4.  BooleanValue          (empty for string conditions)
5.  DateTimeValue         (empty for string conditions)
6.  DateValue             (empty for string conditions)
7.  DoubleValue           (empty for string conditions)
8.  IntegerValue          (empty for string conditions)
9.  Operator              ("equals" for picklist value matching)
10. Product.StockKeepingUnit
11. StringValue           (the AttributePicklistValue.Value)
```

For a string-value condition: `RULE;ATTR;SKU,RULE,ATTR,,,,,,equals,SKU,StringValue`

### 5. AttributeAdjustmentCondition Cannot Be Deleted Directly via DML

`Database.delete` on `List<AttributeAdjustmentCondition>` fails: `DML operation Delete not allowed on List<AttributeAdjustmentCondition>`.

**Fix:** Delete `AttributeBasedAdjRule` (which cascades AAC automatically). Delete `AttributeBasedAdjustment` first (explicit DML — ABA is NOT cascade from ABR):
```apex
delete [SELECT Id FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRuleId IN :ruleIds];
delete [SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE 'OAI-%'];
```

### 6. ABA Read-Only Fields — Leave Blank in CSV, Omit from Apex Constructor

`AttributeBasedAdjustment` has platform-computed read-only fields:

| Field | Source | Write on INSERT |
|---|---|---|
| `AttributeAdjConditionsHash` | Platform computes from conditions | ❌ read-only |
| `AttributeCount` | Platform counts conditions | ❌ read-only |
| `PricingTerm` | Derived from ProductSellingModel | ❌ read-only |
| `PricingTermUnit` | Derived from ProductSellingModel | ❌ read-only |
| `ScheduleType` | Derived from PriceAdjustmentSchedule | ❌ read-only |
| `SellingModelType` | Derived from ProductSellingModel | ❌ read-only |

Including these in an Apex constructor causes a compile error. Leave them blank in CSVs; omit them from Apex SObject constructors.

### 7. SFDMU Cannot Resolve Relationship-Traversal FK Columns for AAC/ABA Inserts — Even With Separate Tasks and Populated Readonly CSVs

**Problem:** Even when `insert_customer_demo_pricing_data` (SFDMU) runs first and fully commits ABRs to the org, a subsequent separate SFDMU task for AAC/ABA Insert reports `SOURCE: 0` for both objects — despite the CSV files having 3 data rows each.

**Root cause:** For `Insert` operations, SFDMU resolves FK columns (e.g., `AttributeBasedAdjRule.Name` → `AttributeBasedAdjRuleId`) by looking up the parent object's **SOURCE** ID collection. For `Readonly` parent objects, SFDMU fetches from the TARGET org (getting real Salesforce IDs) but stores these in the **TARGET** collection, not SOURCE. When building the INSERT payload for child objects, SFDMU uses the SOURCE collection for FK mapping — which is empty for Readonly parents. All child rows fail FK resolution and are silently dropped (SOURCE count: 0).

Populating the Readonly CSVs with actual data rows does not fix this: the `_source.csv` files confirm SFDMU reads the data correctly, but the FK mapping still uses TARGET IDs not SOURCE IDs, and the resolution step filters all rows.

**Fix:** Use Apex for AAC and ABA. Apex resolves all FKs explicitly via SOQL and is fully deterministic:

```apex
// scripts/apex/insertCustomerDemoPricingAdjustments.apex
// Wired as CCI task insert_customer_demo_pricing_adjustments (AnonymousApexTask)
```

This is the **authoritative approach** for all customer demo AAC/ABA loads. The SFDMU CSVs (`AttributeAdjustmentCondition.csv`, `AttributeBasedAdjustment.csv`) are maintained as documentation of the intended data shape and for use during extraction roundtrips.

### 8. AttributeAdjustmentCondition.Operator Picklist Values

The `Operator` field uses the picklist value `equals`, not `=`. Any other value (including `=`) causes `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST` at INSERT time.

---

## Verification

The `customer_demo_verify_catalog` task checks attribute-based pricing when `ExpectedPricingRules` is non-empty in `customer-pricebook-entries.csv`. For OAI API products:
- `OAI-API-DEV`: `ExpectedPricingRules=1` (one ABA record — Frontier tier premium)
- `OAI-API-ENT`: `ExpectedPricingRules=2` (two ABA records — Efficient discount + Frontier premium)

```bash
cci task run customer_demo_verify_catalog --org <alias>
```

Verify manually:
```bash
sf data query -q "SELECT AttributeBasedAdjRule.Name, AdjustmentType, AdjustmentValue, Product.StockKeepingUnit, ProductSellingModel.Name FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRule.Name LIKE 'OAI-%' ORDER BY AttributeBasedAdjRule.Name" --target-org <username>

sf data query -q "SELECT AttributeBasedAdjRule.Name, Operator, StringValue, Product.StockKeepingUnit FROM AttributeAdjustmentCondition WHERE AttributeBasedAdjRule.Name LIKE 'OAI-%'" --target-org <username>
```

Expected: 3 ABR + 3 AAC + 3 ABA records.

---

## Extending to Other Customers

To adapt this pricing plan for a new customer:

1. **Update `AttributeBasedAdjRule.csv`** — replace `OAI-*` names with the new customer's prefix (e.g., `ACME-API-PRO-TIER`).
2. **Update `AttributeAdjustmentCondition.csv`** — update the `$$` key, `AttributeBasedAdjRule.Name`, `AttributeDefinition.Code`, `Product.StockKeepingUnit`, and `StringValue` columns.
3. **Update `AttributeBasedAdjustment.csv`** — update rule names, product SKUs, selling models, and adjustment values.
4. **Update `scripts/apex/insertCustomerDemoPricingAdjustments.apex`** — change ABR name patterns, attribute codes, SKUs, and adjustment values.
5. **Update `scripts/apex/deleteCustomerDemoPricingData.apex`** — change the `LIKE` scope to the new customer prefix.
6. **Update `customer-pricebook-entries.csv`** — set `ExpectedPricingRules` for any new SKUs with attribute-based pricing.
7. **Re-run the delete + 2-phase insert cycle** and verify.

---

## Related Files

| File | Purpose |
|---|---|
| `scripts/apex/deleteCustomerDemoPricingData.apex` | Scoped delete (OAI-* rules only) |
| `scripts/apex/insertCustomerDemoPricingAdjustments.apex` | Insert AAC + ABA (phase 2) |
| `scripts/customer-demo/customer-pricebook-entries.csv` | `ExpectedPricingRules` column drives ABA count verification |
| `tasks/rlm_customer_demo.py` | `VerifyCustomerDemoCatalog._run_task()` — `ExpectedPricingRules` check |
| `datasets/sfdmu/customer-template/en-US/customer-template-pcm/ProductAttributeDefinition.csv` | `IsPriceImpacting=true` on `OAI-MODEL-TIER` for API SKUs |
| `datasets/sfdmu/qb/en-US/qb-pricing/` | Reference plan (QB attribute-based pricing pattern) |
