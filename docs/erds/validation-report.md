# ERD Validation Report

Generated: 2026-05-26 18:16:29

## Summary

| Metric | Count |
|--------|-------|
| Objects validated | 263 |
| Objects not found in org | 9 |
| Objects with field gaps | 33 |
| Fields in org missing from ERD | 56 |
| Relationships in org missing from ERD | 14 |
| ERD fields not found in org | 822 |

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

### Dispute
Domain: Billing (Core Object) | ERD fields: 11 | Org fields: 15

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `CaseId` | reference | Case |

**Data fields in org, missing from ERD (10):**

- *currency*: `ApprovedAmount`, `DisputedAmount`
- *date*: `ReceivedDate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `DisputeSubtype`, `DisputeType`, `ResolutionAction`
- *string*: `Name`
- *textarea*: `Description`

**ERD fields not found in org (8):**

- `BillingResumptionDate`
- `BillingSuspensionDate`
- `Contact`
- `Error`
- `Invoice`
- `MaySetContactAsDefault`
- `RevisedBillToContact`
- `RevisedDueDate`

### DisputeItem
Domain: Billing (Core Object) | ERD fields: 2 | Org fields: 8

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `DisputeId` | reference | Dispute |

**Data fields in org, missing from ERD (5):**

- *currency*: `DisputedAmount`
- *date*: `TransactionDate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductConfigurationFlow
Domain: Product Configurator | ERD fields: 12 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AssociatedProcessId` | reference | ApexClass, FlowRecord, GenAiFunctionDefinition, IntegrationProviderDef, OmniScriptConfig |

**Data fields in org, missing from ERD (5):**

- *int*: `Sequence`
- *picklist*: `AnchorObject`, `SubType`, `Type`
- *string*: `ContextDefinitionName`

**ERD fields not found in org (5):**

- `AssignmentType`
- `Lookup`
- `ProductClassificationId`
- `ProductConfigurationFlowId`
- `ReferenceObjectId`

### FulfillmentAsset
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 12

**Data fields in org, missing from ERD (3):**

- *boolean*: `IsTimeAware`
- *datetime*: `StateEndTime`, `StateStartTime`

**ERD fields not found in org (1):**

- `Lookup`

### FulfillmentOrderLineItem
Domain: Dynamic Revenue Orchestrator | ERD fields: 36 | Org fields: 39

**Data fields in org, missing from ERD (3):**

- *double*: `FulfillmentAssetEndQuantity`, `FulfillmentAssetStartQuantity`
- *string*: `FulfillmentAssetReference`

### Invoice
Domain: Billing | ERD fields: 70 | Org fields: 70

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentScheduleId` | reference | PaymentSchedule |

**Data fields in org, missing from ERD (2):**

- *string*: `CreditInvoiceTaxDocNumber`, `DebitInvoiceTaxDocNumber`

**ERD fields not found in org (2):**

- `InvoiceLine`
- `Settled`

### ApprovalSubmission
Domain: Advanced Approvals | ERD fields: 23 | Org fields: 13

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

**ERD fields not found in org (10):**

- `ApprovalChainName`
- `Authentication`
- `Formats`
- `Input`
- `Inputs`
- `IsAutoReviewed`
- `POST`
- `SmartApprovalBasisWorkItemId`
- `Suspended`
- `URI`

### AssetFulfillmentDecomp
Domain: Dynamic Revenue Orchestrator | ERD fields: 9 | Org fields: 9

**Data fields in org, missing from ERD (2):**

- *datetime*: `EndTime`, `StartTime`

**ERD fields not found in org (1):**

- `SourceLineItem`

### BillingSchedule
Domain: Billing | ERD fields: 54 | Org fields: 53

**Data fields in org, missing from ERD (2):**

- *double*: `ProcessingOrder`
- *picklist*: `SubCategory`

**ERD fields not found in org (3):**

- `LineItemCharge`
- `ReadyForInvoicing`
- `Year`

### CreditMemoInvApplication
Domain: Billing | ERD fields: 17 | Org fields: 17

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `LegalEntityId` | reference | LegalEntity |

**ERD fields not found in org (2):**

- `LastViewedDate`
- `Yes`

### FulfillmentAssetRelationship
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 8

**Data fields in org, missing from ERD (2):**

- *datetime*: `EndTime`, `StartTime`

**ERD fields not found in org (1):**

- `FulfillmentAssetId`

### InvoiceLine
Domain: Billing | ERD fields: 65 | Org fields: 63

**Data fields in org, missing from ERD (2):**

- *string*: `RLM_Charge_Type__c`
- *textarea*: `RLM_Attributes__c`

**ERD fields not found in org (4):**

- `OverageUnitOfMeasure`
- `Product`
- `QuoteLineItem`
- `Tax`

### Order
Domain: Transaction Management (Core Object) | ERD fields: 113 | Org fields: 82

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `RLM_Billing_Arrangement__c` | reference | BillingArrangement |
| `RLM_Billing_Profile__c` | reference | BillingAccount |

**ERD fields not found in org (33):**

- `CustomPermissionId`
- `CustomProductName`
- `Discount`
- `DiscountAmount`
- `EffectiveGrantDate`
- `EndDateTime`
- `EndQuantity`
- `EndTime`
- `FulfillmentPlan`
- `IsRamped`
- `Margin`
- `MarginAmount`
- `NetTotalPrice`
- `OrderItemGroup`
- `OrderItemGroupId`
- `ParentOrderItemGroupId`
- `PartnerDiscountPercent`
- `PartnerUnitPrice`
- `PriceWaterfallIdentifier`
- `SalesTransactionType`
- `SegmentType`
- `ServiceDateTime`
- `ServiceTime`
- `StartDate`
- `StartQuantity`
- `SubscriptionTerm`
- `SummaryTotalAmount`
- `TotalAdjustment`
- `TotalAdjustmentAmount`
- `TotalCost`
- `TotalMargin`
- `TotalMarginAmount`
- `UnitCost`

### PaymentScheduleTreatment
Domain: Billing | ERD fields: 12 | Org fields: 11

**Data fields in org, missing from ERD (2):**

- *int*: `DueDateWindow`
- *picklist*: `GroupingSource`

**ERD fields not found in org (2):**

- `Inactive`
- `TreatmentSelection`

### SequenceGapReconciliation
Domain: Billing | ERD fields: 6 | Org fields: 6

**Data fields in org, missing from ERD (2):**

- *long*: `SequenceValue`
- *picklist*: `Status`

**ERD fields not found in org (1):**

- `SequencePolicySelectionConditionName`

