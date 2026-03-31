# RCA-Only vs rlm-base__mar30_1 Comprehensive Object Metadata Diff

Generated: 2026-03-31 18:39:26 UTC

## Compared Orgs

- RCA-only: `rlm-base__rca_only_1` (`00DRL00000NTD4f2AH`)
- Baseline: `rlm-base__mar30_1` (`00DO400000RJJKMMA5`)

## Methodology

- Full object inventory from `sf sobject list` for each org.
- Set diff for objects only in RCA-only vs only in mar30_1.
- Targeted field-level diff for billing-relevant and adjacent core objects using Tooling API `FieldDefinition`.

## Summary

- Objects in RCA-only: **1766**
- Objects in mar30_1: **2314**
- Shared objects: **1766**
- Objects only in RCA-only: **0**
- Objects only in mar30_1: **548**
- Billing-focus objects with field-level deltas: **31**

## Objects Only in RCA-Only

- None

## Objects Only in mar30_1

- `AIAgentStatusEvent`
- `AIMetric`
- `AccountBillingAccount`
- `AccountBillingAccountChangeEvent`
- `AccountBillingAccountFeed`
- `AccountBillingAccountHistory`
- `AccountingPeriod`
- `AccountingPeriodFeed`
- `AccountingPeriodHistory`
- `AccountingPeriodShare`
- `AiJobRunItem`
- `AiJobRunItemShare`
- `AiJobRunStatusEvent`
- `AnalyticRecipeCompleteEvent`
- `AnalyticsLicensedAsset`
- `AnlytDataAssetEventStore`
- `AnlytDataAssetUsageEvent`
- `Assessment`
- `AssessmentChangeEvent`
- `AssessmentConfiguration`
- `AssessmentConfigurationChangeEvent`
- `AssessmentDefinition`
- `AssessmentDefinitionChangeEvent`
- `AssessmentDefinitionFeed`
- `AssessmentDefinitionHistory`
- `AssessmentDefinitionShare`
- `AssessmentEnvelope`
- `AssessmentEnvelopeChangeEvent`
- `AssessmentEnvelopeFeed`
- `AssessmentEnvelopeHistory`
- `AssessmentEnvelopeItem`
- `AssessmentEnvelopeItemChangeEvent`
- `AssessmentEnvelopeItemFeed`
- `AssessmentEnvelopeItemHistory`
- `AssessmentEnvelopeShare`
- `AssessmentFeed`
- `AssessmentHistory`
- `AssessmentQuestion`
- `AssessmentQuestionAssignment`
- `AssessmentQuestionAssignmentChangeEvent`
- `AssessmentQuestionAssignmentFeed`
- `AssessmentQuestionAssignmentHistory`
- `AssessmentQuestionAssignmentShare`
- `AssessmentQuestionChangeEvent`
- `AssessmentQuestionConfig`
- `AssessmentQuestionFeed`
- `AssessmentQuestionHistory`
- `AssessmentQuestionResponse`
- `AssessmentQuestionResponseChangeEvent`
- `AssessmentQuestionResponseFeed`
- `AssessmentQuestionResponseHistory`
- `AssessmentQuestionResponseShare`
- `AssessmentQuestionSet`
- `AssessmentQuestionSetChangeEvent`
- `AssessmentQuestionSetConfig`
- `AssessmentQuestionSetFeed`
- `AssessmentQuestionSetHistory`
- `AssessmentQuestionSetShare`
- `AssessmentQuestionShare`
- `AssessmentQuestionVersion`
- `AssessmentQuestionVersionChangeEvent`
- `AssessmentQuestionVersionFeed`
- `AssessmentQuestionVersionHistory`
- `AssessmentSavedSession`
- `AssessmentSavedSessionFeed`
- `AssessmentSavedSessionHistory`
- `AssessmentShare`
- `AssessmentSignature`
- `AssessmentSignatureChangeEvent`
- `AssessmentSignatureFeed`
- `AssessmentSignatureHistory`
- `AssetFulfillmentDecomp`
- `AssetFulfillmentDecompHistory`
- `AssetFulfillmentDecompShare`
- `AssetRateAdjustment`
- `AssetRateCardEntry`
- `AsyncRequestResponseEvent`
- `BillSchdCreatedEventDetail`
- `BillingAccount`
- `BillingAccountChangeEvent`
- `BillingAccountFeed`
- `BillingAccountHistory`
- `BillingAccountShare`
- `BillingArrangement`
- `BillingArrangementHistory`
- `BillingArrangementLine`
- `BillingArrangementLineHistory`
- `BillingArrangementShare`
- `BillingBatchFilterCriteria`
- `BillingBatchFilterCriteriaHistory`
- `BillingBatchFilterCriteriaShare`
- `BillingBatchScheduler`
- `BillingBatchSchedulerShare`
- `BillingMilestonePlan`
- `BillingMilestonePlanFeed`
- `BillingMilestonePlanHistory`
- `BillingMilestonePlanItem`
- `BillingMilestonePlanItemFeed`
- `BillingMilestonePlanItemHistory`
- `BillingMilestonePlanShare`
- `BillingPeriodItem`
- `BillingPolicy`
- `BillingPolicyHistory`
- `BillingSchedule`
- `BillingScheduleCreatedEvent`
- `BillingScheduleGroup`
- `BillingScheduleGroupHistory`
- `BillingScheduleGroupShare`
- `BillingTreatment`
- `BillingTreatmentHistory`
- `BillingTreatmentItem`
- `BillingTreatmentItemHistory`
- `BindingObjUsageRsrcPlcy`
- `BindingObjUsageRsrcPlcyFeed`
- `BindingObjUsageRsrcPlcyHistory`
- `BindingObjUsageRsrcPlcyShare`
- `BindingObjectCustomExt`
- `BindingObjectCustomExtFeed`
- `BindingObjectCustomExtHistory`
- `BindingObjectCustomExtShare`
- `BindingObjectRateAdjustment`
- `BindingObjectRateAdjustmentFeed`
- `BindingObjectRateAdjustmentHistory`
- `BindingObjectRateCardEntry`
- `BindingObjectRateCardEntryFeed`
- `BindingObjectRateCardEntryHistory`
- `BindingObjectRateCardEntryShare`
- `BotDefinition`
- `BotVersion`
- `BsgRelationship`
- `BsgRelationshipFeed`
- `BusinessProfile`
- `BusinessProfileChangeEvent`
- `BusinessProfileFeed`
- `BusinessProfileHistory`
- `BuyerGroupMember`
- `BuyerGroupMemberShare`
- `CalculatedInsightRangeBound`
- `CalculatedInsightRangeBoundShare`
- `CartItemAttribute`
- `CartItemAttributeChangeEvent`
- `CaseProceeding`
- `CaseProceedingFeed`
- `CaseProceedingHistory`
- `CaseProceedingParticipant`
- `CaseProceedingParticipantFeed`
- `CaseProceedingParticipantHistory`
- `CaseProceedingResult`
- `CaseProceedingResultFeed`
- `CaseProceedingResultHistory`
- `CaseProceedingShare`
- `CollectionCallRepAvlEvent`
- `CollectionPlan`
- `CollectionPlanChangeEvent`
- `CollectionPlanFeed`
- `CollectionPlanHistory`
- `CollectionPlanItem`
- `CollectionPlanItemChangeEvent`
- `CollectionPlanItemFeed`
- `CollectionPlanItemHistory`
- `CollectionPlanReason`
- `CollectionPlanReasonChangeEvent`
- `CollectionPlanReasonFeed`
- `CollectionPlanReasonHistory`
- `CollectionPlanReasonShare`
- `CollectionPlanShare`
- `ContextUseCaseMapping`
- `ContractDocVerContentDoc`
- `ContractDocVerContentDocFeed`
- `ContractDocVerContentDocHistory`
- `ContractDocVersionSection`
- `ContractDocVersionSectionFeed`
- `ContractDocVersionSectionHistory`
- `ContractDocumentReview`
- `ContractDocumentReviewShare`
- `ContractDocumentVersion`
- `ContractDocumentVersionChangeEvent`
- `ContractDocumentVersionFeed`
- `ContractDocumentVersionHistory`
- `ContractType`
- `ContractTypeConfig`
- `ConvDefDialogDailyMetric`
- `ConvDefDialogHourlyMetric`
- `ConvDefSessionMetric`
- `ConversationDefinitionDialog`
- `ConversationDefinitionEventLog`
- `ConversationDefinitionSession`
- `CrMemoProcessErrDtlEvent`
- `CreateAssetOrderDtlEvent`
- `CreateAssetOrderEvent`
- `CreditInvoiceProcessedEvent`
- `CreditMemoAddressGroup`
- `CreditMemoLineInvoiceLine`
- `CreditMemoLineTax`
- `CreditMemoLineTaxFeed`
- `CreditMemoLineTaxHistory`
- `CreditMemoProcessedEvent`
- `DataAssetSemanticGraphEdge`
- `DatasetExport`
- `DatasetExportEvent`
- `DatasetExportPart`
- `DebitMemo`
- `DebitMemoAddress`
- `DebitMemoAddressHistory`
- `DebitMemoFeed`
- `DebitMemoHistory`
- `DebitMemoLine`
- `DebitMemoLineFeed`
- `DebitMemoLineHistory`
- `DebitMemoLineTax`
- `DebitMemoLineTaxFeed`
- `DebitMemoLineTaxHistory`
- `DebitMemoShare`
- `DigitalSignature`
- `DigitalSignatureChangeEvent`
- `DiscoveryPredictionEvent`
- `DocGenBtchStsChgEvent`
- `DocGenerationBatchProcess`
- `DocGenerationBatchProcessShare`
- `DocumentAuthoredContent`
- `DocumentClause`
- `DocumentClauseFeed`
- `DocumentClauseHistory`
- `DocumentClauseSet`
- `DocumentClauseSetFeed`
- `DocumentClauseSetHistory`
- `DocumentClauseSetShare`
- `DocumentClauseShare`
- `DocumentTemplateConfig`
- `ElectronicMediaGroup`
- `ElectronicMediaGroupHistory`
- `ElectronicMediaGroupShare`
- `ElectronicMediaUse`
- `ExpressionSetConstraintObj`
- `ExpressionSetConstraintObjFeed`
- `ExpressionSetConstraintObjHistory`
- `ExpressionSetConstraintObjShare`
- `ExternalDocStorageConfig`
- `FulfillmentAsset`
- `FulfillmentAssetAttribute`
- `FulfillmentAssetHistory`
- `FulfillmentAssetRelationship`
- `FulfillmentAssetShare`
- `FulfillmentFalloutRule`
- `FulfillmentFalloutRuleHistory`
- `FulfillmentFalloutRuleShare`
- `FulfillmentLineAttribute`
- `FulfillmentLineSourceRel`
- `FulfillmentLineSourceRelShare`
- `FulfillmentPlan`
- `FulfillmentPlanChangeEvent`
- `FulfillmentPlanHistory`
- `FulfillmentPlanShare`
- `FulfillmentStep`
- `FulfillmentStepChangeEvent`
- `FulfillmentStepDefinition`
- `FulfillmentStepDefinitionGroup`
- `FulfillmentStepDefinitionGroupHistory`
- `FulfillmentStepDefinitionGroupShare`
- `FulfillmentStepDefinitionHistory`
- `FulfillmentStepDependency`
- `FulfillmentStepDependencyChangeEvent`
- `FulfillmentStepDependencyDef`
- `FulfillmentStepDependencyDefHistory`
- `FulfillmentStepHistory`
- `FulfillmentStepJeopardyRule`
- `FulfillmentStepJeopardyRuleHistory`
- `FulfillmentStepJeopardyRuleShare`
- `FulfillmentStepShare`
- `FulfillmentStepSource`
- `FulfillmentStepSourceChangeEvent`
- `FulfillmentTaskAssignmentRule`
- `FulfillmentTaskAssignmentRuleFeed`
- `FulfillmentTaskAssignmentRuleHistory`
- `FulfillmentTaskAssignmentRuleShare`
- `FulfillmentWorkspace`
- `FulfillmentWorkspaceHistory`
- `FulfillmentWorkspaceItem`
- `FulfillmentWorkspaceItemHistory`
- `FulfillmentWorkspaceShare`
- `GeneralLdgrAcctPrdSummary`
- `GeneralLdgrAcctPrdSummaryHistory`
- `GeneralLedgerAccount`
- `GeneralLedgerAccountHistory`
- `GeneralLedgerAccountShare`
- `GeneralLedgerAcctAsgntRule`
- `GeneralLedgerAcctAsgntRuleHistory`
- `GeneralLedgerAcctAsgntRuleShare`
- `GeneralLedgerJrnlEntryRule`
- `GeneralLedgerJrnlEntryRuleHistory`
- `GeoCountry`
- `GeoCountryShare`
- `GeoState`
- `GoalAssignment`
- `GoalAssignmentFeed`
- `GoalAssignmentHistory`
- `GoalAssignmentRecommendation`
- `GoalAssignmentRecommendationShare`
- `GoalAssignmentShare`
- `GoalDefinition`
- `GoalDefinitionFeed`
- `GoalDefinitionHistory`
- `GoalDefinitionShare`
- `GuestBuyerProfile`
- `InsightsExternalData`
- `InsightsExternalDataPart`
- `InvBatchDraftToPostedRun`
- `InvoiceAddressGroup`
- `InvoiceBatchRun`
- `InvoiceBatchRunCriteria`
- `InvoiceBatchRunCriteriaShare`
- `InvoiceBatchRunRecovery`
- `InvoiceBatchRunShare`
- `InvoiceDocument`
- `InvoiceDocumentFeed`
- `InvoiceErrorDetailEvent`
- `InvoiceLineRelationship`
- `InvoiceLineRelationshipFeed`
- `InvoiceLineTax`
- `InvoiceLineTaxFeed`
- `InvoiceLineTaxHistory`
- `InvoiceProcPymtExclEvent`
- `InvoiceProcessedDetailEvent`
- `InvoiceProcessedEvent`
- `LegalEntyAccountingPeriod`
- `LegalEntyAccountingPeriodFeed`
- `LegalEntyAccountingPeriodHistory`
- `LegalEntyAccountingPeriodShare`
- `MerchAccPaymentMethodSet`
- `MerchAccPaymentMethodSetHistory`
- `MerchAccPaymentMethodType`
- `MerchAccPaymentMethodTypeHistory`
- `MerchantAccount`
- `MerchantAccountChangeEvent`
- `MerchantAccountEvent`
- `MerchantAccountFeed`
- `MerchantAccountHistory`
- `MerchantAccountShare`
- `MlIntentUtterance`
- `MlIntentUtteranceSuggestion`
- `NegInvcLineProcessedEvent`
- `ObjectStateActionDefinition`
- `ObjectStateActionDefinitionFeed`
- `ObjectStateActionDefinitionHistory`
- `ObjectStateActionDefinitionShare`
- `ObjectStateTransitionAction`
- `ObjectStateTransitionActionFeed`
- `ObjectStateTransitionActionHistory`
- `ObjectStateTransitionActionShare`
- `OmniProcessAsmtQuestionVer`
- `OmniProcessAsmtQuestionVerChangeEvent`
- `OmniProcessAsmtQuestionVerFeed`
- `OmniProcessAsmtQuestionVerHistory`
- `OmniProcessAsmtQuestionVerShare`
- `OmniSpvsrConfigAIAgent`
- `OrderItemRateAdjustment`
- `OrderItemRateAdjustmentFeed`
- `OrderItemRateAdjustmentHistory`
- `OrderItemRateCardEntry`
- `OrderItemRateCardEntryFeed`
- `OrderItemRateCardEntryHistory`
- `OrderItemSummaryAttribute`
- `OrderItemSummaryAttributeChangeEvent`
- `OrderItemUsageRsrcGrant`
- `OrderItemUsageRsrcGrantFeed`
- `OrderItemUsageRsrcGrantHistory`
- `OrderItemUsageRsrcPlcy`
- `OrderItemUsageRsrcPlcyFeed`
- `OrderItemUsageRsrcPlcyHistory`
- `PaymentBatchRun`
- `PaymentBatchRunCriteria`
- `PaymentBatchRunCriteriaShare`
- `PaymentBatchRunShare`
- `PaymentInitiationSource`
- `PaymentIntent`
- `PaymentIntentEvent`
- `PaymentIntentHistory`
- `PaymentLineInvoiceLine`
- `PaymentLink`
- `PaymentLinkEvent`
- `PaymentLinkShare`
- `PaymentRetryRule`
- `PaymentRetryRuleSet`
- `PaymentSchedule`
- `PaymentScheduleItem`
- `PaymentSchedulePolicy`
- `PaymentSchedulePolicyShare`
- `PaymentScheduleShare`
- `PaymentScheduleTreatment`
- `PaymentScheduleTreatmentDtl`
- `PaymentScheduleTreatmentShare`
- `PaymentTerm`
- `PaymentTermItem`
- `PdfGenerationReadyEvent`
- `PdfGenerationRequestEvent`
- `PlaceOrderCompletedEvent`
- `PriceBookRateCard`
- `PriceBookRateCardFeed`
- `PriceBookRateCardHistory`
- `ProdtDecompEnrchVarMap`
- `ProductCategoryMedia`
- `ProductCategoryMediaHistory`
- `ProductDecompEnrichmentRule`
- `ProductDecompEnrichmentRuleHistory`
- `ProductFulfillmentDecompRule`
- `ProductFulfillmentDecompRuleHistory`
- `ProductFulfillmentDecompRuleShare`
- `ProductFulfillmentScenario`
- `ProductFulfillmentScenarioHistory`
- `ProductFulfillmentScenarioShare`
- `ProductMedia`
- `ProductMediaChangeEvent`
- `ProductMediaHistory`
- `ProductUsageGrant`
- `ProductUsageGrantFeed`
- `ProductUsageGrantHistory`
- `ProductUsageGrantShare`
- `ProductUsageResource`
- `ProductUsageResourceFeed`
- `ProductUsageResourceHistory`
- `ProductUsageResourcePolicy`
- `ProductUsageResourcePolicyFeed`
- `ProductUsageResourcePolicyHistory`
- `ProductUsageResourceShare`
- `PymtSchdDistributionMethod`
- `PymtSchdDistributionMethodShare`
- `QuotLineItmUsageRsrcPlcy`
- `QuotLineItmUsageRsrcPlcyFeed`
- `QuotLineItmUsageRsrcPlcyHistory`
- `QuotLineItmUseRsrcGrant`
- `QuotLineItmUseRsrcGrantFeed`
- `QuotLineItmUseRsrcGrantHistory`
- `QuoteItemTaxItem`
- `QuoteLinePriceAdjustment`
- `QuoteLineRateAdjustment`
- `QuoteLineRateAdjustmentFeed`
- `QuoteLineRateAdjustmentHistory`
- `QuoteLineRateCardEntry`
- `QuoteLineRateCardEntryFeed`
- `QuoteLineRateCardEntryHistory`
- `QuoteSaveEvent`
- `QuoteToOrderCompletedEvent`
- `QuoteToOrderErrDtlEvent`
- `RateAdjustmentByAttribute`
- `RateAdjustmentByAttributeFeed`
- `RateAdjustmentByAttributeHistory`
- `RateAdjustmentByTier`
- `RateAdjustmentByTierFeed`
- `RateAdjustmentByTierHistory`
- `RateCard`
- `RateCardEntry`
- `RateCardEntryFeed`
- `RateCardEntryHistory`
- `RateCardFeed`
- `RateCardHistory`
- `RateCardShare`
- `RatingFrequencyPolicy`
- `RatingFrequencyPolicyFeed`
- `RatingFrequencyPolicyHistory`
- `RatingFrequencyPolicyShare`
- `RatingRequest`
- `RatingRequestBatchJob`
- `RatingRequestBatchJobFeed`
- `RatingRequestBatchJobHistory`
- `RatingRequestFeed`
- `RatingRequestHistory`
- `RatingRequestShare`
- `Ruleset`
- `RulesetShare`
- `SalesContractLine`
- `SalesContractLineChangeEvent`
- `SalesContractLineFeed`
- `SalesContractLineHistory`
- `SalesTransactionFulfillReq`
- `SalesTransactionFulfillReqShare`
- `SalesTransactionType`
- `SalesTransactionTypeShare`
- `SavedPaymentMethod`
- `SavedPaymentMethodEvent`
- `TaxEngineInteractionLog`
- `TaxPolicy`
- `TaxTreatment`
- `TaxTreatmentItem`
- `TransactionJournal`
- `TransactionJournalChangeEvent`
- `TransactionUsageEntitlement`
- `TransactionUsageEntitlementFeed`
- `TransactionUsageEntitlementHistory`
- `TransactionUsageEntitlementShare`
- `UsageBillingPeriodItem`
- `UsageBillingPeriodItemFeed`
- `UsageBillingPeriodItemHistory`
- `UsageBillingPeriodItemShare`
- `UsageCmtAssetRelatedObj`
- `UsageCmtAssetRelatedObjFeed`
- `UsageCmtAssetRelatedObjHistory`
- `UsageCommitmentPolicy`
- `UsageCommitmentPolicyFeed`
- `UsageCommitmentPolicyHistory`
- `UsageEntitlementAccount`
- `UsageEntitlementAccountFeed`
- `UsageEntitlementAccountHistory`
- `UsageEntitlementAccountShare`
- `UsageEntitlementBucket`
- `UsageEntitlementBucketFeed`
- `UsageEntitlementBucketHistory`
- `UsageEntitlementBucketShare`
- `UsageEntitlementEntry`
- `UsageEntitlementEntryFeed`
- `UsageEntitlementEntryHistory`
- `UsageGrantRenewalPolicy`
- `UsageGrantRenewalPolicyFeed`
- `UsageGrantRenewalPolicyHistory`
- `UsageGrantRolloverPolicy`
- `UsageGrantRolloverPolicyFeed`
- `UsageGrantRolloverPolicyHistory`
- `UsageOveragePolicy`
- `UsageOveragePolicyFeed`
- `UsageOveragePolicyHistory`
- `UsagePrdGrantBindingPolicy`
- `UsagePrdGrantBindingPolicyFeed`
- `UsagePrdGrantBindingPolicyHistory`
- `UsageRatableSumCmtAssetRt`
- `UsageRatableSumCmtAssetRtHistory`
- `UsageRatableSummary`
- `UsageRatableSummaryHistory`
- `UsageRatableSummaryShare`
- `UsageResource`
- `UsageResourceBillingPolicy`
- `UsageResourceBillingPolicyFeed`
- `UsageResourceBillingPolicyHistory`
- `UsageResourceFeed`
- `UsageResourceHistory`
- `UsageResourcePolicy`
- `UsageResourcePolicyFeed`
- `UsageResourcePolicyHistory`
- `UsageResourceShare`
- `UsageSummary`
- `UsageSummaryHistory`
- `UsageSummaryShare`
- `UserUIPreference`
- `ValTfrm`
- `ValTfrmGrp`
- `ValTfrmGrpHistory`
- `ValTfrmGrpShare`
- `ValTfrmHistory`
- `VoidInvoiceProcessedEvent`
- `WaveAssetEvent`

