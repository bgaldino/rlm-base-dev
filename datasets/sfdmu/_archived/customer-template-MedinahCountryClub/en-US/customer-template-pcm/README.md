# customer-template-pcm Data Plan

Template SFDMU plan for onboarding customer-specific demo products.

## Scope

This template includes both baseline and advanced customer-specific PCM records needed for realistic demos:

1. Core products and selling models:
   - `ProductSellingModel`
   - `Product2` (including `Type`, `ConfigureDuringSale`, or org-specific product type/config fields)
   - `ProductSellingModelOption` (`IsDefault=true`)
   - `ProrationPolicy` and `ProductRampSegment` (when recurring/ramp behavior is needed)
2. Catalog and categorization:
   - `ProductCatalog`
   - `ProductCategory`
   - `ProductCategoryProduct`
   - `ProductCategoryQualification` / `ProductCategoryDisqual` (optional eligibility scaffolding)
3. Attribute framework (for configurable products):
   - `AttributePicklist` / `AttributePicklistValue`
   - `UnitOfMeasureClass` / `UnitOfMeasure`
   - `AttributeDefinition`
   - `AttributeCategory` / `AttributeCategoryAttribute`
   - `ProductClassification` / `ProductClassificationAttr`
   - `ProductAttributeDefinition`
   - `ProdtAttrScope`
4. Bundle structure and component relationships:
   - `ProductRelationshipType`
   - `ProductComponentGroup`
   - `ProductRelatedComponent`
   - `ProductQualification` / `ProductDisqualification` (optional product-level eligibility scaffolding)

Pricebook rows are intentionally excluded from this plan. Use API-based creation with explicit `ProductSellingModelId`.

This template is part of a hybrid customer onboarding set:

- `customer-template-pcm` (this folder): product/catalog foundation
- `customer-template-product-images`: `Product2.DisplayUrl` updates by SKU
- `customer-template-billing`: lightweight billing foundation + product billing assignment
- `customer-template-pricing`: attribute-based pricing (`AttributeBasedAdjRule` / `AttributeAdjustmentCondition` / `AttributeBasedAdjustment`); loads after pricebook recreation in the catalog flow

## How to use

1. Copy this directory to a customer plan path, for example:
   - `datasets/sfdmu/acme/en-US/acme-pcm`
2. Populate CSV rows from your customer SKU matrix.
3. **`Product2.csv` and SFDMU:** the plan’s `Product2` SOQL includes **`BasedOnId`**, **`UnitOfMeasureId`**, and **`QuantityUnitOfMeasure`**. Omitting the relationship columns SFDMU resolves from CSV can produce **bad lookups** (see **`reports/MissingParentRecordsReport.csv`**) and **missing SKUs in the org** even when the log shows Product2 activity. **Copy the column layout from `datasets/sfdmu/qb/en-US/qb-pcm/Product2.csv`** (e.g. empty **`BasedOn.Code`**, **`CanRamp=false`**, **`IsSoldOnlyWithOtherProds=false`**, **`QuantityUnitOfMeasure` / `UnitOfMeasure.UnitCode`** such as **`EACH`** when the org has that unit). See **`docs/guides/customer-demo-onboarding.md`**.
4. When bundles/configuration are in scope, populate component groups, related components, and attribute CSVs in the same pass as products.
   - Decide `Product2.Type` before first insert:
     - parent bundle products: `Type=Bundle` (and `ConfigureDuringSale=Allowed`)
     - all other products in this template: **`Type` blank/null** (many orgs allow only `Base`/`Bundle`/`Set`; null avoids picking the wrong one)
   - for any product with `Type=Bundle`, set `ConfigureDuringSale=Allowed` on initial insert
   - avoid setting bundle children to `Base`/`Set` in orgs that enforce child-type restrictions
5. Ensure `ProductSellingModel.Name` values used in `ProductSellingModelOption` and pricebook seed input exactly match selling models available in the target org.
   - Prefer term-based recurring models (`SellingModelType=TermDefined`) so demo flows can show proration and cancel/replace/amend behavior.
   - Use evergreen recurring models only when no suitable term model exists in the target org.
   - Default `ProductSellingModelOption` rows reference **`Default Proration Policy`** by name — ensure that proration policy exists in the target org (typical after RLM base setup), or change the CSV to an org-native policy name.