### SequencePolicy
Domain: Billing | ERD fields: 20 | Org fields: 19

**Data fields in org, missing from ERD (2):**

- *picklist*: `TimeZone`
- *textarea*: `Description`

**ERD fields not found in org (2):**

- `SequenceValue`
- `Status`

### AssetActionSource
Domain: Transaction Management | ERD fields: 37 | Org fields: 36

**Data fields in org, missing from ERD (1):**

- *textarea*: `RLM_ConstraintEngineNodeStatus__c`

**ERD fields not found in org (2):**

- `LastDayOfPeriod`
- `Lookup`

### CollectionPlan
Domain: Billing (Core Object) | ERD fields: 27 | Org fields: 28

**Data fields in org, missing from ERD (1):**

- *picklist*: `OverdueRiskIndicator`

### CreditMemo
Domain: Billing | ERD fields: 49 | Org fields: 45

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `SequencePolicyId` | reference | SequencePolicy |

**ERD fields not found in org (4):**

- `Name`
- `ProductRelationshipTypeId`
- `Set`
- `Voided`

### ExpressionSet
Domain: Transaction Management | ERD fields: 12 | Org fields: 13

**Data fields in org, missing from ERD (1):**

- *picklist*: `Type`

### FulfillmentStep
Domain: Dynamic Revenue Orchestrator | ERD fields: 46 | Org fields: 40

**Data fields in org, missing from ERD (1):**

- *string*: `CustomConfigParameter`

**ERD fields not found in org (6):**

- `Lookup`
- `Minutes`
- `RequestedCompletionDate`
- `RequestedStartDate`
- `RoundRobin`
- `Skipped`

### FulfillmentStepDefinition
Domain: Dynamic Revenue Orchestrator | ERD fields: 28 | Org fields: 28

**Data fields in org, missing from ERD (1):**

- *string*: `CustomConfigParameter`

**ERD fields not found in org (1):**

- `Lookup`

### InvBatchDraftToPostedRun
Domain: Billing | ERD fields: 17 | Org fields: 14

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BatchJobId` | reference | BatchJob |

**ERD fields not found in org (4):**

- `GeneralLedgerAcctAsgntRuleId`
- `NotApplicable`
- `Percentage`
- `TransactionAmountField`

### InvoiceBatchRun
Domain: Billing | ERD fields: 35 | Org fields: 31

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BatchJobId` | reference | BatchJob |

**ERD fields not found in org (4):**

- `Address`
- `InvoiceAddressGroupNumber`
- `InvoiceId`
- `NotApplicable`

### InvoiceBatchRunRecovery
Domain: Billing | ERD fields: 10 | Org fields: 9

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BatchJobId` | reference | BatchJob |

**ERD fields not found in org (2):**

- `TargetDate`
- `TargetDateOffset`

### OrderItem
Domain: Transaction Management (Core Object) | ERD fields: 95 | Org fields: 91

**Data fields in org, missing from ERD (1):**

- *textarea*: `RLM_ConstraintEngineNodeStatus__c`

**ERD fields not found in org (5):**

- `BillingFrequency`
- `PricingStatus`
- `StartDate`
- `TaxAmount`
- `TotalAdjustmentDistAmount`

### OrderItemGroup
Domain: Transaction Management | ERD fields: 55 | Org fields: 23

**Data fields in org, missing from ERD (1):**

- *percent*: `UnitPriceUplift`

**ERD fields not found in org (33):**

- `AdjustmentDistributionLogic`
- `AppliedDiscount`
- `AppliedDiscountAmount`
- `DeveloperName`
- `EffectiveGrantDate`
- `EndDateTime`
- `EndQuantity`
- `EndTime`
- `Language`
- `LastPricedDate`
- `Lookup`
- `MasterLabel`
- `OriginalActionType`
- `ParentQuoteLineGroupId`
- `PartnerAccountId`
- `PartnerDiscountPercent`
- `PartnerUnitPrice`
- `PriceWaterfallIdentifier`
- `PricingPreference`
- `ProductRelatedComponentId`
- `RatingPreference`
- `StartDateTime`
- `StartEndTimeZone`
- `StartQuantity`
- `StartTime`
- `Status`
- `TotalPriceOverride`
- `TotalPriceWithTax`
- `TotalTaxAmount`
- `TransactionProcessingType`
- `TransactionType`
- `UnitCost`
- `ValidationResult`

### PaymentScheduleItem
Domain: Billing | ERD fields: 27 | Org fields: 28

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentInitiationSourceId` | reference | PaymentInitiationSource |

### Product2
Domain: Product Catalog Management (Core Object) | ERD fields: 46 | Org fields: 33

**Data fields in org, missing from ERD (1):**

- *picklist*: `UsedFor`

**ERD fields not found in org (14):**

- `AlwaysOne`
- `AssociatedProductRoleCat`
- `CatalogType`
- `ChildProductClassificationId`
- `Code`
- `DataType`
- `EffectiveEndDate`
- `EffectiveStartDate`
- `IsDefault`
- `IsNavigational`
- `OrderLineItem`
- `ParentGroupId`
- `ProductClassification`
- `QuoteVisibility`

### QuoteLineGroup
Domain: Transaction Management | ERD fields: 28 | Org fields: 24

**Data fields in org, missing from ERD (1):**

- *percent*: `UnitPriceUplift`

**ERD fields not found in org (5):**

- `ReferenceNumber`
- `TotalLineAmount`
- `TotalPrice`
- `UnitPrice`
- `Yearly`

### QuoteLineItem
Domain: Transaction Management (Core Object) | ERD fields: 91 | Org fields: 90

**Data fields in org, missing from ERD (1):**

- *textarea*: `RLM_ConstraintEngineNodeStatus__c`

**ERD fields not found in org (2):**

- `PricingStatus`
- `TotalAdjustmentDistAmount`

### TransactionJournal
Domain: Usage Management (Core Object) | ERD fields: 34 | Org fields: 27

**Data fields in org, missing from ERD (1):**

- *picklist*: `CreationSourceType`

**ERD fields not found in org (8):**

- `GeneralLedgerAccount`
- `Input`
- `RateUsageType`
- `State`
- `UnrealizedReversal`
- `UsageResource`
- `UsageSummary`
- `ZipCode`

### TransactionUsageEntitlement
Domain: Usage Management | ERD fields: 34 | Org fields: 32

**Data fields in org, missing from ERD (1):**

- *datetime*: `OriginalEndDate`

**ERD fields not found in org (3):**

- `Renewal`
- `UsageCommitmentPolicyId`
- `UsageOveragePolicyId`

