# ERD Validation Report

Generated: 2026-08-15 16:00:06

## Summary

| Metric | Count |
|--------|-------|
| Objects validated | 263 |
| Objects not found in org | 9 |
| Objects with field gaps | 0 |
| Fields in org missing from ERD | 0 |
| Relationships in org missing from ERD | 0 |
| ERD fields not found in org | 58 |

## Objects Not Found in Org

These objects are in `erd-data.json` but could not be described in the target org.
They may require specific licenses, permissions, or features to be enabled.

- `AssetDowntimePeriod` (Transaction Management)
- `AssetOwnerSharingRule` (Transaction Management)
- `AssetShare` (Transaction Management)
- `AssetTag` (Transaction Management)
- `AssetWarranty` (Transaction Management)
- `PricingProcedureResolution` (Salesforce Pricing)
- `ProductPriceHistoryLog` (Salesforce Pricing)
- `ProductPriceRange` (Salesforce Pricing)
- `ProductSellingModelDataTranslation` (Salesforce Pricing)

## Per-Object Gaps

### AccountBillingAccount
Domain: Billing (Core Object) | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `Account`

### Asset
Domain: Transaction Management | ERD fields: 70 | Org fields: 57

**ERD fields not found in org (10):**

- `AssetTypeId`
- `Availability`
- `AverageUptimePerDay`
- `QuantityIncreasePricingType`
- `Reliability`
- `RenewalPricingType`
- `SumDowntime`
- `SumUnplannedDowntime`
- `UptimeRecordEnd`
- `UptimeRecordStart`

### AssetActionSrcPriceAdjustment
Domain: Transaction Management | ERD fields: 11 | Org fields: 9

**ERD fields not found in org (2):**

- `LastReferencedDate`
- `LastViewedDate`

### AssetRelationship
Domain: Transaction Management | ERD fields: 17 | Org fields: 15

**ERD fields not found in org (1):**

- `ProductRelatedComponent`

### AssetStatePeriod
Domain: Transaction Management | ERD fields: 23 | Org fields: 22

**ERD fields not found in org (1):**

- `PriceRevisionPolicy`

### AttributePicklist
Domain: Product Catalog Management | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (1):**

- `Code`

### BillingAccount
Domain: Billing (Core Object) | ERD fields: 32 | Org fields: 28

**ERD fields not found in org (4):**

- `BillDayOfMonth`
- `PaymentTermId`
- `SavedPaymentMethod`
- `ShippingAddress`

### ContractItemPriceHistory
Domain: Transaction Management | ERD fields: 6 | Org fields: 5

**ERD fields not found in org (1):**

- `LastReferencedDate`

### CreditMemoInvApplication
Domain: Billing | ERD fields: 18 | Org fields: 17

**ERD fields not found in org (1):**

- `LastViewedDate`

### CreditMemoLineTax
Domain: Billing | ERD fields: 27 | Org fields: 20

**ERD fields not found in org (7):**

- `CorpCrcyCnvTaxAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`
- `CorporateCurrencyIsoCode`
- `FuncCrcyCnvTaxAmount`
- `FunctionalCurrencyCvsnRate`
- `FunctionalCurrencyIsoCode`

### Dispute
Domain: Billing (Core Object) | ERD fields: 16 | Org fields: 15

**ERD fields not found in org (1):**

- `Invoice`

### FulfillmentLineSourceRel
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 8

**ERD fields not found in org (1):**

- `SourceLineItem`

### FulfillmentStep
Domain: Dynamic Revenue Orchestrator | ERD fields: 44 | Org fields: 41

**ERD fields not found in org (2):**

- `RequestedCompletionDate`
- `RequestedStartDate`

### InvoiceLineTax
Domain: Billing | ERD fields: 26 | Org fields: 23

**ERD fields not found in org (3):**

- `CorpCrcyCnvTaxAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`

### Order
Domain: Transaction Management (Core Object) | ERD fields: 83 | Org fields: 80

**ERD fields not found in org (3):**

- `FulfillmentPlan`
- `SalesTransactionType`
- `TotalAdjustmentAmount`

### OrderItem
Domain: Transaction Management (Core Object) | ERD fields: 94 | Org fields: 92

**ERD fields not found in org (2):**

- `BillingFrequency`
- `TotalAdjustmentDistAmount`

### Payment
Domain: Billing (Core Object) | ERD fields: 58 | Org fields: 57

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### PaymentBatchRun
Domain: Billing | ERD fields: 16 | Org fields: 14

