# Object-to-Plan Mapping

Which SObject lives in which data plan, its externalId, operation, and upstream dependencies.

## qb-pcm (Product Catalog Management)

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| AttributePicklist | `Name` | Upsert | |
| AttributePicklistValue | `Code` | Upsert | |
| UnitOfMeasureClass | `Code` | Upsert | |
| UnitOfMeasure | `UnitCode` | Upsert | |
| AttributeDefinition | `Code` | Upsert | |
| AttributeCategory | `Code` | Upsert | |
| AttributeCategoryAttribute | `AttributeCategory.Code;AttributeDefinition.Code` | Upsert | Junction |
| ProductClassification | `Code` | Upsert | Self-ref hierarchy |
| ProductClassificationAttr | `Name` | Upsert | |
| Product2 | `StockKeepingUnit` | Upsert | Central hub |
| ProductAttributeDefinition | `AttributeDefinition.Code;Product2.StockKeepingUnit` | Upsert | |
| ProductSellingModel | `Name;SellingModelType` | Upsert | |
| ProrationPolicy | `Name` | Upsert | |
| ProductSellingModelOption | `Product2.StockKeepingUnit;ProductSellingModel.Name;ProductSellingModel.SellingModelType` | Upsert | |
| ProductRampSegment | `Product.StockKeepingUnit;ProductSellingModel.SellingModelType;SegmentType` | Upsert | |
| ProductRelationshipType | `Name` | Upsert | |
| ProductComponentGroup | `Code` | Upsert | Self-ref hierarchy |
| ProductRelatedComponent | 5-field composite | Upsert | Bundle components |
| ProductCatalog | `Code` | Upsert | |
| ProductCategory | `Code` | Upsert | Self-ref hierarchy |
| ProductCategoryProduct | `ProductCategory.Code;Product.StockKeepingUnit` | Upsert | Junction |

## qb-pricing

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| CurrencyType | `IsoCode` | Upsert | |
| ProrationPolicy | `Name` | Update | Set fields only |
| ProductSellingModel | `Name;SellingModelType` | Readonly | From qb-pcm |
| AttributeDefinition | `Code` | Readonly | From qb-pcm |
| Product2 | `StockKeepingUnit` | Readonly | From qb-pcm |
| CostBook | `Name;IsDefault` | Upsert | |
| Pricebook2 | `Name;IsStandard` | Upsert | |
| PriceAdjustmentTier | 9-field composite | **Insert** | Bug 3: relationship traversal externalId |
| PriceAdjustmentSchedule | `Name;CurrencyIsoCode` | Update | |
| AttributeBasedAdjRule | `Name` | Upsert | |
| AttributeAdjustmentCondition | 3-field composite | **Insert** | Bug 3 |
| AttributeBasedAdjustment | 5-field composite | **Insert** | Bug 3 |
| BundleBasedAdjustment | 8-field composite | **Insert** | Bug 3 |
| PricebookEntry | `Product2.StockKeepingUnit;ProductSellingModel.Name;CurrencyIsoCode` | **Insert** | Bug 3 |
| PricebookEntryDerivedPrice | 8-field composite | **Insert** | Bug 2+3 |
| CostBookEntry | 3-field composite | **Insert** | Excluded (0 records) |

## qb-billing (3 passes)

| SObject | externalId | Operation | Pass | Notes |
|---------|-----------|-----------|------|-------|
| AccountingPeriod | `Name;FinancialYear` | Upsert | 1 | |
| LegalEntity | `Name` | Upsert | 1 | Shared with qb-tax |
| LegalEntyAccountingPeriod | `Name` | Upsert | 1 | |
| PaymentTerm | `Name` | Upsert | 1 | |
| PaymentTermItem | `PaymentTerm.Name;Type` | Upsert | 1 | |
| BillingPolicy | `Name` | Upsert | 1 | |
| BillingTreatment | `Name` | Upsert | 1 | |
| BillingTreatmentItem | `Name;BillingTreatment.Name` | Upsert | 1 | |
| Product2 | `StockKeepingUnit` | Update | 1 | Sets BillingPolicyId |
| GeneralLedgerAccount | `Name` | Upsert | 1 | |
| GeneralLedgerAcctAsgntRule | `Name;LegalEntity.Name` | Upsert | 1 | |
| BillingTreatmentItem | — | Update | 2 | Activate |
| BillingTreatment | — | Update | 3 | Activate |
| BillingPolicy | — | Update | 3 | Set DefaultBillingTreatmentId |

## qb-tax (2 passes)

| SObject | externalId | Operation | Pass | Notes |
|---------|-----------|-----------|------|-------|
| LegalEntity | `Name` | Upsert | 1 | Shared with qb-billing |
| TaxEngineProvider | `DeveloperName` | Upsert | 1 | |
| TaxEngine | `TaxEngineName` | Upsert | 1 | |
| TaxTreatment | `Name` | Upsert | 1 | |
| TaxPolicy | `Name` | Upsert | 1 | |
| Product2 | `StockKeepingUnit` | Update | 1 | Sets TaxPolicyId |
| TaxTreatment | — | Update | 2 | Activate |
| TaxPolicy | — | Update | 2 | Activate + set defaults |