### AccountBillingAccount
Domain: Billing (Core Object) | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `Account`

### AccountingPeriod
Domain: Billing | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `Open`

### AssessmentQuestion
Domain: Product Catalog Management | ERD fields: 16 | Org fields: 13

**ERD fields not found in org (2):**

- `ShouldExcludeFromMetadata`
- `ShouldHideInDesigner`

### AssessmentQuestionVersion
Domain: Product Catalog Management | ERD fields: 19 | Org fields: 17

**ERD fields not found in org (1):**

- `ExternalAsmtContentVersion`

### Asset
Domain: Transaction Management | ERD fields: 78 | Org fields: 57

**ERD fields not found in org (18):**

- `AssetTypeId`
- `Availability`
- `AverageUptimePerDay`
- `AveragetimeBetweenFailure`
- `AveragetimetoRepair`
- `Critical`
- `Error`
- `ListPrice`
- `Months`
- `Obsolete`
- `QuantityIncreasePricingType`
- `Reliability`
- `RenewalPricingType`
- `Standby`
- `SumDowntime`
- `SumUnplannedDowntime`
- `UptimeRecordEnd`
- `UptimeRecordStart`

### AssetAction
Domain: Transaction Management | ERD fields: 36 | Org fields: 31

**ERD fields not found in org (5):**

- `Lookup`
- `Other`
- `Renewals`
- `RolledbackAssetAction`
- `TransferTo`

### AssetActionSrcPriceAdjustment
Domain: Transaction Management | ERD fields: 17 | Org fields: 8

**ERD fields not found in org (9):**

- `ContractId`
- `EndDate`
- `LastReferencedDate`
- `LastViewedDate`
- `Lookup`
- `StartDate`
- `TotalPrice`
- `TransactionDate`
- `UnitPrice`

### AssetContractRelationship
Domain: Transaction Management | ERD fields: 10 | Org fields: 7

**ERD fields not found in org (3):**

- `PriceAdjustmentCauseId`
- `PriceAdjustmentSource`
- `PrioritySequence`

### AssetRateAdjustment
Domain: Transaction Management | ERD fields: 8 | Org fields: 6

**ERD fields not found in org (2):**

- `GroupId`
- `UserOrGroupId`

### AssetRateCardEntry
Domain: Transaction Management | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `UpperBound`

### AssetRelationship
Domain: Transaction Management | ERD fields: 18 | Org fields: 15

**ERD fields not found in org (2):**

- `ProductRelatedComponent`
- `UsageResourceId`

### AssetStatePeriod
Domain: Transaction Management | ERD fields: 22 | Org fields: 19

**ERD fields not found in org (3):**

- `Lookup`
- `PriceRevisionPolicy`
- `UserOrGroupId`

### AssetStatePeriodAttribute
Domain: Transaction Management | ERD fields: 13 | Org fields: 6

**ERD fields not found in org (7):**

- `ItemId`
- `Lookup`
- `Name`
- `StartDate`
- `TagDefinitionId`
- `UnitPrice`
- `UnitPriceUplift`

### AssetTokenEvent
Domain: Transaction Management | ERD fields: 15 | Org fields: 13

**ERD fields not found in org (2):**

- `AssetWarrantyNumber`
- `EndDate`

### AttrPicklistExcludedValue
Domain: Product Catalog Management | ERD fields: 90 | Org fields: 5

**ERD fields not found in org (83):**

- `Aggregate`
- `AlwaysOne`
- `AssociatedProductRoleCat`
- `AttributeCategoryId`
- `AttributeDefinitionId`
- `AttributeNameOverride`
- `CanRamp`
- `CatalogType`
- `CategoryId`
- `ChildProductClassificationId`
- `Code`
- `DataType`
- `Date`
- `DecompositionScope`
- `DefaultValue`
- `DeveloperName`
- `DisplayType`
- `DoesBundlePriceIncludeChild`
- `DurationType`
- `EffectiveEndDate`
- `EffectiveFromDate`
- `EffectiveStartDate`
- `EffectiveToDate`
- `ExcludedPicklistValues`
- `FulfillmentQtyCalcMethod`
- `HelpText`
- `IsCommercial`
- `IsComponentRequired`
- `IsDefault`
- `IsDefaultComponent`
- `IsDisqualified`
- `IsExcluded`
- `IsHidden`
- `IsNavigational`
- `IsPriceImpacting`
- `IsQualified`
- `IsQuantityEditable`
- `IsReadOnly`
- `IsRequired`
- `Language`
- `Lookup`
- `MasterLabel`
- `MaxBundleComponents`
- `MaxQuantity`
- `MaximumCharacterCount`
- `MaximumValue`
- `MinBundleComponents`
- `MinQuantity`
- `MinimumCharacterCount`
- `MinimumValue`
- `Months`
- `NamespacePrefix`
- `Never`
- `Number`
- `OrderLineItem`
- `OverriddenProductAttributeDefinitionId`
- `OverrideContextId`
- `ParentGroupId`
- `ParentProductId`
- `Product2Id`
- `ProductClassificationAttributeId`
- `ProductClassificationId`
- `ProductComponentGroupId`
- `ProductDisqualification`
- `ProductId`
- `ProductRelatedComponentId`
- `ProductSellingModelId`
- `ProductSpecificationType`
- `Quantity`
- `QuantityScaleMethod`
- `QuoteVisibility`
- `Reason`
- `Resource`
- `RootProductId`
- `SegmentType`
- `Sequence`
- `Status`
- `StepValue`
- `Text`
- `Toggle`
- `TrialDuration`
- `UsageModelType`
- `ValueDescription`

### AttributeAdjustmentCondition
Domain: Salesforce Pricing | ERD fields: 16 | Org fields: 14

**ERD fields not found in org (2):**

- `Lookup`
- `True`

### AttributeBasedAdjRule
Domain: Salesforce Pricing | ERD fields: 8 | Org fields: 5

**ERD fields not found in org (2):**

- `Lookup`
- `StringValue`

### AttributeBasedAdjustment
Domain: Salesforce Pricing | ERD fields: 22 | Org fields: 17

**ERD fields not found in org (4):**

- `Lookup`
- `Percentage`
- `Quarterly`
- `UsageType`

### AttributeCategory
Domain: Product Catalog Management | ERD fields: 9 | Org fields: 5

**ERD fields not found in org (3):**

- `AttributeCategoryId`
- `AttributeDefinitionId`
- `Lookup`

### AttributeDefinition
Domain: Product Catalog Management | ERD fields: 19 | Org fields: 16

**ERD fields not found in org (2):**

