# SFDMU Composite Key Optimizations (QB)

> **SFDMU v5 Required** — This project requires SFDMU v5.0.0+. The `validate_setup`
> task enforces this and will auto-update if needed. Run `cci task run validate_setup`
> to check your environment.

## SFDMU v5 Migration

SFDMU v5 introduced breaking changes that affect how composite `externalId` definitions
interact with data plans. The following adjustments were made to ensure all QB data plans
work correctly with v5 and remain **idempotent** (safe to re-run without creating duplicates).

### Key v5 behavioral changes

| v4 Behavior | v5 Change | Impact |
|-------------|-----------|--------|
| Nested relationship paths in parent `externalId` (e.g. `Pricebook2.Name`) resolved correctly when a child references that parent | v5 flattens the parent's externalId fields into the child's SOQL query, causing `Didn't understand relationship` errors when the field path is not valid on the child object | Parent externalIds with nested relationship paths must be simplified to fields valid on the parent itself, or the child's reference must not trigger flattening |
| `$$` composite key columns in CSVs used for source-to-target record matching | v5 cannot reliably match target records when `externalId` contains only relationship paths (e.g. `Parent.Name;OtherParent.Code`) | Objects with all-relationship externalIds and auto-number Names need `deleteOldData: true` or a direct-field externalId |
| `$$` notation in `externalId` definitions (e.g. `$$Field1$Field2`) recognized as composite keys | v5 does not recognize `$$` in externalId definitions; requires `;`-delimited format | All `externalId` definitions use `Field1;Field2` format |

### Changes by dataset

#### qb-pcm
- **ProductClassificationAttr**: externalId simplified to `Name` (was composite with nested relationship `ProductClassification.Code;AttributeDefinition.Code;AttributeCategory.Code`)
- **ProductRelComponentOverride**, **ProductComponentGrpOverride**: excluded (0 records)
- `$$` columns removed from `ProductClassificationAttr.csv`; child CSV references updated
- **ProductComponentGroup** (Bug 4 fix): externalId simplified to `Code` (was `Code;ParentProduct.StockKeepingUnit`). Self-referential `ParentGroup.$$Code$ParentProduct.StockKeepingUnit` replaced with `ParentGroup.Code`. Primary `$$Code$ParentProduct.StockKeepingUnit` column removed from CSV. SOQL updated to include `ParentGroup.Code` and `ParentGroup.ParentProduct.StockKeepingUnit` traversal fields for extraction.

#### qb-pricing
- **PriceAdjustmentSchedule**: externalId simplified to `Name;CurrencyIsoCode` (removed `Pricebook2.Name` — single pricebook in dataset)
- **PricebookEntry**: externalId simplified to `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` (removed `Pricebook2.Name`)
- **PricebookEntryDerivedPrice**: excluded (2 records; problematic nested references)
- CSV headers and values updated to match simplified externalIds

#### qb-billing
- **BillingTreatment**: externalId simplified to `Name` (was `Name;BillingPolicy.Name;LegalEntity.Name`)
- **BillingTreatmentItem**: externalId simplified to `Name;BillingTreatment.Name`
- **PaymentTermItem**: externalId updated from legacy `$$PaymentTerm.Name$Type` to v5 format `PaymentTerm.Name;Type`
- **GeneralLedgerAcctAsgntRule**: externalId is `Name` (names are unique in this dataset; composite key caused duplicate inserts)
- CSV references updated; `BillingPolicy.DefaultBillingTreatment` reference simplified
- **Pass 3 objectset_source fix**: BillingPolicy and BillingTreatment CSVs updated to use simplified externalId formats
- **LegalEntity**: changed to `Readonly` — qb-tax (runs first at step 13) is now the authoritative source for LegalEntity data; qb-billing only resolves IDs
- **SequencePolicy + SeqPolicySelectionCondition**: created via Connect API (`/connect/sequences/policy`) by `create_sequence_policies` task — standard REST/Bulk API silently fails for these objects (required fields `DateStampFormat` and `IncrementByNumber` are not createable via DML). Data sourced from `SequencePolicies.json` (policies with selection conditions inline); LegalEntity names are resolved to org IDs at task runtime. Not in SFDMU export.json.
- **BillingTreatments expanded**: US/CA/EU/UK × Advance/Arrears (8 treatments); EU uses EUR, UK uses GBP
- **LegalEntities expanded**: 4 entities (US, Canada, EU/France, UK/London) with corresponding LegalEntyAccountingPeriod coverage (336 rows, 2024–2030)