6. **Unit of measure for usage demos:** add **`UnitOfMeasureClass`** / **`UnitOfMeasure`** rows for each consumption family you meter (e.g. data volume + a dedicated credit unit), with **`Type = Usage`** on the class where required so they pair with **`UsageResource.Category = Usage`**. Set **`BaseUnitOfMeasure`** and **`DefaultUnitOfMeasure`** on the class; each **`UsageResource.DefaultUnitOfMeasure`** must be a **`UnitOfMeasure`** under that class. See **`docs/references/customer-template-usage-resource.md`**. Keep **`Code` / `UnitCode` / `Name`** aligned across PCM, rating, and rates lookup CSVs.
7. Wire `cumulusci.yml` anchors/tasks for the new customer plan.
8. Run the dedicated customer onboarding flow.

## Known pitfalls (from real customer onboardings)

### AttributePicklistValue — Code must be globally unique

`AttributePicklistValue.Code` is the **externalId** used for Upsert matching across **all** picklists in the org. If two values share the same `Code` (even in different picklists), the second one overwrites the first. This causes a cascade failure: `AttributeDefinition`, `AttributeCategoryAttribute`, `ProductClassificationAttr`, and `ProductAttributeDefinition` all lose their parent references and fail to load, potentially aborting the entire PCM job.

**Example:** A "Service Tier" picklist and a "Property Size" picklist both used `Code = Enterprise`. Fix: rename the property-size entry to `Code = XLarge`.

### AttributeDefinition — DeveloperName must be org-unique

`DeveloperName` on `AttributeDefinition` is unique across the org. Packages, prior demos, or RLM base setup may already define names like `Service_Tier` or `Property_Size`. If a collision occurs, the insert fails silently within the SFDMU batch, and downstream objects referencing that definition cascade-fail.

**Fix:** prefix customer-specific developer names (e.g. `RK_Service_Tier`, `RK_Property_Size`).

### Product images — static resources must deploy first

`Product2.DisplayUrl` resolves to `/resource/<StaticResourceName>`. If set in the PCM `Product2.csv` before static resources exist in the org, the URL is broken until resources deploy. The intended flow order handles this:
1. Step 2: PCM load (leave `DisplayUrl` empty in `Product2.csv`)
2. Step 3: `deploy_customer_demo_staticresources` (deploys `.resource` + `-meta.xml` files)
3. Step 5: `customer-template-product-images` SFDMU step (sets `DisplayUrl` on each product)

### CSV fields with commas must be quoted — silent Product2 insert failures

Any CSV field that contains a comma **must** be wrapped in double-quotes (`"value, with comma"`). This is standard RFC 4180 CSV — SFDMU parses CSVs strictly and does not tolerate unquoted commas in field values.

**Failure mode:** If a `Description` (or any other text field) contains a comma and is not quoted, SFDMU misparsed the row, shifting all subsequent columns by one or more positions. The platform then rejects the INSERT because fields receive wrong values (or a required field receives an unexpected string). SFDMU logs the row as "processed" while the record is never created — the silent failure pattern.

**Confirmed impact (Chicago Bulls demo):** 5 out of 13 Product2 records failed to insert because their `Description` values contained commas without quoting. The 8 products with comma-free descriptions inserted successfully. The pattern was only visible by cross-referencing which records appeared in the org against the CSV.

**Fix:** wrap any CSV cell containing a comma in double-quotes. Run the following snippet before loading to detect mismatched column counts:

```python
import csv, os
for fname in os.listdir('.'):
    if not fname.endswith('.csv'): continue
    with open(fname, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        hcount = len(headers)
        for i, row in enumerate(reader, 2):
            if len(row) != hcount:
                print(f'{fname} row {i}: expected {hcount} cols, got {len(row)}')
```

Or run the project-level validator: `python scripts/validate_sfdmu_v5_datasets.py`.

### AttributePicklist.DataType must be Text (not Picklist)

`AttributePicklist.DataType` describes the **data type of the values stored in the picklist** (e.g. `Text`, `Number`). Setting it to `Picklist` is invalid — the platform rejects the INSERT silently (SFDMU reports "processed" but the record never appears in the org). This cascades to `AttributePicklistValue`, `AttributeDefinition`, `AttributeCategoryAttribute`, and `ProductAttributeDefinition` all failing with missing-parent lookups.

**Fix:** use `Text` for string-valued option lists (the most common case), `Number` for numeric ranges. See the qb-pcm `AttributePicklist.csv` for reference — all entries use `Text` or `Number`.