- `HelpText`
- `IsNameRequiredForPicklist`

### AttributePicklist
Domain: Product Catalog Management | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (1):**

- `Code`

### AttributePicklistValue
Domain: Product Catalog Management | ERD fields: 16 | Org fields: 11

**ERD fields not found in org (4):**

- `AttributePicklistId`
- `Description`
- `DisplaySequence`
- `IsActive`

### BillingAccount
Domain: Billing (Core Object) | ERD fields: 34 | Org fields: 28

**ERD fields not found in org (6):**

- `BillDayOfMonth`
- `Contact`
- `PaymentTerm`
- `PaymentTermId`
- `SavedPaymentMethod`
- `ShippingAddress`

### BillingArrangement
Domain: Billing | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (1):**

- `Inactive`

### BillingBatchFilterCriteria
Domain: Billing | ERD fields: 18 | Org fields: 14

**ERD fields not found in org (4):**

- `CustomPercent`
- `CustomText`
- `Inactive`
- `TimeZone`

### BillingBatchScheduler
Domain: Billing | ERD fields: 25 | Org fields: 23

**ERD fields not found in org (1):**

- `Saturday`

### BillingMilestonePlan
Domain: Billing | ERD fields: 11 | Org fields: 10

**ERD fields not found in org (1):**

- `Value`

### BillingMilestonePlanItem
Domain: Billing | ERD fields: 25 | Org fields: 20

**ERD fields not found in org (5):**

- `Event`
- `OrderProductActivation`
- `ReferenceItemAmount`
- `ReferenceItemId`
- `Years`

### BillingPolicy
Domain: Billing | ERD fields: 11 | Org fields: 7

**ERD fields not found in org (4):**

- `Manual`
- `Reviewed`
- `TotalUsedQuantity`
- `UnitOfMeasureId`

### BillingScheduleGroup
Domain: Billing | ERD fields: 70 | Org fields: 64

**ERD fields not found in org (5):**

- `LastDayOfPeriod`
- `None`
- `UnitPrice`
- `UsageResourceId`
- `Year`

### BillingTreatment
Domain: Billing | ERD fields: 14 | Org fields: 10

**ERD fields not found in org (3):**

- `TotalPendingAmount`
- `UsageType`
- `Yes`

### BindingObjUsageRsrcPlcy
Domain: Transaction Management | ERD fields: 15 | Org fields: 12

**ERD fields not found in org (3):**

- `StartDate`
- `WarrantyTermId`
- `WarrantyType`

### BindingObjectRateCardEntry
Domain: Rate Management | ERD fields: 16 | Org fields: 15

**ERD fields not found in org (1):**

- `UpperBound`

### BsgRelationship
Domain: Billing | ERD fields: 14 | Org fields: 9

**ERD fields not found in org (5):**

- `Bundle`
- `None`
- `NotIncludedInBundlePrice`
- `Set`
- `Status`

### BundleBasedAdjustment
Domain: Salesforce Pricing | ERD fields: 23 | Org fields: 18

**ERD fields not found in org (4):**

- `Lookup`
- `Percentage`
- `SourceSystemIdentifier`
- `ValueDescription`

### ContractItemPrice
Domain: Salesforce Pricing | ERD fields: 18 | Org fields: 14

**ERD fields not found in org (3):**

- `AdjustmentPercentage`
- `Lookup`
- `UsageResourceId`

### ContractItemPriceHistory
Domain: Transaction Management | ERD fields: 47 | Org fields: 5

**ERD fields not found in org (42):**

- `Carrier`
- `ClassOfService`
- `DiscountValue`
- `EncryptedText`
- `EndDate`
- `EntityId`
- `EnumOrId`
- `ExternalId`
- `Fax`
- `File`
- `HtmlMultiLineText`
- `HtmlStringPlusClob`
- `InetAddress`
- `IsActive`
- `Item`
- `Json`
- `LastReferencedDate`
- `Location`
- `Lookup`
- `MultiEnum`
- `MultiLineText`
- `Name`
- `Namespace`
- `OverrideAmount`
- `Percent`
- `PersonName`
- `Phone`
- `Price`
- `ProductSellingModel`
- `Raw`
- `RecordType`
- `SfdcEncryptedText`
- `SimpleNamespace`
- `StartDate`
- `StringPlusClob`
- `Switchable_PersonName`
- `Text`
- `TierValue`
- `TimeOnly`
- `UpperBound`
- `Url`
- `YearQuarter`

### CostBook
Domain: Salesforce Pricing | ERD fields: 8 | Org fields: 6

**ERD fields not found in org (1):**

- `Lookup`

### CostBookEntry
Domain: Salesforce Pricing | ERD fields: 12 | Org fields: 9

**ERD fields not found in org (2):**

- `SellingModelType`
- `StartDate`

### CreditMemoAddressGroup
Domain: Billing | ERD fields: 17 | Org fields: 13

**ERD fields not found in org (4):**

- `TotalChargeAmountWithTax`
- `TotalChargeTaxAmount`
- `TotalTaxAmount`
- `TotalTaxesCapturedAtHeader`

### CreditMemoLine
Domain: Billing | ERD fields: 48 | Org fields: 46

**ERD fields not found in org (2):**

- `Unapplied`
- `UnappliedDate`

### CreditMemoLineInvoiceLine
Domain: Billing | ERD fields: 21 | Org fields: 16

**ERD fields not found in org (5):**

- `StartDate`
- `Status`
- `TaxAmount`
- `TaxTreatmentId`
- `Unapplied`

### CreditMemoLineTax
Domain: Billing | ERD fields: 31 | Org fields: 20

**ERD fields not found in org (11):**

- `Complete`
- `CorpCrcyCnvTaxAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`
- `CorporateCurrencyIsoCode`
- `Error`
- `FuncCrcyCnvTaxAmount`
- `FunctionalCurrencyCvsnRate`
- `FunctionalCurrencyIsoCode`
- `None`
- `Product2Id`

### FulfillmentFalloutRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 14 | Org fields: 11

**ERD fields not found in org (2):**

- `Lookup`
- `ProductRelationshipTypeId`

### FulfillmentLineAttribute
Domain: Dynamic Revenue Orchestrator | ERD fields: 8 | Org fields: 6

**ERD fields not found in org (2):**

- `Staggered`
- `StepType`

### FulfillmentLineRel
Domain: Dynamic Revenue Orchestrator | ERD fields: 11 | Org fields: 9

**ERD fields not found in org (2):**

- `ExternalId`
- `FulfillmentOrderLineItemId`

