# Object-to-Plan Mapping

Which SObject lives in which data plan, its externalId, operation, and upstream dependencies.

## qb-pcm (Product Catalog Management — 28 objects)

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
| ProductComponentGrpOverride | `Name` | Upsert | `excluded: true` — placeholder |
| ProductRelComponentOverride | `Name` | Upsert | `excluded: true` — placeholder |
| ProductCatalog | `Code` | Upsert | |
| ProductCategory | `Code` | Upsert | Self-ref hierarchy |
| ProductCategoryProduct | `ProductCategory.Code;Product.StockKeepingUnit` | Upsert | Junction |
| ProductQualification | `Name` | Upsert | |
| ProductDisqualification | `Name` | Upsert | |
| ProductCategoryDisqual | `Name` | Upsert | |
| ProductCategoryQualification | `Name` | Upsert | |
| ProdtAttrScope | `Name` | Upsert | |

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
| LegalEntity | `Name` | Readonly | 1 | Loaded by qb-tax (runs first) |
| LegalEntyAccountingPeriod | `Name` | Upsert | 1 | |
| PaymentTerm | `Name` | Upsert | 1 | |
| PaymentTermItem | `PaymentTerm.Name;Type` | Upsert | 1 | |
| BillingPolicy | `Name` | Upsert | 1 | |
| BillingTreatment | `Name` | Upsert | 1 | 9 treatments: US/CA/EU/UK × Advance/Arrears + Milestone |
| BillingTreatmentItem | `Name;BillingTreatment.Name` | Upsert | 1 | One item per treatment |
| Product2 | `StockKeepingUnit` | Update | 1 | Sets BillingPolicyId |
| GeneralLedgerAccount | `Name` | Upsert | 1 | |
| GeneralLedgerAcctAsgntRule | `Name` | Upsert | 1 | |
| PaymentRetryRuleSet | `Name` | Upsert | 1 | |
| PaymentRetryRule | `PaymentGatewayErrorCategory;PaymentRetryRuleSet.Name;RetryIntervalType` | Upsert | 1 | |
| SequencePolicy | `Name` | Upsert | 1 | 8 policies (US/CA/EU/UK × Invoice/CreditMemo) |
| SeqPolicySelectionCondition | `ConditionNumber;SequencePolicy.Name` | Upsert | 1 | FilterValue stores LegalEntity name; resolved to ID by resolveSeqPolicyConditionRefs.apex |
| BillingTreatmentItem | — | Update | 2 | Activate |
| BillingTreatment | — | Update | 3 | Activate |
| BillingPolicy | — | Update | 3 | Set DefaultBillingTreatmentId |

## qb-tax (2 passes)

| SObject | externalId | Operation | Pass | Notes |
|---------|-----------|-----------|------|-------|
| LegalEntity | `Name` | Upsert | 1 | Authoritative source (4 entities: US, Canada, EU, UK) |
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

## qb-dro (17 objects)

| SObject | externalId | Operation | Notes |
|---------|-----------|-----------|-------|
| Product2 | `StockKeepingUnit` | Update | Sets DRO fields |
| ProductFulfillmentDecompRule | `Name` | Upsert | |
| ValTfrmGrp | `Name` | Upsert | Value transformation groups |
| ValTfrm | `Name` | Upsert | Value transformations |
| ProductDecompEnrichmentRule | `Name` | Upsert | `excluded: true` — placeholder |
| FulfillmentStepDefinitionGroup | `Name` | Upsert | |
| User | `Name` | ReadOnly | Assignee resolution |
| Group | `Name` | ReadOnly | Queue resolution |
| IntegrationProviderDef | `DeveloperName` | ReadOnly | |
| FulfillmentStepDefinition | `Name` | Upsert | Polymorphic AssignedToId |
| FulfillmentStepDependencyDef | `Name` | Upsert | |
| ProductFulfillmentScenario | `Name` | Upsert | |
| FulfillmentWorkspace | `Name` | Upsert | |
| FulfillmentWorkspaceItem | `FulfillmentWorkspace.Name;FulfillmentStepDefinitionGroup.Name` | Upsert + deleteOldData | Bug 5 — auto-number Name |
| FulfillmentFalloutRule | `Name` | Upsert | |
| FulfillmentStepJeopardyRule | `Name` | Upsert | |
| FulfillmentTaskAssignmentRule | `Name` | Upsert | |

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
| qb-approvals | Group | `Name;Type` | Readonly |
| qb-approvals | User | `Username` | Readonly |
| qb-approvals | GroupMember | `Group.Name;Group.Type;UserOrGroupId$User.Username` | Upsert |
| scratch_data | Account | `Name` | Upsert |
| scratch_data | Contact | `Name` | Upsert |
| scratch_data | BillingAccount | `Name` | Upsert |