## Billing-Focus Field-Level Diff

### `Account`
- Field count: RCA=49 vs mar30_1=50
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (1)
  - `IsBuyer`
- Shared fields with attribute deltas (0)
  - None

### `AccountingPeriod`
- Object present only in `mar30_1`.

### `BillingMilestonePlan`
- Object present only in `mar30_1`.

### `BillingMilestonePlanItem`
- Object present only in `mar30_1`.

### `BillingPolicy`
- Object present only in `mar30_1`.

### `BillingSchedule`
- Object present only in `mar30_1`.

### `BillingScheduleGroup`
- Object present only in `mar30_1`.

### `BillingTreatment`
- Object present only in `mar30_1`.

### `BillingTreatmentItem`
- Object present only in `mar30_1`.

### `BsgRelationship`
- Object present only in `mar30_1`.

### `CreditMemo`
- Field count: RCA=49 vs mar30_1=55
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (6)
  - `BillingProfileId`
  - `EffectiveDate`
  - `LegalEntityAccountingPeriodId`
  - `LegalEntityId`
  - `SettlementLevel`
  - `SourceAction`
- Shared fields with attribute deltas (0)
  - None

### `CreditMemoLine`
- Field count: RCA=45 vs mar30_1=56
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (11)
  - `Balance`
  - `BillingAddressId`
  - `LegalEntityAccountingPeriodId`
  - `LegalEntityId`
  - `NetCreditsApplied`
  - `ShipFromAddressId`
  - `ShippingAddressId`
  - `TaxDocumentNumber`
  - `TaxStatus`
  - `TaxTransactionNumber`
  - `TaxTreatmentId`