**ERD fields not found in org (2):**

- `TotalLiabilitiesAmount`
- `TotalRevenueAmount`

### ProductCategoryProduct
Domain: Product Catalog Management | ERD fields: 9 | Org fields: 6

**ERD fields not found in org (2):**

- `LastReferencedDate`
- `LastViewedDate`

### ProductSellingModelOption
Domain: Salesforce Pricing | ERD fields: 11 | Org fields: 7

**ERD fields not found in org (3):**

- `Increment`
- `Maximum`
- `Minimum`

### Quote
Domain: Transaction Management (Core Object) | ERD fields: 90 | Org fields: 87

**ERD fields not found in org (3):**

- `Account`
- `EndDate`
- `TotalAdjustmentAmount`

### QuoteLineItem
Domain: Transaction Management (Core Object) | ERD fields: 90 | Org fields: 89

**ERD fields not found in org (1):**

- `TotalAdjustmentDistAmount`

### Refund
Domain: Billing (Core Object) | ERD fields: 51 | Org fields: 50

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### RefundLinePayment
Domain: Billing (Core Object) | ERD fields: 20 | Org fields: 19

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### TaxRate
Domain: Billing (Core Object) | ERD fields: 22 | Org fields: 19

**ERD fields not found in org (1):**

- `LegalEntity`

### TransactionJournal
Domain: Usage Management (Core Object) | ERD fields: 29 | Org fields: 27

**ERD fields not found in org (2):**

- `UsageResource`
- `UsageSummary`

## Complete Objects (228)

These objects have no gaps between ERD and org:

- `Account` (46 fields)
- `AccountingPeriod` (13 fields)
- `ApprovalAlertContentDef` (5 fields)
- `ApprovalSubmission` (15 fields)
- `AssessmentQuestion` (14 fields)
- `AssessmentQuestionAssignment` (5 fields)
- `AssessmentQuestionConfig` (4 fields)
- `AssessmentQuestionSet` (6 fields)
- `AssessmentQuestionSetConfig` (4 fields)
- `AssessmentQuestionVersion` (18 fields)
- `AssetAction` (32 fields)
- `AssetActionSource` (36 fields)
- `AssetContractRelationship` (7 fields)
- `AssetFulfillmentDecomp` (10 fields)
- `AssetRateAdjustment` (6 fields)
- `AssetRateCardEntry` (13 fields)
- `AssetStatePeriodAttribute` (6 fields)
- `AssetTokenEvent` (13 fields)
- `AttrPicklistExcludedValue` (7 fields)
- `AttributeAdjustmentCondition` (14 fields)
- `AttributeBasedAdjRule` (6 fields)
- `AttributeBasedAdjustment` (18 fields)
- `AttributeCategory` (6 fields)
- `AttributeCategoryAttribute` (5 fields)
- `AttributeDefinition` (17 fields)
- `AttributePicklistValue` (12 fields)
- `BillingArrangement` (8 fields)
- `BillingArrangementLine` (8 fields)
- `BillingBatchFilterCriteria` (14 fields)
- `BillingBatchScheduler` (25 fields)
- `BillingMilestonePlan` (10 fields)
- `BillingMilestonePlanItem` (20 fields)
- `BillingPeriodItem` (16 fields)
- `BillingPolicy` (7 fields)
- `BillingSchedule` (61 fields)
- `BillingScheduleGroup` (65 fields)
- `BillingTreatment` (11 fields)
- `BillingTreatmentItem` (19 fields)
- `BindingObjUsageRsrcPlcy` (12 fields)
- `BindingObjectCustomExt` (4 fields)
- `BindingObjectRateAdjustment` (8 fields)
- `BindingObjectRateCardEntry` (15 fields)
- `BsgRelationship` (9 fields)
- `BundleBasedAdjustment` (19 fields)
- `ChannelProgram` (6 fields)
- `ChannelProgramLevel` (7 fields)
- `ChannelProgramMember` (6 fields)
- `ClauseCatgConfiguration` (6 fields)
- `CollectionPlan` (28 fields)
- `CollectionPlanItem` (8 fields)
- `Contact` (57 fields)
- `Contract` (51 fields)
- `ContractItemPrice` (15 fields)
- `ContractItemPriceAdjTier` (8 fields)
- `ContractLineItem` (20 fields)
- `CostBook` (7 fields)
- `CostBookEntry` (10 fields)
- `CreditMemo` (50 fields)
- `CreditMemoAddressGroup` (13 fields)
- `CreditMemoLine` (46 fields)
- `CreditMemoLineInvoiceLine` (18 fields)
- `CurrencyType` (5 fields)
- `CustomPermission` (8 fields)
- `DebitMemo` (29 fields)
- `DebitMemoAddress` (13 fields)
- `DebitMemoLine` (31 fields)
- `DebitMemoLineTax` (18 fields)
- `DisputeItem` (8 fields)
- `DocumentClauseSet` (7 fields)
- `EmailTemplate` (22 fields)
- `ExpressionSet` (13 fields)
- `ExpressionSetConstraintObj` (8 fields)
- `FlowOrchestration` (25 fields)
- `FulfillmentAsset` (12 fields)
- `FulfillmentAssetAttribute` (6 fields)
- `FulfillmentAssetRelationship` (8 fields)
- `FulfillmentFalloutRule` (12 fields)
- `FulfillmentLineAttribute` (6 fields)
- `FulfillmentLineRel` (9 fields)
- `FulfillmentOrder` (57 fields)
- `FulfillmentOrderLineItem` (41 fields)
- `FulfillmentPlan` (10 fields)
- `FulfillmentStepDefinition` (29 fields)
- `FulfillmentStepDefinitionGroup` (5 fields)
- `FulfillmentStepDependency` (5 fields)
- `FulfillmentStepDependencyDef` (7 fields)
- `FulfillmentStepJeopardyRule` (11 fields)
- `FulfillmentStepSource` (5 fields)
- `FulfillmentTaskAssignmentRule` (10 fields)
- `FulfillmentWorkspace` (4 fields)
- `FulfillmentWorkspaceItem` (5 fields)
- `GeneralLdgrAcctPrdSummary` (9 fields)
- `GeneralLedgerAccount` (12 fields)
- `GeneralLedgerAcctAsgntRule` (13 fields)
- `GeneralLedgerJrnlEntryRule` (7 fields)
- `IndexRate` (9 fields)
- `IntegrationProviderDef` (22 fields)
- `InvBatchDraftToPostedRun` (14 fields)
- `Invoice` (71 fields)
- `InvoiceAddressGroup` (11 fields)
- `InvoiceBatchRun` (38 fields)
- `InvoiceBatchRunCriteria` (16 fields)
- `InvoiceBatchRunRecovery` (9 fields)
- `InvoiceDocument` (7 fields)
- `InvoiceLine` (61 fields)
- `InvoiceLineRelationship` (10 fields)
- `LegalEntity` (18 fields)
- `LegalEntyAccountingPeriod` (13 fields)
- `NamedCredential` (17 fields)
- `ObjectStateActionDefinition` (9 fields)
- `ObjectStateDefinition` (11 fields)
- `ObjectStateTransition` (8 fields)
- `ObjectStateTransitionAction` (8 fields)
- `ObjectStateValue` (8 fields)
- `OmniProcess` (35 fields)
- `OmniProcessAsmtQuestionVer` (7 fields)
- `OmniProcessElement` (18 fields)
- `OmniScriptConfig` (3 fields)
- `OrderDeliveryMethod` (11 fields)
- `OrderItemAttribute` (7 fields)
- `OrderItemDetail` (14 fields)
- `OrderItemGroup` (23 fields)
- `OrderItemRateAdjustment` (6 fields)
- `OrderItemRateCardEntry` (8 fields)
- `OrderItemUsageRsrcGrant` (11 fields)
- `OrderItemUsageRsrcPlcy` (9 fields)
- `PaymentLineInvoice` (20 fields)
- `PaymentLineInvoiceLine` (22 fields)
- `PaymentRetryRule` (12 fields)
- `PaymentRetryRuleSet` (11 fields)
- `PaymentSchedule` (22 fields)
- `PaymentScheduleItem` (28 fields)
- `PaymentSchedulePolicy` (9 fields)
- `PaymentScheduleTreatment` (12 fields)
- `PaymentScheduleTreatmentDtl` (12 fields)
- `PaymentTerm` (6 fields)
- `PaymentTermItem` (9 fields)
- `PriceAdjustmentSchedule` (14 fields)
- `PriceAdjustmentTier` (18 fields)
- `PriceBook2` (12 fields)
- `PriceBookEntry` (11 fields)
- `PriceBookEntryDerivedPrice` (15 fields)
- `PriceBookRateCard` (6 fields)
- `PriceRevisionPolicy` (9 fields)
- `PricingAPIExecution` (8 fields)
- `PricingAdjBatchJob` (15 fields)
- `PricingAdjBatchJobLog` (10 fields)
- `PricingProcessExecution` (10 fields)
- `ProcedurePlanCriterion` (7 fields)
- `ProdtAttrScope` (5 fields)
- `ProdtDecompEnrchVarMap` (7 fields)
- `Product2` (34 fields)
- `ProductAttributeDefinition` (29 fields)
- `ProductCatalog` (9 fields)
- `ProductCategory` (11 fields)
- `ProductCategoryDisqual` (8 fields)
- `ProductCategoryQualification` (7 fields)
- `ProductClassification` (6 fields)
- `ProductClassificationAttr` (26 fields)
- `ProductComponentGroup` (10 fields)
- `ProductComponentGrpOverride` (8 fields)
- `ProductConfigFlowAssignment` (7 fields)
- `ProductConfigurationFlow` (14 fields)
- `ProductConfigurationRule` (14 fields)
- `ProductDecompEnrichmentRule` (18 fields)
- `ProductDisqualification` (10 fields)
- `ProductFulfillmentDecompRule` (13 fields)
- `ProductFulfillmentScenario` (15 fields)
- `ProductQualification` (9 fields)
- `ProductRampSegment` (8 fields)
- `ProductRelComponentOverride` (15 fields)
- `ProductRelatedComponent` (24 fields)
- `ProductRelationshipType` (7 fields)
- `ProductSellingModel` (8 fields)
- `ProductUsageGrant` (23 fields)
- `ProductUsageResource` (10 fields)
- `ProductUsageResourcePolicy` (9 fields)
- `ProrationPolicy` (6 fields)
- `PymtSchdDistributionMethod` (7 fields)
- `QuotLineItmUsageRsrcPlcy` (11 fields)
- `QuotLineItmUseRsrcGrant` (13 fields)
- `QuoteAction` (8 fields)
- `QuoteLineDetail` (14 fields)
- `QuoteLineGroup` (23 fields)
- `QuoteLineItemAttribute` (7 fields)
- `QuoteLineRateAdjustment` (6 fields)
- `QuoteLineRateCardEntry` (8 fields)
- `RateAdjustmentByAttribute` (18 fields)
- `RateAdjustmentByTier` (17 fields)
- `RateCard` (8 fields)
- `RateCardEntry` (19 fields)
- `RatingFrequencyPolicy` (7 fields)
- `RatingRequest` (9 fields)
- `RatingRequestBatchJob` (7 fields)
- `RevenueTransactionErrorLog` (15 fields)
- `SalesTransactionFulfillReq` (13 fields)
- `SalesTransactionType` (4 fields)
- `SalesTrxnDeleteEvent` (3 fields)
- `SeqPolicySelectionCondition` (10 fields)
- `SequenceGapReconciliation` (7 fields)
- `SequencePolicy` (20 fields)
- `TaxEngine` (23 fields)
- `TaxEngineInteractionLog` (21 fields)
- `TaxEngineProvider` (7 fields)
- `TaxPolicy` (9 fields)
- `TaxTreatment` (13 fields)
- `TransactionProcessingType` (10 fields)
- `TransactionUsageEntitlement` (28 fields)
- `UnitOfMeasure` (14 fields)
- `UnitOfMeasureClass` (9 fields)
- `UsageBillingPeriodItem` (19 fields)
- `UsageCmtAssetRelatedObj` (7 fields)
- `UsageCommitmentPolicy` (4 fields)
- `UsageEntitlementAccount` (15 fields)
- `UsageEntitlementBucket` (17 fields)
- `UsageEntitlementEntry` (17 fields)
- `UsageGrantRenewalPolicy` (8 fields)
- `UsageGrantRolloverPolicy` (8 fields)
- `UsageOveragePolicy` (4 fields)
- `UsagePrdGrantBindingPolicy` (6 fields)
- `UsageRatableSumCmtAssetRt` (9 fields)
- `UsageRatableSummary` (25 fields)
- `UsageResource` (12 fields)
- `UsageResourceBillingPolicy` (7 fields)
- `UsageResourcePolicy` (8 fields)
- `UsageSummary` (19 fields)
- `ValTfrm` (14 fields)
- `ValTfrmGrp` (9 fields)