### FulfillmentLineSourceRel
Domain: Dynamic Revenue Orchestrator | ERD fields: 12 | Org fields: 8

**ERD fields not found in org (3):**

- `NoChange`
- `ProductRelationshipTypeId`
- `SourceLineItem`

### FulfillmentPlan
Domain: Dynamic Revenue Orchestrator | ERD fields: 11 | Org fields: 9

**ERD fields not found in org (1):**

- `Bulk`

### FulfillmentStepDefinitionGroup
Domain: Dynamic Revenue Orchestrator | ERD fields: 6 | Org fields: 4

**ERD fields not found in org (1):**

- `ContextBased`

### FulfillmentStepDependency
Domain: Dynamic Revenue Orchestrator | ERD fields: 8 | Org fields: 5

**ERD fields not found in org (3):**

- `DependencyScope`
- `DependsOnStepDefinitionId`
- `FulfillmentStepDefinitionId`

### FulfillmentStepDependencyDef
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `DependsOnStepId`

### FulfillmentStepJeopardyRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 17 | Org fields: 10

**ERD fields not found in org (6):**

- `AutoTask`
- `Callout`
- `Lookup`
- `ManualTask`
- `Milestone`
- `Pause`

### FulfillmentTaskAssignmentRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 12 | Org fields: 10

**ERD fields not found in org (2):**

- `StepId`
- `VersionGroupIdentifier`

### GeneralLedgerAccount
Domain: Billing | ERD fields: 27 | Org fields: 10

**ERD fields not found in org (15):**

- `Billing`
- `ClosingBalanceAmount`
- `CreditGeneralLedgerAccountId`
- `Custom`
- `DebitGeneralLedgerAccountId`
- `FilterCriteria`
- `FilterLogic`
- `GeneralLedgerAccountId`
- `GeneralLedgerAcctAsgntRule`
- `Inactive`
- `Priority`
- `Status`
- `TaxTransactionNumber`
- `TransactionAmountField`
- `TransactionType`

### GeneralLedgerAcctAsgntRule
Domain: Billing | ERD fields: 15 | Org fields: 12

**ERD fields not found in org (2):**

- `Custom`
- `Inactive`

### IndexRate
Domain: Salesforce Pricing | ERD fields: 10 | Org fields: 9

**ERD fields not found in org (1):**

- `Resources`

### InvoiceAddressGroup
Domain: Billing | ERD fields: 13 | Org fields: 11

**ERD fields not found in org (2):**

- `WriteOffTotalChargeAmount`
- `WriteOffTotalTaxAmount`

### InvoiceBatchRunCriteria
Domain: Billing | ERD fields: 15 | Org fields: 10

**ERD fields not found in org (4):**

- `TotalInvoicesCanceled`
- `TotalInvoicesFailed`
- `TotalInvoicesGenerated`
- `TotalPostedInvoices`

### InvoiceDocument
Domain: Billing | ERD fields: 8 | Org fields: 7

**ERD fields not found in org (1):**

- `StartTime`

### InvoiceLineRelationship
Domain: Billing | ERD fields: 16 | Org fields: 10

**ERD fields not found in org (6):**

- `NotIncludedInBundlePrice`
- `Set`
- `SetComponent`
- `UsageOverageQuantity`
- `UsageProductBillSchdGrpId`
- `UsageProductId`

### InvoiceLineTax
Domain: Billing | ERD fields: 25 | Org fields: 21

**ERD fields not found in org (4):**

- `CorpCrcyCnvTaxAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`
- `CorporateCurrencyIsoCode`

### LegalEntyAccountingPeriod
Domain: Billing | ERD fields: 16 | Org fields: 12

**ERD fields not found in org (3):**

- `CreateUnrealizedGainOrLossTransactionJournals`
- `Reopened`
- `ShouldAttachInvoiceDocToEmail`

### OrderDeliveryMethod
Domain: Transaction Management | ERD fields: 13 | Org fields: 10

**ERD fields not found in org (2):**

- `NewValue`
- `OldValue`

### OrderItemAttribute
Domain: Transaction Management | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (2):**

- `Lookup`
- `ShippingCarrierMethod`

### OrderItemDetail
Domain: Transaction Management | ERD fields: 15 | Org fields: 14

**ERD fields not found in org (1):**

- `IsPriceImpacting`

### OrderItemRateAdjustment
Domain: Transaction Management | ERD fields: 11 | Org fields: 6

**ERD fields not found in org (5):**

- `Percentage`
- `ReferenceNumber`
- `TotalLineAmount`
- `TotalPrice`
- `UnitPrice`

### OrderItemRateCardEntry
Domain: Transaction Management | ERD fields: 9 | Org fields: 8

**ERD fields not found in org (1):**

- `UpperBound`

### OrderItemUsageRsrcPlcy
Domain: Transaction Management | ERD fields: 12 | Org fields: 9

**ERD fields not found in org (3):**

- `GrantedLast`
- `ValidityPeriodTerm`
- `ValidityPeriodUnit`

### Payment
Domain: Billing (Core Object) | ERD fields: 58 | Org fields: 57

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### PaymentBatchRun
Domain: Billing | ERD fields: 16 | Org fields: 14

**ERD fields not found in org (2):**

- `TotalLiabilitiesAmount`
- `TotalRevenueAmount`

### PaymentLineInvoice
Domain: Billing (Core Object) | ERD fields: 21 | Org fields: 20

**ERD fields not found in org (1):**

- `LegalEntyAccountingPeriod`

### PaymentLineInvoiceLine
Domain: Billing | ERD fields: 22 | Org fields: 20

**ERD fields not found in org (2):**

- `TotalScheduleItemsApplied`
- `TotalScheduleItemsApplyFailed`

### PaymentRetryRule
Domain: Billing | ERD fields: 16 | Org fields: 12

**ERD fields not found in org (4):**

- `Minutes`
- `Unapplied`
- `UnappliedDateTime`
- `UnappliedStatus`

### PaymentRetryRuleSet
Domain: Billing | ERD fields: 16 | Org fields: 11

**ERD fields not found in org (5):**

- `AvailableRequestedAmount`
- `Minutes`
- `PaymentRetryRuleSetId`
- `RetryIntervalType`
- `Staggered`

### PaymentSchedule
Domain: Billing | ERD fields: 23 | Org fields: 21

**ERD fields not found in org (1):**

- `Name`

### PaymentSchedulePolicy
Domain: Billing | ERD fields: 13 | Org fields: 8

**ERD fields not found in org (4):**

- `TotalPaymentsReceived`
- `TotalProcessedAmount`
- `TotalRequestedAmount`
- `UsageType`