- Shared fields with attribute deltas (0)
  - None

### `CreditMemoLineTax`
- Object present only in `mar30_1`.

### `Invoice`
- Field count: RCA=50 vs mar30_1=77
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (27)
  - `AppType`
  - `BillingArrangementId`
  - `BillingArrangementVerNumber`
  - `BillingProfileId`
  - `ChildInvoiceCount`
  - `CorrelationIdentifier`
  - `CreationMode`
  - `DaysInvoiceOpen`
  - `DaysInvoiceOverdue`
  - `FullSettlementDate`
  - `GroupingKey`
  - `InvBatchDraftToPostedRunId`
  - `InvoiceBatchRunId`
  - `InvoiceReference`
  - `IsBillingScheduleGroupSkipped`
  - `LastEmailDispatchStatus`
  - `LegalEntityAccountingPeriodId`
  - `LegalEntityId`
  - `PaymentExclusionReason`
  - `PaymentTermId`
  - `PostedDate`
  - `SavedPaymentMethodId`
  - `SettlementLevel`
  - `SettlementStatus`
  - `ShouldExcludePayment`
  - `TotalConvertedNegAmount`
  - `UniqueIdentifier`
- Shared fields with attribute deltas (1)
  - `ReferenceEntityId`

### `InvoiceAddressGroup`
- Object present only in `mar30_1`.

