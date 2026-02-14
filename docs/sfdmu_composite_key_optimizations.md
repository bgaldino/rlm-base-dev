# SFDMU Composite Key Optimizations (QB)

## Changes applied

### `datasets/sfdmu/qb/en-US/qb-pcm/export.json`
- **ProductSellingModelOption** externalId includes `ProductSellingModel.SellingModelType`.
- Query includes `Product2.StockKeepingUnit`, `ProductSellingModel.Name`, and `ProductSellingModel.SellingModelType`.
- Reason: avoids collisions when the same selling model name exists across types.

### `datasets/sfdmu/qb/en-US/qb-pricing/export.json`
- **PriceAdjustmentTier** externalId uses full composite key with `;` delimiters.
- **PricebookEntry** externalId uses `Pricebook2.Name;Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` with `$$Pricebook2.Name$Product2.StockKeepingUnit$ProductSellingModel.Name$CurrencyIsoCode` in CSV.
- **PricebookEntryDerivedPrice** externalId includes the PricebookEntry key parts plus `Product.StockKeepingUnit;ContributingProduct.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode`, with matching `$$` column in CSV.
- Reason: aligns keys with org uniqueness and prevents false inserts.

### `datasets/sfdmu/qb/en-US/qb-billing/export.json`
- **AccountingPeriod** externalId uses `Name;FinancialYear`.
- **LegalEntyAccountingPeriod** externalId uses `Name`.
- **PaymentTermItem** externalId uses `$$PaymentTerm.Name$Type` with matching CSV column.
- **BillingTreatmentItem** externalId uses `$$Name$BillingTreatment.Name` with `BillingTreatment.Name` in CSV.
- Reason: stable keys for updates without duplicate inserts.

### `datasets/sfdmu/qb/en-US/qb-tax/export.json`
- **TaxTreatment** externalId uses `Name;LegalEntity.Name;TaxPolicy.Name`, with matching query fields.
- **TaxEngine** externalId uses `TaxEngineName`.
- Reason: scope tax treatments by legal entity/policy and match org uniqueness.

### `datasets/sfdmu/qb/en-US/qb-rating/export.json`
- **ProductUsageResource** externalId uses `Product.StockKeepingUnit;UsageResource.Code` with `$$Product.StockKeepingUnit$UsageResource.Code` in CSV.
- Reason: stable composite key for usage resource linkage.

### `datasets/sfdmu/qb/en-US/qb-rates/export.json`
- **RateCard** externalId uses `Name;Type` with `$$Name$Type` in CSV.
- **PriceBookRateCard** uses `RateCard.$$Name$Type` in CSV to resolve lookups.
- **RateCardEntry** externalId uses `Product.StockKeepingUnit;RateCard.Name;UsageResource.Code;RateUnitOfMeasure.UnitCode` with matching `$$` column in CSV.
- **RateAdjustmentByTier** externalId includes `LowerBound;UpperBound` for uniqueness.
- Reason: distinguish rate card entries and tiers by usage resource, UoM, and bounds.

### `datasets/sfdmu/qb/en-US/qb-dro/` (single DRO plan)
- **Single plan for scratch and TSO:** The qb-dro plan uses the placeholder `__DRO_ASSIGNED_TO_USER__` in `FulfillmentStepDefinition.csv` (AssignedTo.Name) and `UserAndGroup.csv` (Name). The tasks `insert_qb_dro_data_scratch` and `insert_qb_dro_data_prod` run with `dynamic_assigned_to_user: true`, which queries the target org for the default user's Name and replaces the placeholder before running SFDMU. This replaces the former separate `qb-dro_scratch` plan (removed).

## Notes
- These updates focus on QB datasets referenced by `cumulusci.yml`.
- Decision tables and expression sets: SFDMU data plans for activating/deactivating them have been removed; use CCI tasks `manage_decision_tables` and `manage_expression_sets` instead.
- The separate **qb-dro_scratch** data plan has been removed; use the single **qb-dro** plan with dynamic AssignedTo user (see above).
- If you want similar composite key hardening for non-QB datasets (q3, multicurrency, accounting, etc.), call that out and I’ll extend the same approach.