### PaymentScheduleTreatmentDtl
Domain: Billing | ERD fields: 15 | Org fields: 12

**ERD fields not found in org (3):**

- `Inactive`
- `Status`
- `TriggerSource`

### PaymentTerm
Domain: Billing | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `UsageType`

### PaymentTermItem
Domain: Billing | ERD fields: 10 | Org fields: 9

**ERD fields not found in org (1):**

- `Status`

### PriceAdjustmentTier
Domain: Salesforce Pricing | ERD fields: 19 | Org fields: 17

**ERD fields not found in org (1):**

- `Months`

### PriceBook2
Domain: Salesforce Pricing | ERD fields: 13 | Org fields: 10

**ERD fields not found in org (2):**

- `TierValue`
- `UpperBound`

### PricingAPIExecution
Domain: Salesforce Pricing | ERD fields: 9 | Org fields: 8

**ERD fields not found in org (1):**

- `TargetRecord`

### PricingAdjBatchJob
Domain: Salesforce Pricing | ERD fields: 21 | Org fields: 14

**ERD fields not found in org (6):**

- `Amount`
- `Override`
- `Percentage`
- `PricebookEntry`
- `Region`
- `Rerun`

### ProcedurePlanCriterion
Domain: Salesforce Pricing | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (2):**

- `NotIn`
- `ProrationPolicyId`

### ProdtDecompEnrchVarMap
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 7

**ERD fields not found in org (3):**

- `SourceAttributeIdentifier`
- `SourceContextTag`
- `SourceType`

### ProductCategoryProduct
Domain: Product Catalog Management | ERD fields: 11 | Org fields: 6

**ERD fields not found in org (4):**

- `CategoryId`
- `DisplaySequence`
- `LastReferencedDate`
- `LastViewedDate`

### ProductConfigFlowAssignment
Domain: Product Configurator | ERD fields: 10 | Org fields: 7

**ERD fields not found in org (3):**

- `FlowIdentifier`
- `IsDefault`
- `Status`

### ProductConfigurationRule
Domain: Product Configurator | ERD fields: 15 | Org fields: 13

**ERD fields not found in org (1):**

- `ProductId`

### ProductFulfillmentDecompRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `VariableType`

### ProductFulfillmentScenario
Domain: Dynamic Revenue Orchestrator | ERD fields: 17 | Org fields: 14

**ERD fields not found in org (2):**

- `Lookup`
- `Renew`

### ProductRelatedComponent
Domain: Product Catalog Management | ERD fields: 27 | Org fields: 23

**ERD fields not found in org (3):**

- `ProductId`
- `ProductSellingModelId`
- `QuantityUnitOfMeasureId`

### ProductRelationshipType
Domain: Product Catalog Management | ERD fields: 9 | Org fields: 5

**ERD fields not found in org (3):**

- `Code`
- `Description`
- `IsActive`

### ProductSellingModel
Domain: Salesforce Pricing | ERD fields: 11 | Org fields: 8

**ERD fields not found in org (3):**

- `Annual`
- `Quarterly`
- `RecordedPrice`

### ProductSellingModelOption
Domain: Salesforce Pricing | ERD fields: 12 | Org fields: 7

**ERD fields not found in org (4):**

- `DisplayName`
- `Increment`
- `Maximum`
- `Minimum`

### ProductUsageGrant
Domain: Usage Management | ERD fields: 26 | Org fields: 23

**ERD fields not found in org (2):**

- `ProductOfferId`
- `UsageResourceId`

### ProductUsageResource
Domain: Usage Management | ERD fields: 12 | Org fields: 10

**ERD fields not found in org (2):**

- `ValidityPeriodTerm`
- `ValidityPeriodUnit`

### ProrationPolicy
Domain: Salesforce Pricing | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `Sequence`

### QuotLineItmUsageRsrcPlcy
Domain: Transaction Management | ERD fields: 14 | Org fields: 11

**ERD fields not found in org (3):**

- `GrantedLast`
- `ValidityPeriodTerm`
- `ValidityPeriodUnit`

### QuotLineItmUseRsrcGrant
Domain: Transaction Management | ERD fields: 14 | Org fields: 13

**ERD fields not found in org (1):**

- `IsPriceImpacting`

### Quote
Domain: Transaction Management (Core Object) | ERD fields: 131 | Org fields: 104

**ERD fields not found in org (27):**

- `Account`
- `DiscountAmount`
- `EffectiveGrantDate`
- `EndDate`
- `EndDateTime`
- `EndQuantity`
- `EndTime`
- `IsRamped`
- `Margin`
- `MarginAmount`
- `ParentQuoteLineGroupId`
- `PartnerDiscountPercent`
- `PartnerUnitPrice`
- `PriceWaterfallIdentifier`
- `QuoteLineGroup`
- `SegmentType`
- `StartDateTime`
- `StartEndTimeZone`
- `StartQuantity`
- `StartTime`
- `SummaryTotalAmount`
- `TotalAdjustment`
- `TotalAdjustmentAmount`
- `TotalCost`
- `TotalMargin`
- `TotalMarginAmount`
- `UnitCost`

### QuoteLineRateAdjustment
Domain: Transaction Management | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `Percentage`

### QuoteLineRateCardEntry
Domain: Transaction Management | ERD fields: 74 | Org fields: 8

**ERD fields not found in org (66):**

- `AdjustmentDistributionLogic`
- `AppUsageType`
- `AppliedDiscount`
- `AppliedDiscountAmount`
- `CalculationStatus`
- `CustomPermissionId`
- `CustomProductName`
- `DeveloperName`
- `Discount`
- `DiscountAmount`
- `DiscountPercent`
- `EffectiveGrantDate`
- `EndDate`
- `EndDateTime`
- `EndQuantity`
- `EndTime`
- `FulfillmentPlanId`
- `IsRamped`
- `Language`
- `LastPricedDate`
- `Lookup`
- `Margin`
- `MarginAmount`
- `MasterLabel`
- `NetTotalPrice`
- `OrchestrationSbmsStatus`
- `OrderItemGroupId`
- `OriginalActionType`
- `ParentOrderItemGroupId`
- `ParentQuoteLineGroupId`
- `PartnerAccountId`
- `PartnerDiscountPercent`
- `PartnerUnitPrice`
- `PriceWaterfallIdentifier`
- `PricingPreference`
- `ProductRelatedComponentId`
- `QuoteLineRateCardEntryId`
- `RatingPreference`
- `SalesTransactionTypeId`
- `SegmentType`
- `ServiceDateTime`
- `ServiceEndTimeZone`
- `ServiceTime`
- `StartDate`
- `StartDateTime`
- `StartEndTimeZone`
- `StartQuantity`
- `StartTime`
- `Status`
- `SubscriptionTerm`
- `SummaryTotalAmount`
- `TotalAdjustment`
- `TotalAdjustmentAmount`
- `TotalAmountOverride`
- `TotalCost`
- `TotalMargin`
- `TotalMarginAmount`
- `TotalPriceOverride`
- `TotalPriceWithTax`
- `TotalRoundedLineAmount`
- `TotalTaxAmount`
- `TransactionProcessingType`
- `TransactionType`
- `UnitCost`
- `UpperBound`
- `ValidationResult`