### `InvoiceBatchRun`
- Object present only in `mar30_1`.

### `InvoiceLine`
- Field count: RCA=50 vs mar30_1=75
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (25)
  - `Balance`
  - `BillingAddressId`
  - `BillingScheduleGroupId`
  - `BillingScheduleId`
  - `ChargeConvertedNegAmount`
  - `ConvertedNegAmount`
  - `GroupingKey`
  - `HasMultipleItems`
  - `InvoiceLineReference`
  - `IsUsageBasedInvoiceLine`
  - `LegalEntityAccountingPeriodId`
  - `LegalEntityId`
  - `NetCreditsApplied`
  - `NetPaymentsApplied`
  - `ParentInvoiceLineId`
  - `RLM_Account__c`
  - `RLM_Product_Type__c`
  - `ShipFromAddressId`
  - `ShippingAddressId`
  - `TaxDocumentNumber`
  - `TaxTransactionNumber`
  - `TaxTreatmentId`
  - `UsageOverageQuantity`
  - `UsageProductBillSchdGrpId`
  - `UsageProductId`
- Shared fields with attribute deltas (2)
  - `GroupReferenceEntityItemId`
  - `ReferenceEntityItemId`

### `InvoiceLineTax`
- Object present only in `mar30_1`.

### `LegalEntity`
- Field count: RCA=18 vs mar30_1=20
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (2)
  - `EmailTemplateId`
  - `ShouldAttachInvoiceDocToEmail`