#### qb-tax
- **TaxTreatment**: externalId simplified to `Name` (was `Name;LegalEntity.Name;TaxPolicy.Name`)
- CSV references updated
- **LegalEntity**: now the authoritative source (was shared with qb-billing); owns all 4 entities (US, Canada, EU, UK) with full address data; qb-billing defers to qb-tax via Readonly

#### qb-clm
- **ObjectStateActionDefinition**: externalId simplified to `Name` (was `Name;ReferenceObject.Name`); duplicate `Name` column removed from CSV
- CSV references updated

#### qb-dro
- **ProductFulfillmentDecompRule**: externalId simplified to `Name`; `$$` column removed from CSV; 1 duplicate-Name pair disambiguated with SKU suffix
- **FulfillmentStepDefinition**: externalId simplified to `Name`; `$$` column removed; 2 duplicate-Name pairs disambiguated with group-name suffix
- **FulfillmentStepDependencyDef**: externalId simplified to `Name`; `$$` column removed; parent references updated to use renamed FSD Names
- **ProductFulfillmentScenario**: externalId simplified to `Name`; `$$` column removed
- **FulfillmentWorkspaceItem**: `deleteOldData: true` added (auto-number Names make direct-field matching impossible); `$$` column removed
- **ProductDecompEnrichmentRule**: excluded (0 records)
- **Single plan for scratch and TSO:** The qb-dro plan uses the placeholder `__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv` (AssignedTo.Name), `User.csv`, and `UserAndGroup.csv` (Name). The task `insert_qb_dro_data` runs with `dynamic_assigned_to_user: true`, which queries the target org for the default user's Name and replaces the placeholder before running SFDMU.

#### qb-rates
- **PriceBookRateCard**: `deleteOldData: true` added (auto-number Name, all-relationship externalId `PriceBook.Name;RateCard.Name;RateCardType`)
- **RateCardEntry**: `deleteOldData: true` added (auto-number Name, all-relationship externalId)
- **RateAdjustmentByTier**: `deleteOldData: true` added (auto-number Name, all-relationship externalId)

#### qb-tax
- **TaxPolicy**: `DefaultTaxTreatmentId` removed from Pass 2 query — SFDMU v5 cannot resolve the circular `DefaultTaxTreatment.Name` reference. The `activateTaxRecords.apex` script now sets `DefaultTaxTreatmentId` before activating.

#### qb-rating
- **ProductUsageResourcePolicy**, **ProductUsageGrant**: excluded (v5 cannot resolve their nested relationship-based externalIds)

### Idempotency

All 10 QB data tasks have been verified as idempotent with SFDMU v5 on a fresh 260 scratch org.
47/47 objects show zero record count changes on re-run.

| Strategy | Objects |
|----------|---------|
| Name-based Upsert matching | PCM, pricing, billing, tax, CLM, DRO (PFDR, FSD, FSDD, PFS, FSDG, FW, FFR, FSJR), rating, transaction processing types, guided selling |
| `deleteOldData: true` (delete + reinsert) | FulfillmentWorkspaceItem, PriceBookRateCard, RateCardEntry, RateAdjustmentByTier |

### Known limitations (v5)

- **FulfillmentStepDefinition**: 9/17 records fail to insert due to unresolved polymorphic `AssignedTo` references (`User`/`Group`) and missing `IntegrationProviderDef` records. These are data dependency issues, not SFDMU bugs.
- **FulfillmentStepDependencyDef**: 10/13 records depend on the missing FSD records above.
- **ObjectStateActionDefinition**: `legalS2` fails to insert (missing `SalesforceContractsCustomAction` reference target). 10/11 records succeed.
- **Excluded objects** (PricebookEntryDerivedPrice, ProductUsageResourcePolicy, ProductUsageGrant, ProductDecompEnrichmentRule, ProductComponentGrpOverride, ProductRelComponentOverride): require manual handling if needed.

### Bug 5 — Composite `externalId` with traversal fields fails for upsert matching (discovered 2026-04-02)

**Problem:** When `externalId` uses `;`-delimited traversal fields (e.g. `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name`), SFDMU cannot match source CSV rows to existing target records for upsert. Each run inserts new records instead of updating existing ones, even when:
- The traversal fields are included in the SOQL query
- A `$` composite key column is present in the CSV with matching values
- The target org has records with identical parent lookup values

**Discovered on:** `FulfillmentWorkspaceItem` — externalId `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name`. SFDMU inserted 7 new records on every run instead of matching the 7 existing records. Record count grew from 7 → 14 → 21 → 28 across successive runs.

