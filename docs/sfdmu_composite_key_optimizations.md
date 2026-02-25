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

#### qb-pricing
- **PriceAdjustmentSchedule**: externalId simplified to `Name;CurrencyIsoCode` (removed `Pricebook2.Name` — single pricebook in dataset)
- **PricebookEntry**: externalId simplified to `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` (removed `Pricebook2.Name`)
- **PricebookEntryDerivedPrice**: excluded (2 records; problematic nested references)
- CSV headers and values updated to match simplified externalIds

#### qb-billing
- **BillingTreatment**: externalId simplified to `Name` (was `Name;BillingPolicy.Name;LegalEntity.Name`)
- **BillingTreatmentItem**: externalId simplified to `Name;BillingTreatment.Name`
- CSV references updated; `BillingPolicy.DefaultBillingTreatment` reference simplified

#### qb-tax
- **TaxTreatment**: externalId simplified to `Name` (was `Name;LegalEntity.Name;TaxPolicy.Name`)
- CSV references updated

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
- **Single plan for scratch and TSO:** The qb-dro plan uses the placeholder `__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv` (AssignedTo.Name) and `UserAndGroup.csv` (Name). The tasks `insert_qb_dro_data_scratch` and `insert_qb_dro_data_prod` run with `dynamic_assigned_to_user: true`, which queries the target org for the default user's Name and replaces the placeholder before running SFDMU.

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
- **PaymentTermItem** externalId uses `$$PaymentTerm.Name$Type` with matching CSV column.

### qb-rates
- **RateCard** externalId uses `Name;Type` with `$$Name$Type` in CSV.
- **RateCardEntry** externalId uses full composite key with matching `$$` column in CSV.
- **RateAdjustmentByTier** externalId includes `LowerBound;UpperBound` for uniqueness.

## Notes
- These updates focus on QB datasets referenced by `cumulusci.yml`.
- Decision tables and expression sets: SFDMU data plans for activating/deactivating them have been removed; use CCI tasks `manage_decision_tables` and `manage_expression_sets` instead.
- The separate **qb-dro_scratch** data plan has been removed; use the single **qb-dro** plan with dynamic AssignedTo user.
- If you want similar composite key hardening for non-QB datasets (q3, multicurrency, accounting, etc.), call that out and the same approach can be extended.