- Shared fields with attribute deltas (0)
  - None

### `Order`
- Field count: RCA=86 vs mar30_1=88
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (2)
  - `RLM_FulfillmentPlanIdText__c`
  - `SavedPaymentMethodId`
- Shared fields with attribute deltas (0)
  - None

### `OrderItem`
- Field count: RCA=116 vs mar30_1=121
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (5)
  - `BillingTreatmentId`
  - `EffectiveGrantDate`
  - `RLM_ConstraintEngineNodeStatus__c`
  - `RLM_ProductName__c`
  - `RLM_RampMode__c`
- Shared fields with attribute deltas (1)
  - `BindingInstanceTargetId`

### `Payment`
- Field count: RCA=55 vs mar30_1=67
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (12)
  - `CorporateCurrencyCnvAmount`
  - `CorporateCurrencyCvsnDate`
  - `CorporateCurrencyCvsnRate`
  - `CorporateCurrencyIsoCode`
  - `FunctionalCurrencyCnvAmount`
  - `FunctionalCurrencyCvsnDate`
  - `FunctionalCurrencyCvsnRate`
  - `FunctionalCurrencyIsoCode`
  - `LegalEntityAccountingPeriodId`
  - `LegalEntityId`
  - `PaymentInitiationSourceId`
  - `PaymentIntentId`