**Root cause:** SFDMU's upsert matching engine cannot reliably resolve composite keys composed entirely of relationship traversal fields (`Parent.Field`) against target org data. The matching works for direct-field externalIds (e.g. `Name`, `Code`) and for composite keys mixing direct + traversal fields, but fails when all components are traversal paths.

**Prescribed pattern:** Use `deleteOldData: true` for objects whose only logical key is a composite of parent lookups and whose `Name` is an auto-number (not portable across orgs). This deletes all existing records and re-inserts from CSV, guaranteeing the target matches the source exactly. For small record sets (< 50 records), the performance cost is negligible.

**Objects using this pattern:**
- `FulfillmentWorkspaceItem` (qb-dro) — 7 records
- `PriceBookRateCard` (qb-rates) — auto-number Name, all-relationship externalId
- `RateCardEntry` (qb-rates) — auto-number Name, all-relationship externalId
- `RateAdjustmentByTier` (qb-rates) — auto-number Name, all-relationship externalId

**Rule:** If an object has (1) auto-number Name, (2) no portable natural key, and (3) externalId composed entirely of relationship traversals — use `deleteOldData: true`. Do not rely on composite `externalId` matching with traversal fields.

### Bug 4 — `$$` composite notation fails for lookup reference columns (discovered 2026-04-02)

**Problem:** `$$` composite key notation works for primary record matching (externalId ↔ `$$` CSV column) but **fails when used as a lookup reference column** in the CSV. SFDMU cannot decompose a composite `$$` value to resolve the referenced record.

**Discovered on:** `ProductComponentGroup.ParentGroup.$$Code$ParentProduct.StockKeepingUnit` — SFDMU ran 3 passes but left all `ParentGroupId` fields null. MissingParentRecordsReport showed anonymized hashes instead of resolved records.

**Fix applied:** Replaced composite `ParentGroup.$$Code$ParentProduct.StockKeepingUnit` with simple `ParentGroup.Code`, changed externalId from `Code;ParentProduct.StockKeepingUnit` to `Code` (unique in this dataset). After fix, all 7 nested parent group assignments resolved correctly.

**Impact — audit required across all plans:**
All data plan CSVs that use `$$` composite notation in *lookup reference columns* (not just the primary `$$` key column) need to be reviewed. This includes:
- Self-referential lookups (e.g., `ParentGroup.$$...`, `ParentCategory.$$...`)
- Cross-object lookups using `$$` (e.g., `ProductComponentGroup.$$Code$ParentProduct.StockKeepingUnit` referenced from `ProductRelatedComponent`)

The primary `$$` column (first column, used for record matching) is unaffected — only lookup references to other objects or self-references are broken.

**Rule:** Always use simple field references for lookup columns. If the target object's externalId is composite, simplify to a unique single field if possible.

### Validation and Fixing Tools

The project includes `scripts/validate_sfdmu_v5_datasets.py` for validating and fixing SFDMU v5 compliance issues:

**Validation Only:**

```bash
python scripts/validate_sfdmu_v5_datasets.py
python scripts/validate_sfdmu_v5_datasets.py --dataset datasets/sfdmu/qb/en-US/qb-billing
```

**Automatic Fixes:**

```bash
# Fix empty CSV headers
python scripts/validate_sfdmu_v5_datasets.py --fix-headers

# Fix missing composite key columns
python scripts/validate_sfdmu_v5_datasets.py --fix-composite-keys

# Fix all issues
python scripts/validate_sfdmu_v5_datasets.py --fix-all

# Dry-run to preview changes
python scripts/validate_sfdmu_v5_datasets.py --fix-all --dry-run
```

**Recent Fixes Applied:**

