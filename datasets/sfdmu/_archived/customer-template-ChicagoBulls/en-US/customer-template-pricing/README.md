# customer-template-pricing

Attribute-based pricing plan for the Chicago Bulls customer demo. Implements seat-section-driven **Override** price adjustments on season ticket products using the three-object RLM pricing chain:

```
AttributeBasedAdjRule → AttributeAdjustmentCondition → AttributeBasedAdjustment
```

---

## What This Plan Does

Seat Section (`BULLS-SEAT-SECTION`) is a price-impacting attribute on the three season ticket SKUs. When a buyer configures their seat section during quoting, the platform evaluates all `AttributeBasedAdjRule` records associated with the product and its `PriceAdjustmentSchedule`, finds the matching condition, and applies the corresponding `AttributeBasedAdjustment` price override.

### Pricing Table

| SKU | Seat Section | Override Price |
|---|---|---|
| `BULLS-ST-FULL` | Upper Bowl | $3,200 |
| `BULLS-ST-FULL` | Lower Bowl | $5,000 |
| `BULLS-ST-FULL` | Courtside | $12,000 |
| `BULLS-ST-20` | Upper Bowl | $1,600 |
| `BULLS-ST-20` | Lower Bowl | $2,500 |
| `BULLS-ST-20` | Courtside | $6,000 |
| `BULLS-ST-10` | Upper Bowl | $800 |
| `BULLS-ST-10` | Lower Bowl | $1,200 |
| `BULLS-ST-10` | Courtside | $2,800 |

Lower Bowl is the list price (matches Standard PricebookEntry). Upper Bowl discounts it; Courtside upgrades it.

---

## Objects Loaded

| Object | Operation | Count | ExternalId |
|---|---|---|---|
| `Product2` | Readonly | header-only | `StockKeepingUnit` |
| `AttributeDefinition` | Readonly | header-only | `Code` |
| `ProductSellingModel` | Readonly | header-only | `Name;SellingModelType` |
| `PriceAdjustmentSchedule` | Readonly | header-only | `Name;CurrencyIsoCode` |
| `AttributeBasedAdjRule` | Upsert | 9 | `Name` |
| `AttributeAdjustmentCondition` | Insert | 9 | `AttributeBasedAdjRule.Name;AttributeDefinition.Code;Product.StockKeepingUnit` |
| `AttributeBasedAdjustment` | Insert | 9 | `AttributeBasedAdjRule.Name;PriceAdjustmentSchedule.Name;Product.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` |

**Readonly CSVs are header-only**: SFDMU queries the TARGET org at load time to build FK context. The CSV file only needs to exist; content is populated during extraction.

---

## CumulusCI Tasks

```bash
# Load attribute-based pricing (steps 8–9 of prepare_customer_demo_catalog)
cci task run delete_customer_demo_pricing_data --org <alias>
cci task run insert_customer_demo_pricing_data --org <alias>

# Re-run just the pricing load (standalone, after PCM + pricebook are loaded)
cci task run delete_customer_demo_pricing_data --org <alias>
cci task run insert_customer_demo_pricing_data --org <alias>
cci task run customer_demo_verify_catalog --org <alias>
```

---

## Order of Operations

**Within `prepare_customer_demo_catalog`:**

```
Step 1:  customer_demo_purge_records             (clear QLIURG/policy blocks)
Step 2:  insert_customer_demo_pcm_data           (Product2, attributes, classifications)
Step 3:  deploy_customer_demo_staticresources    (logo static resource)
Step 4:  deploy_customer_demo_branding           (conditional: theme)
Step 5:  insert_customer_demo_product_images_data
Step 6:  insert_customer_demo_billing_data
Step 7:  customer_demo_recreate_pricebook_via_api  (Standard PBE with PSM)
Step 8:  delete_customer_demo_pricing_data ◄── NEW
Step 9:  insert_customer_demo_pricing_data ◄── NEW
Step 10: customer_demo_verify_catalog
```

**Why pricing runs after pricebook (step 7):** `AttributeBasedAdjustment` doesn't have an FK to `PricebookEntry`, so technically pricing can load any time after Product2 and AttributeDefinition exist. However, placing it after pricebook recreation (step 7) keeps the logical flow: "list prices first, then adjustments." The platform resolves ABA at quote time by joining through PriceAdjustmentSchedule, not via a stored FK.

**Why delete runs before insert (step 8):** `AttributeAdjustmentCondition` and `AttributeBasedAdjustment` use `operation: Insert` (not Upsert) because their externalIds are all-relationship-traversal — SFDMU Bug 3 would cause Upsert to always insert and never match. Without a pre-delete, re-running the plan creates duplicates on every run.

**Why delete is scoped (Apex, not DeleteSFDMUData):** `DeleteSFDMUData` deletes **all** records of Insert-operation object types. If QB pricing data coexists in the same org, this would wipe those records too. The Apex script scopes deletion to `WHERE Name LIKE 'BULLS-%'`.