### RateAdjustmentByTier
Domain: Rate Management | ERD fields: 18 | Org fields: 17

**ERD fields not found in org (1):**

- `Percentage`

### RateCard
Domain: Rate Management | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (1):**

- `UsageResourceId`

### RatingFrequencyPolicy
Domain: Rate Management | ERD fields: 10 | Org fields: 8

**ERD fields not found in org (1):**

- `Hours`

### RatingRequest
Domain: Rate Management | ERD fields: 11 | Org fields: 8

**ERD fields not found in org (2):**

- `Monthly`
- `UsageResourceId`

### RatingRequestBatchJob
Domain: Rate Management | ERD fields: 10 | Org fields: 7

**ERD fields not found in org (3):**

- `BadRequest`
- `FlowActionCall`
- `InternalError`

### Refund
Domain: Billing (Core Object) | ERD fields: 49 | Org fields: 48

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### RefundLinePayment
Domain: Billing (Core Object) | ERD fields: 20 | Org fields: 19

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### RevenueTransactionErrorLog
Domain: Billing | ERD fields: 17 | Org fields: 15

**ERD fields not found in org (2):**

- `Days`
- `InvoiceLineTax`

### SalesTransactionFulfillReq
Domain: Dynamic Revenue Orchestrator | ERD fields: 19 | Org fields: 12

**ERD fields not found in org (6):**

- `Completed`
- `Failed`
- `Freezing`
- `InProgress`
- `NotStarted`
- `Rejected`

### SalesTransactionType
Domain: Transaction Management | ERD fields: 6 | Org fields: 3

**ERD fields not found in org (2):**

- `UsageOveragePolicyId`
- `UsageResourceId`

### SalesTrxnDeleteEvent
Domain: Dynamic Revenue Orchestrator | ERD fields: 4 | Org fields: 3

**ERD fields not found in org (1):**

- `UsageType`

### SeqPolicySelectionCondition
Domain: Billing | ERD fields: 18 | Org fields: 9

**ERD fields not found in org (8):**

- `DateTime`
- `MultiPicklist`
- `Number`
- `Percent`
- `Picklist`
- `Reference`
- `SequenceGapReconciliationNumber`
- `Text`

### TaxEngine
Domain: Billing | ERD fields: 22 | Org fields: 21

**ERD fields not found in org (1):**

- `Inactive`

### TaxEngineInteractionLog
Domain: Billing | ERD fields: 25 | Org fields: 21

**ERD fields not found in org (4):**

- `TaxPrvdAccountIdentifier`
- `ValidationError`
- `Void`
- `VoidOrDebit`

### TaxEngineProvider
Domain: Billing | ERD fields: 8 | Org fields: 7

**ERD fields not found in org (1):**

- `TaxEngineInteractionLogNumber`

### TaxPolicy
Domain: Billing | ERD fields: 80 | Org fields: 7

**ERD fields not found in org (71):**

- `AccountID`
- `ActivityDate`
- `AddTaxIdentificationDetails`
- `ApplicationBasis`
- `ApprovedAmount`
- `BillDayOfMonth`
- `BillToContactId`
- `Billing`
- `BillingResumptionDate`
- `BillingSuspensionDate`
- `City`
- `CorporateCurrencyCnvAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`
- `CorporateCurrencyIsoCode`
- `Country`
- `Credit`
- `CreditGeneralLedgerAccountId`
- `Debit`
- `DebitGeneralLedgerAccountId`
- `DeliveryTerms`
- `DoesSkipAutomaticPayments`
- `EmailTemplateId`
- `EndDate`
- `Error`
- `FCA`
- `FOB`
- `FlatTaxAmount`
- `ForeignExchangeGainOrLossType`
- `FunctionalCurrencyCnvAmount`
- `FunctionalCurrencyCvsnDate`
- `FunctionalCurrencyCvsnRate`
- `FunctionalCurrencyIsoCode`
- `GeneralLedgerAcctAsgntRuleId`
- `GenlLdgrJournalEntryRuleId`
- `Inactive`
- `InvoiceBalance`
- `InvoiceDocumentTemplateId`
- `InvoiceId`
- `InvoiceLineId`
- `IsDefaultBillingAccount`
- `IsDefaultBillingProfile`
- `LegalEntityAccountingPeriodId`
- `LegalEntityId`
- `MaySetContactAsDefault`
- `PaymentTermId`
- `ProductCode`
- `ProductId`
- `RateUsageType`
- `ReferenceTransactionRecordId`
- `ResolutionAction`
- `ResolutionActionStatus`
- `RevisedBillToContact`
- `RevisedDueDate`
- `SUP`
- `SavedPaymentMethodId`
- `ShippingAddress`
- `ShouldAttachInvoiceDocToEmail`
- `StartDate`
- `State`
- `TaxCode`
- `TaxExemptionExpirationDate`
- `TaxExemptionNumber`
- `TaxExemptionStatus`
- `TaxIdentificationNumber`
- `TaxTreatmentId`
- `TotalInvoiceBalance`
- `TransactionType`
- `UnrealizedReversal`
- `UsageType`
- `ZipCode`

### TaxRate
Domain: Billing (Core Object) | ERD fields: 22 | Org fields: 19

**ERD fields not found in org (1):**

- `LegalEntity`

### UnitOfMeasure
Domain: Usage Management | ERD fields: 15 | Org fields: 12

**ERD fields not found in org (1):**

- `Inactive`

### UnitOfMeasureClass
Domain: Usage Management | ERD fields: 14 | Org fields: 9

**ERD fields not found in org (5):**

- `Inactive`
- `Token`
- `UnitCode`
- `UnitOfMeasureClassId`
- `Usage`

### UsageCmtAssetRelatedObj
Domain: Usage Management | ERD fields: 8 | Org fields: 7

**ERD fields not found in org (1):**

- `UsageResourceId`