- **qb-billing/export.json**: PaymentTermItem externalId updated from legacy `$$PaymentTerm.Name$Type` to v5 format `PaymentTerm.Name;Type`
- **qb-billing/GeneralLedgerAcctAsgntRule.csv**: externalId reverted to `Name` — composite key `Name;LegalEntity.Name` broke SFDMU upsert matching and caused duplicate inserts
- **qb-billing/objectset_source/object-set-3/**: Updated Pass 3 CSVs to use simplified BillingTreatment externalId (`Name` only, not composite)
- **Empty CSV headers added**: GeneralLedgerJrnlEntryRule, ProductQualification, ProductDisqualification, ProductCategoryQualification, ProductCategoryDisqualification, CostBook, CostBookEntry

## Original composite key optimizations

### qb-pcm
- **ProductSellingModelOption** externalId includes `ProductSellingModel.SellingModelType`.
- Query includes `Product2.StockKeepingUnit`, `ProductSellingModel.Name`, and `ProductSellingModel.SellingModelType`.

### qb-pricing
- **PriceAdjustmentTier** externalId uses full composite key with `;` delimiters.
- **AttributeBasedAdjustment**, **BundleBasedAdjustment**: composite keys include all distinguishing fields.

### qb-billing
- **AccountingPeriod** externalId uses `Name;FinancialYear`.
- **LegalEntyAccountingPeriod** externalId uses `Name`.
- **PaymentTermItem** externalId uses `PaymentTerm.Name;Type` (v5 format); matching `$$PaymentTerm.Name$Type` column remains in the CSV.

### qb-rates
- **RateCard** externalId uses `Name;Type` with `$$Name$Type` in CSV.
- **RateCardEntry** externalId uses full composite key with matching `$$` column in CSV.
- **RateAdjustmentByTier** externalId includes `LowerBound;UpperBound` for uniqueness.

## Notes
- These updates focus on QB datasets referenced by `cumulusci.yml`.
- Decision tables and expression sets: SFDMU data plans for activating/deactivating them have been removed; use CCI tasks `manage_decision_tables` and `manage_expression_sets` instead.
- The separate **qb-dro_scratch** data plan has been removed; use the single **qb-dro** plan with dynamic AssignedTo user.
- If you want similar composite key hardening for non-QB datasets (q3, multicurrency, accounting, etc.), call that out and the same approach can be extended.

## Export → Re-import (roundtrip) without post-process?

**Use the processed folder for re-import.** Raw SFDMU extraction writes one CSV per object with the columns from the SOQL query (including relationship traversals like `Product2.StockKeepingUnit`, `ProductSellingModel.Name`) but **does not** write the `$$` composite key column (e.g. `$$Product2.StockKeepingUnit$ProductSellingModel.Name$ProductSellingModel.SellingModelType`). In v5, Upsert uses that `$$` column to match existing records; without it, re-import creates duplicates. The post-process script builds the `$$` columns from the extracted relationship columns and aligns headers (including fixing BOM/quoted headers from extraction). So:

- **Re-import as a new data plan:** Use the **processed** output (e.g. `extractions/qb-pcm/<timestamp>/processed/`), not the raw extraction folder. Point SFDMU at the processed directory (and its copy of `export.json`) as the plan path.
- **Standard SFDMU only (no post-process):** There is no supported way in SFDMU v5 to get a roundtrip-safe export that can be re-imported as-is when the plan uses composite `externalId`s. Options are: (1) run post-process after extract (recommended), (2) change the plan to single-field externalIds where possible (loses composite uniqueness), or (3) use `deleteOldData: true` for that object so each run deletes and reinserts (no matching, not idempotent for record identity). SFDMU does not currently add the `$$` column during export.

## Data Management tasks and flows

Extract and idempotency tasks are grouped in CumulusCI for convenience:

- **Data Management - Extract:** Tasks `extract_qb_*_data` (qb-pcm, qb-pricing, …). Each task runs the post-processor by default so output in `<timestamp>/processed/` is re-import-ready. The extract task and post-process script are **plan-agnostic**: each task uses its `pathtoexportjson` from `cumulusci.yml` (e.g. qb-rating → `datasets/sfdmu/qb/en-US/qb-rating`), and output goes to `extractions/<plan_name>/<timestamp>/`. Single-pass (flat `objects`) and multi-pass (`objectSets`) export.json formats are supported. Other data shapes (e.g. mfg) use the same pattern: place plans under `datasets/sfdmu/<shape>/<locale>/<plan-name>/` (e.g. `mfg/en-US/mfg-pcm`) and add matching anchors and tasks; the same tooling applies. List with `cci task list --group "Data Management - Extract"`.
- **Data Management - Idempotency:** Tasks `test_qb_*_idempotency` for the same plans. Each loads the plan twice and asserts no record count increase. Options: `use_extraction_roundtrip` (when true, second run uses extract → post-process → load from processed); `persist_extraction_output` (when true with roundtrip, write extraction to `extractions/<plan>/<timestamp>` instead of temp). qb-pcm idempotency uses both by default. List with `cci task list --group "Data Management - Idempotency"`.

**Flows:** `cci flow run run_qb_extracts --org <org>` runs all extract tasks; `cci flow run run_qb_idempotency_tests --org <org>` runs all idempotency tests. See main [README](../README.md) Data Management Tasks and Flows sections.