### ProductCatalog.CatalogType must be Sales

`ProductCatalog.CatalogType` is a restricted picklist. `Standard` and `Commercial` are not valid values — the platform rejects the INSERT silently (SFDMU reports success but the record never appears in the org). Use `Sales` to match the qb-pcm reference.

### AttributeDefinition.DataType must be Picklist (not Text) when referencing a picklist

When an `AttributeDefinition` references an `AttributePicklist`, the `DataType` must be `Picklist`. Setting it to `Text` causes a platform rejection: `Select a picklist only if you selected the picklist data type.` SFDMU reports the INSERT as processed but the record never appears in the org.

**Fix:** always use `DataType = Picklist` for attributes backed by an `AttributePicklist`. Use `Text` only for free-form text attributes with no picklist.

### ProductClassificationAttr.DisplayType and ProductAttributeDefinition.DisplayType — restricted picklist

The `DisplayType` field on both `ProductClassificationAttr` and `ProductAttributeDefinition` is a restricted picklist. `Picklist` is **not** a valid value — the platform rejects the INSERT. SFDMU returns 0 SOURCE records for the entire object in that objectSet pass (it pre-validates values before batching), causing **silent wholesale skip** with no MissingParentRecordsReport entry.

Valid values: `RadioButton` (most common for picklist-backed attributes), or leave blank. See existing QB PCA rows for reference.

### ProductRelatedComponent — no selling models for configurable bundles

When the parent product has `ConfigureDuringSale = Allowed` (i.e. it is a configurable bundle), Salesforce rejects any `ProductRelatedComponent` row that specifies `ChildSellingModelId` or `ParentSellingModelId`. The error message is:

> `The parent selling model is unsupported for configurable product bundles. Delete the parent selling model and try again.`

**Fix:** leave `ChildSellingModel.$$Name$SellingModelType` and `ParentSellingModel.$$Name$SellingModelType` blank in the PRC CSV for configurable bundle components (follow the QB `ProductRelatedComponent.csv` pattern — all selling model columns are empty).

### UnitOfMeasure updates on re-run are benign

When UOMs like `USD` or `EACH` already exist in the org (from `qb-pcm` or base setup), the Upsert Update phase may log errors because fields like `ConversionFactor` or `Type` are not updatable after creation. These errors are **benign** — the existing UOM is correct. Only truly new UOMs (e.g. a customer-specific `EVENT` unit) need the Insert to succeed.

### CategoryCode in customer-pricebook-entries.csv

`customer_demo_verify_catalog` uses the `CategoryCode` column in `scripts/customer-demo/customer-pricebook-entries.csv` to verify that `ProductCategoryProduct` records exist for each SKU. Leaving `CategoryCode` empty causes the verify step to report **"ProductCategoryProduct missing for category"** on every SKU, even when all catalog objects loaded correctly. Always populate `CategoryCode` with the matching `ProductCategory.Code`.

### Rating grant policies — reference existing org records, don't create new ones

`UsageGrantRenewalPolicy`, `UsageGrantRolloverPolicy`, and `UsageOveragePolicy` are setup-like objects that SFDMU silently fails to create — the REST API Insert logs "processed 1" but the records never persist in the org. Downstream `ProductUsageGrant` and `ProductUsageResourcePolicy` then fail parent lookups. **Always reference policies that already exist in the org** (e.g. `SF-DEMO-USG-RENEW`, `SF-DEMO-USG-ROLL`, `Default Usage Overage Policy`). Query the org before populating the rating CSVs. See `customer-template-rating/README.md` for full details.

### ProductUsageGrant — always verify after load

SFDMU's `Insert` for `ProductUsageGrant` has a confirmed silent-failure bug: it reports success but the record never appears in the org. After every rating load, verify PUG existence via SOQL. If missing, insert via Apex. See `docs/guides/customer-demo-onboarding.md` → Troubleshooting.

---

## Attribute framework — end-to-end pitfalls (from Chicago Bulls onboarding)

Getting attributes and configurable products to work requires a specific chain of objects that all have non-obvious constraints.

### ProductAttributeDefinition.DisplayType — restricted picklist

`ProductAttributeDefinition.DisplayType` is a restricted picklist. Common invalid values:

| Value tried | Correct value |
|---|---|
| `Dropdown` | `ComboBox` |
| `Select` | `ComboBox` |
| `List` | `ComboBox` |