### UsageCommitmentPolicy
Domain: Usage Management | ERD fields: 5 | Org fields: 4

**ERD fields not found in org (1):**

- `RelatedObjectId`

### UsageEntitlementAccount
Domain: Usage Management | ERD fields: 16 | Org fields: 14

**ERD fields not found in org (1):**

- `MONTH`

### UsageEntitlementBucket
Domain: Usage Management | ERD fields: 18 | Org fields: 16

**ERD fields not found in org (1):**

- `ProductId`

### UsageEntitlementEntry
Domain: Usage Management | ERD fields: 19 | Org fields: 17

**ERD fields not found in org (2):**

- `Expired`
- `Rollover`

### UsageGrantRenewalPolicy
Domain: Usage Management | ERD fields: 9 | Org fields: 8

**ERD fields not found in org (1):**

- `UsageSummaryId`

### UsageGrantRolloverPolicy
Domain: Usage Management | ERD fields: 10 | Org fields: 8

**ERD fields not found in org (2):**

- `RenewalFrequencyUnit`
- `Year`

### UsageOveragePolicy
Domain: Usage Management | ERD fields: 6 | Org fields: 4

**ERD fields not found in org (2):**

- `ShouldAllowRolloverExpiry`
- `Status`

### UsagePrdGrantBindingPolicy
Domain: Usage Management | ERD fields: 8 | Org fields: 6

**ERD fields not found in org (2):**

- `Account`
- `Target`

### UsageRatableSumCmtAssetRt
Domain: Usage Management | ERD fields: 10 | Org fields: 9

**ERD fields not found in org (1):**

- `UsageResourceId`

### UsageRatableSummary
Domain: Usage Management | ERD fields: 26 | Org fields: 25

**ERD fields not found in org (1):**

- `Product2Id`

### UsageResource
Domain: Usage Management | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `Inactive`

### UsageSummary
Domain: Usage Management | ERD fields: 30 | Org fields: 19

**ERD fields not found in org (11):**

- `Authentication`
- `Formats`
- `Input`
- `Inputs`
- `POST`
- `Sum`
- `URI`
- `UsageAccumulationPeriod`
- `UsageModelType`
- `UsageSummaryId`
- `UsageType`

### ValTfrmGrp
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 8

**ERD fields not found in org (1):**

- `Text`

## Complete Objects (86)

These objects have no gaps between ERD and org:

- `Account` (46 fields)
- `ApprovalAlertContentDef` (5 fields)
- `AssessmentQuestionAssignment` (5 fields)
- `AssessmentQuestionConfig` (4 fields)
- `AssessmentQuestionSet` (6 fields)
- `AssessmentQuestionSetConfig` (4 fields)
- `AttributeCategoryAttribute` (5 fields)
- `BillingArrangementLine` (8 fields)
- `BillingPeriodItem` (16 fields)
- `BillingTreatmentItem` (19 fields)
- `BindingObjectCustomExt` (4 fields)
- `BindingObjectRateAdjustment` (8 fields)
- `ChannelProgram` (6 fields)
- `ChannelProgramLevel` (7 fields)
- `ChannelProgramMember` (6 fields)
- `ClauseCatgConfiguration` (6 fields)
- `CollectionPlanItem` (7 fields)
- `Contact` (57 fields)
- `Contract` (50 fields)
- `ContractItemPriceAdjTier` (8 fields)
- `ContractLineItem` (20 fields)
- `CurrencyType` (5 fields)
- `CustomPermission` (8 fields)
- `DebitMemo` (28 fields)
- `DebitMemoAddress` (13 fields)
- `DebitMemoLine` (31 fields)
- `DebitMemoLineTax` (18 fields)
- `DocumentClauseSet` (7 fields)
- `EmailTemplate` (22 fields)
- `ExpressionSetConstraintObj` (8 fields)
- `FlowOrchestration` (25 fields)
- `FulfillmentAssetAttribute` (6 fields)
- `FulfillmentOrder` (56 fields)
- `FulfillmentStepSource` (5 fields)
- `FulfillmentWorkspace` (4 fields)
- `FulfillmentWorkspaceItem` (5 fields)
- `GeneralLdgrAcctPrdSummary` (9 fields)
- `GeneralLedgerJrnlEntryRule` (7 fields)
- `IntegrationProviderDef` (22 fields)
- `LegalEntity` (18 fields)
- `NamedCredential` (17 fields)
- `ObjectStateActionDefinition` (9 fields)
- `ObjectStateDefinition` (11 fields)
- `ObjectStateTransition` (8 fields)
- `ObjectStateTransitionAction` (8 fields)
- `ObjectStateValue` (8 fields)
- `OmniProcess` (33 fields)
- `OmniProcessAsmtQuestionVer` (7 fields)
- `OmniProcessElement` (18 fields)
- `OmniScriptConfig` (3 fields)
- `OrderItemUsageRsrcGrant` (11 fields)
- `PriceAdjustmentSchedule` (13 fields)
- `PriceBookEntry` (11 fields)
- `PriceBookEntryDerivedPrice` (15 fields)
- `PriceBookRateCard` (6 fields)
- `PriceRevisionPolicy` (9 fields)
- `PricingAdjBatchJobLog` (10 fields)
- `PricingProcessExecution` (10 fields)
- `ProdtAttrScope` (5 fields)
- `ProductAttributeDefinition` (28 fields)
- `ProductCatalog` (9 fields)
- `ProductCategory` (11 fields)
- `ProductCategoryDisqual` (8 fields)
- `ProductCategoryQualification` (7 fields)
- `ProductClassification` (6 fields)
- `ProductClassificationAttr` (25 fields)
- `ProductComponentGroup` (10 fields)
- `ProductComponentGrpOverride` (8 fields)
- `ProductDecompEnrichmentRule` (18 fields)
- `ProductDisqualification` (10 fields)
- `ProductQualification` (9 fields)
- `ProductRampSegment` (8 fields)
- `ProductRelComponentOverride` (15 fields)
- `ProductUsageResourcePolicy` (9 fields)
- `PymtSchdDistributionMethod` (7 fields)
- `QuoteAction` (8 fields)
- `QuoteLineDetail` (14 fields)
- `QuoteLineItemAttribute` (7 fields)
- `RateAdjustmentByAttribute` (18 fields)
- `RateCardEntry` (19 fields)
- `TaxTreatment` (13 fields)
- `TransactionProcessingType` (10 fields)
- `UsageBillingPeriodItem` (19 fields)
- `UsageResourceBillingPolicy` (7 fields)
- `UsageResourcePolicy` (8 fields)
- `ValTfrm` (14 fields)