---

## Lessons Learned (Debugging Notes)

These pitfalls were discovered during development and are documented here so future implementors can avoid them.

### 1. Two-ObjectSet Architecture is Required for Fresh Parent Inserts

**Problem:** When `AttributeBasedAdjRule` is Upserted in the same `objectSet` as `AttributeAdjustmentCondition` and `AttributeBasedAdjustment` Inserts, the child inserts fail silently.

**Root cause:** SFDMU builds its parent FK lookup map during **STAGE 2** (before the UPDATE phase). If ABR records don't exist yet at STAGE 2 query time (because they were deleted before the run), the FK map for ABR is empty. When SFDMU later tries to insert ABA (which references ABR), it crashes with `COMMAND_UNEXPECTED_ERROR` because it can't resolve `AttributeBasedAdjRuleId`.

**Fix:** Use **two `objectSets`**:
- Set 1: ABR Upsert only
- Set 2: Readonly parents (including ABR) + AAC Insert + ABA Insert

In Set 2, ABR is listed as `Readonly`. SFDMU queries the org for Readonly objects at STAGE 2 — which runs **after Set 1's inserts complete**. So Set 2's FK map for ABR contains the freshly-inserted ABR records. AAC and ABA inserts then resolve the FK correctly.

**Key insight:** QB's pricing plan works with a single objectSet because ABR records already exist when the plan runs (QB's `delete_quantumbit_pricing_data` uses `DeleteSFDMUData` which skips Upsert objects — so ABR is never deleted). Our demo purge script deletes ABR, making the two-objectSet approach necessary.

### 2. SELECT Queries Must Use Direct ID Fields, Not Relationship-Traversal

**Problem:** SFDMU crashes with `COMMAND_UNEXPECTED_ERROR` during AAC Insert when the SELECT query uses relationship-traversal field references like `AttributeBasedAdjRule.Name`, `AttributeDefinition.Code`, `Product.StockKeepingUnit`.

SFDMU logs the warning: `Referenced field removed from the script query. It will be added automatically if required.`

When SFDMU "removes" these traversal fields, it appears to also remove them from the FK resolution context for the INSERT phase, causing a null-pointer crash in SFDMU's internal processing.