- Shared fields with attribute deltas (0)
  - None

### `PaymentMethod`
- Field count: RCA=19 vs mar30_1=20
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (1)
  - `SavedPaymentMethodId`
- Shared fields with attribute deltas (0)
  - None

### `PaymentTerm`
- Object present only in `mar30_1`.

### `PaymentTermItem`
- Object present only in `mar30_1`.

### `Product2`
- Field count: RCA=43 vs mar30_1=44
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (1)
  - `BillingPolicyId`
- Shared fields with attribute deltas (0)
  - None

### `Quote`
- Field count: RCA=62 vs mar30_1=83
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (21)
  - `RLM_Account_Name__c`
  - `RLM_Approval_Level__c`
  - `RLM_Approval_Status__c`
  - `RLM_Discount_Percent__c`
  - `RLM_EndDate__c`
  - `RLM_Payment_Terms__c`
  - `RLM_Sales_Rep_Name__c`
  - `RLM_Seller_City__c`
  - `RLM_Seller_CompanyName__c`
  - `RLM_Seller_Country__c`
  - `RLM_Seller_Email__c`
  - `RLM_Seller_Fax__c`
  - `RLM_Seller_Phone__c`
  - `RLM_Seller_PostalCode__c`
  - `RLM_Seller_State__c`
  - `RLM_Seller_Street__c`
  - `RLM_Seller_Website__c`
  - `RLM_TermMonths__c`
  - `ServiceDocumentTemplate`
  - `TotalPriceWithTax`
  - `TotalTaxAmount`