Valid values: `ComboBox`, `RadioButton`, `Text`, `CheckBox`, `Toggle`, `Number`, `Date`, `Datetime`, `Slider`. Leave blank for read-only informational attributes.

SFDMU logs the PAD rows as "processed" while Salesforce silently rejects the INSERT. No entry appears in `MissingParentRecordsReport.csv` because the failure is a field-level validation, not a missing parent.

### AttributeDefinition.DefaultValue must match AttributePicklistValue.Value (not Name)

For `DataType = Picklist` attributes, `AttributeDefinition.DefaultValue` must equal the **`Value`** column of an existing `AttributePicklistValue`, not the `Name` or `DisplayValue`.

**Example failure:**
- `AttributePicklistValue`: `Name = "2 Seats"`, `Value = "2"`, `IsDefault = true`
- `AttributeDefinition.DefaultValue = "2 Seats"` → INSERT fails with `INVALID_INPUT: Provided default value for picklist data type is either invalid or an inactive attribute picklist value.`
- **Fix:** `AttributeDefinition.DefaultValue = "2"` (matching `AttributePicklistValue.Value`)

The same applies to `ProductAttributeDefinition.DefaultValue` for picker attributes — use the `Value` field, not `Name`.

### ProductAttributeDefinition requires ProductClassificationAttributeId (always)

`ProductClassificationAttributeId` is a **required** field on `ProductAttributeDefinition`. It must point to a `ProductClassificationAttr` record that links the `AttributeDefinition` + `AttributeCategory` to a `ProductClassification`.

The full chain that must exist before PAD can be loaded:
1. `AttributePicklist` → `AttributePicklistValue` (for Picklist-typed attributes)
2. `AttributeDefinition` (with `PicklistId` pointing to the picklist above)
3. `AttributeCategory`
4. `AttributeCategoryAttribute` (links AttributeDefinition + AttributeCategory)
5. **`ProductClassification`** (logical grouping of products with shared attributes)
6. **`ProductClassificationAttr`** (defines an attribute within a classification — links AttributeDefinition + AttributeCategory + ProductClassification)
7. **`Product2.BasedOnId`** must point to the **same `ProductClassification`** that the `ProductClassificationAttr` belongs to (enforced by platform validation — see next pitfall)
8. `ProductAttributeDefinition` (with `ProductClassificationAttributeId` = the matching PCA)

Ensure `ProductClassification.csv` and `ProductClassificationAttr.csv` are populated **before** PAD rows are loaded. Both CSVs are empty by default in the template.

### Product2.BasedOnId must match ProductClassificationAttr.ProductClassificationId

When creating a `ProductAttributeDefinition`, Salesforce validates that:

> **"The BasedOnId of the Product must match the ProductClassificationId of the Product Classification Attribute."**

This means `Product2.BasedOnId` must reference the same `ProductClassification` that the PCA belongs to. Set `BasedOn.Code` in `Product2.csv` to the `ProductClassification.Code` for every product that will have attributes. Leave `BasedOn.Code` empty for products with no attributes.

**Design pattern for this template:**
- `BULLS-PC-TICKET` (Bulls Ticket Plan) → season ticket products (BULLS-ST-FULL, BULLS-ST-20, BULLS-ST-10)
- `BULLS-PC-SUITE` (Bulls Suite and Bundle) → suite + bundle products (BULLS-SUITE-LOWER, BULLS-SUITE-CLUB, BULLS-CORP-PKG)
- No classification → products with no configurable attributes (experience add-ons, digital membership, camps)

### ProductRelatedComponent — MinQuantity/MaxQuantity require IsQuantityEditable=true

When `IsQuantityEditable = false` (fixed quantity), Salesforce rejects any non-null `MinQuantity` or `MaxQuantity` with:

> **"Select 'Allow quantity changes' and then edit the minimum quantity."**

SFDMU silently fails the row. Leave `MinQuantity` and `MaxQuantity` blank in the CSV when `IsQuantityEditable = false`.

### ConfigureDuringSale — only set Allowed on products with actual PAD rows

Setting `Product2.ConfigureDuringSale = Allowed` on products with no `ProductAttributeDefinition` records causes an empty/confusing configuration panel during demo flows. Only set `Allowed` on:
- Products with at least one PAD row (configurable or read-only attributes)
- `Type = Bundle` products (always need `Allowed` for the component assembly panel)

Leave `ConfigureDuringSale` blank for products with no attributes.