**Fix:** Use direct ID fields in the SELECT query (matching QB's pattern):
```sql
-- CORRECT (direct ID fields)
SELECT AttributeBasedAdjRuleId, AttributeDefinitionId, BooleanValue, DateValue,
       DateTimeValue, DoubleValue, IntegerValue, Operator, ProductId, StringValue
FROM AttributeAdjustmentCondition

-- WRONG (traversal fields removed by SFDMU, causing crash)
SELECT AttributeBasedAdjRule.Name, AttributeDefinition.Code, BooleanValue, ...
FROM AttributeAdjustmentCondition
```

SFDMU automatically adds the traversal columns (`AttributeBasedAdjRule.Name`, `AttributeDefinition.Code`, `Product.StockKeepingUnit`) alongside the ID fields in the FK resolution context when direct ID fields are used in the query. The CSV column headers using traversal names still work correctly — SFDMU maps them.

**Same applies to `AttributeBasedAdjustment`:** Use `AttributeBasedAdjRuleId`, `PriceAdjustmentScheduleId`, `ProductId`, `ProductSellingModelId` in the SELECT, not traversal fields.

### 3. AAC CSV Column Count — Empty Fields Require Explicit Commas

**Problem:** The `AttributeAdjustmentCondition` CSV has 11 columns but several value-type columns (BooleanValue, DateTimeValue, DateValue, DoubleValue, IntegerValue) are always empty for string-value conditions. Forgetting to include explicit empty commas for ALL 5 empty columns causes column misalignment.

**Example:** `Operator` value (`equals`) appears in `IntegerValue` column when one comma is missing.

**Debug method:** Use Python's `csv.DictReader` to validate column mapping:
```python
import csv
with open('AttributeAdjustmentCondition.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(rows[0])  # Check Operator, Product.StockKeepingUnit, StringValue
```

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
11. StringValue           (the AttributePicklistValue.Value — e.g. "Upper Bowl")
```

For a string-value condition: `RULE;ATTR;SKU,RULE,ATTR,,,,,,equals,SKU,StringValue`
There are **6 commas** between col 3 (AttributeDefinition.Code) and col 9 (Operator), creating 5 empty fields (cols 4-8).

### 4. AttributeAdjustmentCondition Cannot Be Deleted Directly via DML

**Problem:** `Database.delete` on `List<AttributeAdjustmentCondition>` fails with: `DML operation Delete not allowed on List<AttributeAdjustmentCondition>`.

**Root cause:** `AttributeAdjustmentCondition` is a master-detail child of `AttributeBasedAdjRule`. Cascade-delete is the only supported deletion path.

**Fix:** Delete `AttributeBasedAdjRule` (which cascades AAC automatically). Delete `AttributeBasedAdjustment` first (explicit DML — ABA is NOT cascade from ABR, must be deleted before ABR):
```apex
// ABA first (explicit, NOT cascade from ABR)
delete [SELECT Id FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRuleId IN :ruleIds];
// ABR deletes cascade AAC automatically
delete [SELECT Id FROM AttributeBasedAdjRule WHERE Name LIKE 'BULLS-%'];
```

### 5. AttributePicklistValue.Value Must Match Exactly in StringValue

The `StringValue` in `AttributeAdjustmentCondition` must match the **`Value`** field of `AttributePicklistValue` exactly (case-sensitive). The `Value` field is distinct from `Name`. Query the org to confirm values before populating the CSV:

```bash
sf data query -q "SELECT Code, Value, Name FROM AttributePicklistValue WHERE Code LIKE 'BULLS-SEC%'" \
  --target-org <username>
```

Seat section values in this org: `Upper Bowl`, `Lower Bowl`, `Courtside` (from `BULLS-SEC-UPPER`, `BULLS-SEC-LOWER`, `BULLS-SEC-COURT`).

### 6. Read-Only ABA Fields — Leave Blank in CSV

`AttributeBasedAdjustment` has several platform-computed read-only fields. Including them as blank in the CSV is safe — SFDMU omits blank values from the INSERT payload:

| Field | Source | Write on INSERT |
|---|---|---|
| `AttributeAdjConditionsHash` | Platform computes from conditions | ❌ read-only |
| `AttributeCount` | Platform counts conditions | ❌ read-only |
| `PricingTerm` | Derived from ProductSellingModel | ❌ read-only |
| `PricingTermUnit` | Derived from ProductSellingModel | ❌ read-only |
| `ScheduleType` | Derived from PriceAdjustmentSchedule | ❌ read-only |
| `SellingModelType` | Derived from ProductSellingModel | ❌ read-only |

These columns must still appear in the CSV header (SFDMU uses them in the extraction SELECT), but their values should be blank for fresh inserts.

---

## Verification

The `customer_demo_verify_catalog` task checks attribute-based pricing when `ExpectedPricingRules` is non-empty in `customer-pricebook-entries.csv`. For season ticket SKUs, the expected count is `3` (one ABA record per seat section value):

```bash
cci task run customer_demo_verify_catalog --org <alias>
```

Verify manually:
```bash
sf data query -q "SELECT AttributeBasedAdjRule.Name, AdjustmentType, AdjustmentValue, Product.StockKeepingUnit, ProductSellingModel.Name FROM AttributeBasedAdjustment WHERE AttributeBasedAdjRule.Name LIKE 'BULLS-%' ORDER BY AttributeBasedAdjRule.Name" --target-org <username>

sf data query -q "SELECT AttributeBasedAdjRule.Name, Operator, StringValue, Product.StockKeepingUnit FROM AttributeAdjustmentCondition WHERE AttributeBasedAdjRule.Name LIKE 'BULLS-%'" --target-org <username>
```

Expected: 9 ABR + 9 AAC + 9 ABA records.

---

## Extending to Other Products

To add attribute-based pricing for additional products (e.g., suite capacity tiers):

1. **Add rows to `AttributeBasedAdjRule.csv`** — new rule names like `BULLS-SUITE-LOWER-CAP-S`, `BULLS-SUITE-LOWER-CAP-M`, etc.
2. **Add rows to `AttributeAdjustmentCondition.csv`** — one row per rule, matching the `AttributePicklistValue.Value` of the controlling attribute.
3. **Add rows to `AttributeBasedAdjustment.csv`** — one row per rule with the Override `AdjustmentValue`.
4. **Update `customer-pricebook-entries.csv`** — set `ExpectedPricingRules` for the new SKU.
5. **Re-run the delete + insert cycle** and verify.

Suite products use `AdjustmentType = Override` and a `One-Time` ProductSellingModel, so update the `ProductSellingModel.$$Name$SellingModelType` column in ABA accordingly.

---

## Related Files

| File | Purpose |
|---|---|
| `scripts/apex/deleteCustomerDemoPricingData.apex` | Scoped delete (BULLS-* rules only) |
| `scripts/customer-demo/customer-pricebook-entries.csv` | `ExpectedPricingRules` column drives ABA count verification |
| `tasks/rlm_customer_demo.py` | `VerifyCustomerDemoCatalog._run_task()` — `ExpectedPricingRules` check |
| `datasets/sfdmu/customer-template/en-US/customer-template-pcm/ProductAttributeDefinition.csv` | `IsPriceImpacting=true` on `BULLS-SEAT-SECTION` for the three ticket SKUs |
| `datasets/sfdmu/qb/en-US/qb-pricing/` | Reference plan (QB attribute-based pricing pattern) |