- Shared fields with attribute deltas (0)
  - None

### `QuoteLineItem`
- Field count: RCA=93 vs mar30_1=102
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (9)
  - `BillingTreatmentId`
  - `RLM_Approval_Level_Calc__c`
  - `RLM_Approval__c`
  - `RLM_ConstraintEngineNodeStatus__c`
  - `RLM_ProductName__c`
  - `RLM_RampMode__c`
  - `TaxTreatmentId`
  - `TotalPriceWithTax`
  - `TotalTaxAmount`
- Shared fields with attribute deltas (1)
  - `BindingInstanceTargetId`

### `RevenueTransactionErrorLog`
- Field count: RCA=24 vs mar30_1=25
- Fields only in RCA (0)
  - None
- Fields only in mar30_1 (1)
  - `BillingScheduleGroupId`
- Shared fields with attribute deltas (4)
  - `PrimaryRecord2Id`
  - `PrimaryRecordId`
  - `RelatedRecord2Id`
  - `RelatedRecordId`

### `TaxPolicy`
- Object present only in `mar30_1`.

### `TaxTreatment`
- Object present only in `mar30_1`.

## Domain Mapping of mar30_1-Only Objects

This section classifies the `mar30_1`-only object list into practical feature domains for gating decisions.

- **Billing / Collections domain** (must align to `billing`): objects with prefixes/names such as `AccountBillingAccount`, `AccountingPeriod`, `Billing*`, `CreditMemo*Tax`, `Invoice*Tax`, `InvoiceBatchRun`, `InvoiceAddressGroup`, `PaymentTermItem`, `BsgRelationship`.
- **Tax-adjacent billing domain** (typically tied to billing configuration): `TaxPolicy`, `TaxTreatment` and related object field references where tax is persisted through billing entities.
- **Analytics / AI platform domain** (independent of billing): objects such as `AIAgentStatusEvent`, `AIMetric`, `Analytic*`, `Anlyt*`, `AiJobRun*`.
- **Assessment / service process domain** (independent of billing): objects with `Assessment*` and process tracking families.
- **General platform metadata/security domain** (independent of billing): `NamedCredential*`, `Metadata*`, `NavigationMenu*`, and other platform administration objects.

## Gating Implications from the Diff

- **Gate by `billing`**: any task/metadata path that references objects listed in the Billing / Collections domain above.
- **Do not gate by `billing`**: Analytics/AI/Assessment/platform families unless they also reference Billing domain objects.
- **Keep shared paths clean**: where shared metadata references Billing objects/fields (for example in base layouts/flexipages), move those references into billing-conditioned overlays so `billing=false` remains viable.
- **Use field-level evidence**: for shared objects (`QuoteLineItem`, `RevenueTransactionErrorLog`, etc.), billing-only field deltas identify exactly which components/queries should be billing-gated.

## How To Use This Document in Implementation

- Treat this file as the source list for `billing` gate expansion in `cumulusci.yml`.
- Start with hard blockers: security group assignment (`RLM_RCB`) and billing-object deploy paths.
- Then apply targeted gating to rating/rates/payments/docgen/ux artifacts that reference billing-only object or field deltas captured above.