## qb-rating (2 passes)

| SObject | externalId | Operation | Pass | Notes |
|---------|-----------|-----------|------|-------|
| UnitOfMeasure | `UnitCode` | Upsert | 1 | |
| UnitOfMeasureClass | `Code` | Upsert | 1 | |
| UsageResourceBillingPolicy | `Code` | Upsert | 1 | |
| UsageResource | `Code` | Upsert | 1 | Self-ref via TokenResourceId |
| Product2 | `StockKeepingUnit` | Update | 1 | Sets UsageModelType |
| UsageGrantRenewalPolicy | `Code` | Upsert | 1 | |
| UsageGrantRolloverPolicy | `Code` | Upsert | 1 | |
| UsageOveragePolicy | `Name` | Upsert | 1 | |
| UsageCommitmentPolicy | `Name` | Upsert | 1 | |
| ProductUsageResource (PUR) | `Product.StockKeepingUnit;UsageResource.Code` | **Insert** + deleteOldData | 1 | Bug 3 |
| UsagePrdGrantBindingPolicy | `Name;Product2.StockKeepingUnit` | Upsert | 1 | |
| RatingFrequencyPolicy | `RatingPeriod` | Upsert | 1 | |
| ProductUsageResourcePolicy (PURP) | `ProductUsageResourceId` | **Insert** + deleteOldData | 1 | Bug 3 |
| ProductUsageGrant (PUG) | 3-field composite | **Insert** + deleteOldData | 1 | Bug 3 |
| UnitOfMeasureClass | — | Update | 2 | Activate |
| UsageResource | — | Update | 2 | Activate |

## qb-rates

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| Product2 | `StockKeepingUnit` | Update | Sets UsageModelType |
| RateCard | `Name;Type` | Upsert | |
| PriceBookRateCard | `PriceBook.Name;RateCard.Name;RateCardType` | Upsert + deleteOldData | Auto-number Name |
| RateCardEntry | 4-field composite | **Insert** + deleteOldData | Bug 3 |
| RateAdjustmentByTier | 6-field composite | **Insert** + deleteOldData | Bug 3 |

## qb-dro

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| Product2 | `StockKeepingUnit` | Update | Sets DRO fields |
| ProductFulfillmentDecompRule | `Name` | Upsert | |
| FulfillmentStepDefinitionGroup | `Name` | Upsert | |
| User | `Name` | ReadOnly | Assignee resolution |
| Group | `Name` | ReadOnly | Queue resolution |
| IntegrationProviderDef | `DeveloperName` | ReadOnly | |
| FulfillmentStepDefinition | `Name` | Upsert | Polymorphic AssignedToId |
| FulfillmentStepDependencyDef | `Name` | Upsert | |
| ProductFulfillmentScenario | `Name` | Upsert | |
| FulfillmentWorkspace | `Name` | Upsert | |
| FulfillmentWorkspaceItem | `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name` | Upsert + deleteOldData | Auto-number Name |
| FulfillmentFalloutRule | `Name` | Upsert | |
| FulfillmentStepJeopardyRule | `Name` | Upsert | |

## qb-clm

| SObject | externalId | Operation |
|---------|-----------|-----------|
| ClauseCatgConfiguration | `DeveloperName` | Upsert |
| DocumentClauseSet | `Name;CategoryReference.DeveloperName` | Upsert |
| ObjectStateDefinition | `Name` | Upsert |
| ObjectStateActionDefinition | `Name` | Upsert |
| ObjectStateValue | `Name` | Upsert |
| ObjectStateTransition | `Name` | Upsert |
| ObjectStateTransitionAction | `Name` | Upsert |

## qb-guidedselling

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| AssessmentQuestionConfig | `DeveloperName` | Upsert | |
| AssessmentQuestionSetConfig | `DeveloperName` | Upsert | |
| AssessmentQuestion | `UniqueIndex` | Upsert | |
| AssessmentQuestionSet | `UniqueIndex` | Upsert | |
| AssessmentQuestionAssignment | traversal composite | **Insert** + deleteOldData | Bug 3 |
| AssessmentQuestionVersion | `Name` | **Insert** + deleteOldData | |
| OmniProcess | `UniqueName` | Upsert | |
| OmniScriptConfig | `DeveloperName` | Upsert | |
| OmniProcessElement | traversal composite | **Insert** + deleteOldData | Bug 3 |
| OmniProcessAsmtQuestionVer | traversal composite | **Insert** + deleteOldData | Bug 3 |

## Standalone Plans

| Plan | SObject | externalId | Operation |
|------|---------|-----------|-----------|
| qb-transactionprocessingtypes | TransactionProcessingType | `DeveloperName` | Upsert |
| qb-product-images | Product2 | `StockKeepingUnit` | Update (DisplayUrl) |
| qb-approvals | ApprovalAlertContentDef | `Name` | Upsert |
| qb-approvals | EmailTemplate | — | ReadOnly |
| scratch_data | Account | `Name` | Upsert |
| scratch_data | Contact | `Name` | Upsert |
