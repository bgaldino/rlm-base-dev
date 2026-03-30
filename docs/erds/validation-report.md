# ERD Validation Report

Generated: 2026-03-26 22:53:06

## Summary

| Metric | Count |
|--------|-------|
| Objects validated | 263 |
| Objects not found in org | 14 |
| Objects with field gaps | 178 |
| Fields in org missing from ERD | 1297 |
| Relationships in org missing from ERD | 281 |
| ERD fields not found in org | 806 |

## Objects Not Found in Org

These objects are in `erd-data.json` but could not be described in the target org.
They may require specific licenses, permissions, or features to be enabled.

- `AssetDowntimePeriod` (Transaction Management)
- `AssetOwnerSharingRule` (Transaction Management)
- `AssetShare` (Transaction Management)
- `AssetTag` (Transaction Management)
- `AssetWarranty` (Transaction Management)
- `Dispute` (Billing (Core Object))
- `DisputeItem` (Billing (Core Object))
- `PricingProcedureResolution` (Salesforce Pricing)
- `ProductPriceHistoryLog` (Salesforce Pricing)
- `ProductPriceRange` (Salesforce Pricing)
- `ProductSellingModelDataTranslation` (Salesforce Pricing)
- `SeqPolicySelectionCondition` (Billing)
- `SequenceGapReconciliation` (Billing)
- `SequencePolicy` (Billing)

## Per-Object Gaps

### Quote
Domain: Transaction Management (Core Object) | ERD fields: 41 | Org fields: 104

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `BillToContactId` | reference | Contact |
| `ContactId` | reference | Contact |
| `ContractId` | reference | Contract |
| `LegalEntityId` | reference | LegalEntity |
| `OpportunityId` | reference | Opportunity |
| `Pricebook2Id` | reference | Pricebook2 |
| `PricingContractId` | reference | Contract |
| `QuoteAccountId` | reference | Account |
| `RelatedQuoteId` | reference | Quote |
| `SalesTransactionTypeId` | reference | SalesTransactionType |

**Data fields in org, missing from ERD (79):**

- *address*: `AdditionalAddress`, `BillingAddress`, `QuoteToAddress`, `ShippingAddress`
- *boolean*: `CanCreateQuoteLineItems`, `IsSyncing`
- *currency*: `GrandTotal`, `ShippingHandling`, `Subtotal`, `Tax`, `TotalPrice`
- *date*: `ExpirationDate`, `RLM_EndDate__c`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `AdditionalLatitude`, `AdditionalLongitude`, `BillingLatitude`, `BillingLongitude`, `QuoteToLatitude`, `QuoteToLongitude`, `RLM_Approval_Level__c`, `RLM_TermMonths__c`, `ShippingLatitude`, `ShippingLongitude`
- *email*: `Email`
- *int*: `LineGroupCount`, `LineItemCount`
- *percent*: `RLM_Discount_Percent__c`
- *phone*: `Fax`, `Phone`
- *picklist*: `AdditionalGeocodeAccuracy`, `BillingGeocodeAccuracy`, `CalculationStatus`, `QuoteToGeocodeAccuracy`, `RLM_Approval_Status__c`, `RLM_Payment_Terms__c`, `RelatedQuoteType`, `ShippingGeocodeAccuracy`
- *string*: `AdditionalCity`, `AdditionalCountry`, `AdditionalName`, `AdditionalPostalCode`, `AdditionalState`, `BillingCity`, `BillingCountry`, `BillingName`, `BillingPostalCode`, `BillingState`, `Name`, `QuoteNumber`, `QuoteToCity`, `QuoteToCountry`, `QuoteToName`, `QuoteToPostalCode`, `QuoteToState`, `RLM_Account_Name__c`, `RLM_Sales_Rep_Name__c`, `RLM_Seller_City__c`, `RLM_Seller_CompanyName__c`, `RLM_Seller_Country__c`, `RLM_Seller_Email__c`, `RLM_Seller_Fax__c`, `RLM_Seller_Phone__c`, `RLM_Seller_PostalCode__c`, `RLM_Seller_State__c`, `RLM_Seller_Street__c`, `RLM_Seller_Website__c`, `ServiceDocumentTemplate`, `ShippingCity`, `ShippingCountry`, `ShippingName`, `ShippingPostalCode`, `ShippingState`
- *textarea*: `AdditionalStreet`, `BillingStreet`, `Description`, `QuoteToStreet`, `ShippingStreet`

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

### OrderItem
Domain: Transaction Management (Core Object) | ERD fields: 27 | Org fields: 90

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillingTreatmentId` | reference | BillingTreatment |
| `BindingInstanceTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract, OrderItem |
| `LegalEntityId` | reference | LegalEntity |
| `OrderActionId` | reference | OrderAction |
| `OrderDeliveryGroupId` | reference | OrderDeliveryGroup |
| `OrderItemRecipientId` | reference | OrderItemRecipient |
| `ParentOrderItemId` | reference | OrderItem |
| `PriceRevisionPolicyId` | reference | PriceRevisionPolicy |
| `QuantityUnitOfMeasureId` | reference | UnitOfMeasure |
| `RelatedOrderItemId` | reference | OrderItem |
| `ReplacementGroupId` | reference | OrderItemGroup |
| `TaxTreatmentId` | reference | TaxTreatment |

**Data fields in org, missing from ERD (56):**

- *boolean*: `DoesAutomaticallyRenew`, `IsOrderItemLocked`, `IsPrimarySegment`
- *currency*: `DiscountAmount`, `GrossUnitPrice`, `MarginAmount`, `NetTotalPrice`, `PartnerUnitPrice`, `TotalAdjustmentTaxAmount`, `TotalAmtWithTax`, `TotalCost`, `TotalLineAdjustmentAmount`, `TotalLineAdjustmentTaxAmount`, `TotalLineTaxAmount`, `TotalMarginAmount`, `TotalTaxAmount`, `UnitCost`
- *date*: `EarliestEstimatedDeliveryDate`, `EffectiveGrantDate`, `LatestEstimatedDeliveryDate`
- *double*: `AggregatedQuantity`, `AvailableQuantity`, `EndQuantity`, `PricingTermCount`, `StartQuantity`
- *int*: `LineNumber`, `SubscriptionTerm`
- *percent*: `Discount`, `Margin`, `PartnerDiscountPercent`, `TotalAdjustment`, `TotalMargin`, `UnitPriceUplift`
- *picklist*: `BillingFrequency2`, `EstimatedDeliveryTimeZone`, `PeriodBoundaryStartMonth`, `RLM_RampMode__c`, `SegmentType`, `Status`, `SupplementalChangeType`, `Type`, `TypeCode`, `ValidationResult`
- *string*: `BatchIdentifier`, `BillingReference2`, `CustomProductName`, `EstimatedDeliveryReference`, `PriceWaterfallIdentifier`, `RLM_ProductName__c`, `RampIdentifier`, `RelatedChangeIdentifier`, `RevenueCloudPackagingFlag`, `SegmentIdentifier`, `SegmentName`
- *time*: `EarliestEstimatedDeliveryTime`, `LatestEstimatedDeliveryTime`

**ERD fields not found in org (5):**

- `BillingFrequency`
- `PricingStatus`
- `StartDate`
- `TaxAmount`
- `TotalAdjustmentDistAmount`

### QuoteLineItem
Domain: Transaction Management (Core Object) | ERD fields: 25 | Org fields: 89

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillingTreatmentId` | reference | BillingTreatment |
| `BindingInstanceTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract, QuoteLineItem |
| `LegalEntityId` | reference | LegalEntity |
| `OpportunityLineItemId` | reference | OpportunityLineItem |
| `ParentQuoteLineItemId` | reference | QuoteLineItem |
| `PriceRevisionPolicyId` | reference | PriceRevisionPolicy |
| `PricingContractId` | reference | Contract |
| `QuantityUnitOfMeasureId` | reference | UnitOfMeasure |
| `QuoteActionId` | reference | QuoteAction |
| `QuoteLineItemRecipientId` | reference | QuoteLineItemRecipient |
| `QuoteRecipientGroupId` | reference | QuoteRecipientGroup |
| `RelatedQuoteLineItemId` | reference | QuoteLineItem |
| `ReplacementGroupId` | reference | QuoteLineGroup |
| `TaxTreatmentId` | reference | TaxTreatment |

**Data fields in org, missing from ERD (52):**

- *boolean*: `DoesAutomaticallyRenew`, `IsPrimarySegment`
- *currency*: `DiscountAmount`, `MarginAmount`, `NetTotalPrice`, `PartnerUnitPrice`, `Subtotal`, `TotalCost`, `TotalMarginAmount`, `TotalPriceWithTax`, `TotalTaxAmount`, `UnitCost`
- *date*: `EffectiveGrantDate`
- *datetime*: `EndDateTime`, `LastReferencedDate`, `LastViewedDate`, `StartDateTime`
- *double*: `AggregatedQuantity`, `EndQuantity`, `PricingTermCount`, `RLM_Approval_Level_Calc__c`, `StartQuantity`
- *int*: `PricingTerm`, `RecipientScaledQuantity`, `SubscriptionTerm`
- *percent*: `Margin`, `PartnerDiscountPercent`, `TotalAdjustment`, `TotalMargin`, `UnitPriceUplift`
- *picklist*: `PeriodBoundaryStartMonth`, `PricingTermUnit`, `RLM_RampMode__c`, `SegmentType`, `SellingModelType`, `StartEndTimeZone`, `SubscriptionTermUnit`, `ValidationResult`, `Visibility`
- *string*: `BatchIdentifier`, `BillingReference`, `CustomProductName`, `PriceWaterfallIdentifier`, `ProductInstanceIdentifier`, `RLM_Approval__c`, `RLM_ProductName__c`, `RampIdentifier`, `RevenueCloudPackagingFlag`, `SegmentIdentifier`, `SegmentName`
- *time*: `EndTime`, `StartTime`

**ERD fields not found in org (2):**

- `PricingStatus`
- `TotalAdjustmentDistAmount`

### Order
Domain: Transaction Management (Core Object) | ERD fields: 48 | Org fields: 80

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `ActivatedById` | reference | User |
| `BillToContactId` | reference | Contact |
| `CompanyAuthorizedById` | reference | User |
| `ContractId` | reference | Contract |
| `CustomerAuthorizedById` | reference | Contact |
| `FulfillmentPlanId` | reference | FulfillmentPlan |
| `LegalEntityId` | reference | LegalEntity |
| `OriginalOrderId` | reference | Order |
| `PaymentTermId` | reference | PaymentTerm |
| `Pricebook2Id` | reference | Pricebook2 |
| `QuoteId` | reference | Quote |
| `RelatedOrderId` | reference | Order |
| `SalesChannelId` | reference | SalesChannel |
| `ShipToContactId` | reference | Contact |

**Data fields in org, missing from ERD (50):**

- *address*: `BillingAddress`, `ShippingAddress`
- *boolean*: `IsReductionOrder`
- *currency*: `GrandTotalAmount`, `TotalAdjustedDeliveryAmount`, `TotalAdjustedDeliveryTaxAmount`, `TotalAdjustedProductAmount`, `TotalAdjustedProductTaxAmount`, `TotalAmount`, `TotalDeliveryAdjDistAmount`, `TotalDeliveryAdjDistTaxAmount`, `TotalProductAdjDistAmount`, `TotalProductAdjDistTaxAmount`, `TotalTaxAmount`
- *date*: `CompanyAuthorizedDate`, `CustomerAuthorizedDate`, `EffectiveDate`, `PoDate`
- *datetime*: `ActivatedDate`, `LastReferencedDate`, `LastViewedDate`, `OrderedDate`
- *double*: `BillingLatitude`, `BillingLongitude`, `ShippingLatitude`, `ShippingLongitude`
- *email*: `BillingEmailAddress`
- *phone*: `BillingPhoneNumber`
- *picklist*: `BillingGeocodeAccuracy`, `RelatedOrderType`, `ShippingGeocodeAccuracy`, `StatusCode`, `TaxLocaleType`, `Type`
- *string*: `BillingCity`, `BillingCountry`, `BillingPostalCode`, `BillingState`, `Name`, `OrderNumber`, `OrderReferenceNumber`, `PoNumber`, `RLM_FulfillmentPlanIdText__c`, `ShippingCity`, `ShippingCountry`, `ShippingPostalCode`, `ShippingState`
- *textarea*: `BillingStreet`, `Description`, `ShippingStreet`

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

### Contact
Domain: Transaction Management (Core Object) | ERD fields: 6 | Org fields: 57

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `IndividualId` | reference | Individual |
| `MasterRecordId` | reference | Contact |
| `ReportsToId` | reference | Contact |

**Data fields in org, missing from ERD (48):**

- *address*: `MailingAddress`, `OtherAddress`
- *boolean*: `CanAllowPortalSelfReg`, `DoNotCall`, `HasOptedOutOfEmail`, `HasOptedOutOfFax`, `IsEmailBounced`
- *date*: `Birthdate`
- *datetime*: `EmailBouncedDate`, `LastCURequestDate`, `LastCUUpdateDate`, `LastReferencedDate`, `LastViewedDate`
- *double*: `MailingLatitude`, `MailingLongitude`, `OtherLatitude`, `OtherLongitude`
- *multipicklist*: `BuyerAttributes`
- *phone*: `AssistantPhone`, `Fax`, `HomePhone`, `MobilePhone`, `OtherPhone`
- *picklist*: `ContactSource`, `DepartmentGroup`, `LeadSource`, `MailingGeocodeAccuracy`, `OtherGeocodeAccuracy`, `Salutation`, `TitleType`
- *string*: `AssistantName`, `Department`, `EmailBouncedReason`, `Jigsaw`, `JigsawContactId`, `MailingCity`, `MailingCountry`, `MailingPostalCode`, `MailingState`, `Name`, `OtherCity`, `OtherCountry`, `OtherPostalCode`, `OtherState`
- *textarea*: `Description`, `MailingStreet`, `OtherStreet`
- *url*: `PhotoUrl`

### FulfillmentOrder
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 56

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillToContactId` | reference | Contact |
| `DeliveryMethodId` | reference | OrderDeliveryMethod |
| `FulfilledFromLocationId` | reference | Location |
| `InvoiceId` | reference | Invoice |
| `OrderSummaryId` | reference | OrderSummary |

**Data fields in org, missing from ERD (44):**

- *address*: `FulfilledToAddress`
- *boolean*: `IsReship`, `IsSuspended`
- *currency*: `GrandTotalAmount`, `TotalAdjustmentAmount`, `TotalAdjustmentAmtWithTax`, `TotalAdjustmentTaxAmount`, `TotalDeliveryAdjustAmount`, `TotalDeliveryAdjustAmtWithTax`, `TotalDeliveryAdjustTaxAmount`, `TotalDeliveryAmount`, `TotalDeliveryAmtWithTax`, `TotalDeliveryTaxAmount`, `TotalFeeAdjustAmount`, `TotalFeeAdjustAmtWithTax`, `TotalFeeAdjustTaxAmount`, `TotalFeeAmount`, `TotalFeeAmtWithTax`, `TotalFeeTaxAmount`, `TotalProductAmount`, `TotalProductAmtWithTax`, `TotalProductTaxAmount`, `TotalTaxAmount`
- *datetime*: `ActivatedDate`, `ClosedDate`, `DeliveryDate`, `LastReferencedDate`, `LastViewedDate`, `StartFulfillmentDate`
- *double*: `FulfilledToLatitude`, `FulfilledToLongitude`, `ItemCount`
- *email*: `FulfilledToEmailAddress`
- *int*: `ProcessingTimeInMinutes`
- *phone*: `FulfilledToPhone`
- *picklist*: `FulfilledToGeocodeAccuracy`, `StatusCategory`, `TaxLocaleType`, `TypeCategory`
- *string*: `FulfilledToCity`, `FulfilledToCountry`, `FulfilledToPostalCode`, `FulfilledToState`
- *textarea*: `FulfilledToStreet`

### Payment
Domain: Billing (Core Object) | ERD fields: 10 | Org fields: 57

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `LegalEntityId` | reference | LegalEntity |
| `OrderPaymentSummaryId` | reference | OrderPaymentSummary |
| `PaymentAuthorizationId` | reference | PaymentAuthorization |
| `PaymentGatewayId` | reference | PaymentGateway |
| `PaymentGroupId` | reference | PaymentGroup |
| `PaymentInitiationSourceId` | reference | PaymentInitiationSource |
| `PaymentIntentId` | reference | PaymentIntent |
| `PaymentMethodId` | reference | PaymentMethod |

**Data fields in org, missing from ERD (39):**

- *currency*: `Amount`, `Balance`, `ImpactAmount`, `NetApplied`, `NetPaymentCreditApplied`, `NetRefundApplied`, `TotalApplied`, `TotalPaymentCreditApplied`, `TotalPaymentCreditUnapplied`, `TotalRefundApplied`, `TotalRefundUnapplied`, `TotalUnapplied`
- *datetime*: `CancellationDate`, `CancellationEffectiveDate`, `CancellationGatewayDate`, `Date`, `EffectiveDate`, `GatewayDate`, `LastReferencedDate`, `LastViewedDate`
- *email*: `Email`
- *phone*: `Phone`
- *picklist*: `ProcessingMode`, `SfResultCode`, `Status`, `Type`
- *string*: `CancellationGatewayRefNumber`, `CancellationGatewayResultCode`, `CancellationSfResultCode`, `GatewayRefNumber`, `GatewayResultCode`, `GatewayResultCodeDescription`, `IpAddress`, `MacAddress`, `PaymentIntentGuid`, `PaymentNumber`
- *textarea*: `ClientContext`, `Comments`, `GatewayRefDetails`

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### Contract
Domain: Transaction Management (Core Object) | ERD fields: 8 | Org fields: 50

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ActivatedById` | reference | User |
| `CompanySignedId` | reference | User |
| `ContractDocumentVersionId` | reference | ContractDocumentVersion |
| `CustomerSignedId` | reference | Contact |
| `Pricebook2Id` | reference | Pricebook2 |
| `SourceOpportunityId` | reference | Opportunity |
| `SourceOrderId` | reference | Order |
| `SourceQuoteId` | reference | Quote |

**Data fields in org, missing from ERD (34):**

- *address*: `ShippingAddress`
- *boolean*: `IsAssociatedWithClm`, `IsPricingContract`
- *date*: `CompanySignedDate`, `CustomerSignedDate`
- *datetime*: `ActivatedDate`, `LastApprovedDate`, `LastReferencedDate`, `LastViewedDate`
- *double*: `BillingLatitude`, `BillingLongitude`, `RenewalTerm2`, `ShippingLatitude`, `ShippingLongitude`
- *percent*: `UnitPriceUplift`
- *picklist*: `BillingGeocodeAccuracy`, `PricingSource`, `RenewalTermUnit`, `ShippingGeocodeAccuracy`, `StatusCode`
- *string*: `BillingCity`, `BillingCountry`, `BillingPostalCode`, `BillingState`, `ContractType`, `CustomerSignedTitle`, `ShippingCity`, `ShippingCountry`, `ShippingPostalCode`, `ShippingState`
- *textarea*: `BillingStreet`, `Description`, `ShippingStreet`, `SpecialTerms`

### CreditMemoLine
Domain: Billing | ERD fields: 7 | Org fields: 46

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `CreditMemoId` | reference | CreditMemo |
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `LegalEntityId` | reference | LegalEntity |
| `Product2Id` | reference | Product2 |
| `ReferenceEntityItemId` | reference | InvoiceLine, OrderItem, OrderItemSummary |
| `RelatedLineId` | reference | CreditMemoLine |
| `ShipFromAddressId` | reference | CreditMemoAddressGroup |
| `ShippingAddressId` | reference | CreditMemoAddressGroup |
| `TaxTreatmentId` | reference | TaxTreatment |

**Data fields in org, missing from ERD (32):**

- *currency*: `ChargeAmount`, `ChargeAmountWithTax`, `ChargeTaxAmount`, `GrossUnitPrice`, `LineAmount`, `NetCreditsApplied`, `TaxAmount`
- *date*: `CorporateCurrencyCvsnDate`, `EndDate`, `FunctionalCurrencyCvsnDate`, `StartDate`, `TaxEffectiveDate`
- *double*: `CorpCurrencyCnvChargeAmt`, `CorpCurrencyCnvTotalTaxAmt`, `CorporateCurrencyCvsnRate`, `FuncCrcyCnvTotalTaxAmt`, `FuncCurrencyCnvChargeAmt`, `FunctionalCurrencyCvsnRate`
- *percent*: `TaxRate`
- *picklist*: `ReferenceEntityItemType`, `ReferenceEntityItemTypeCode`, `TaxStatus`, `Type`
- *string*: `CorporateCurrencyIsoCode`, `Description`, `FunctionalCurrencyIsoCode`, `Name`, `Status`, `TaxCode`, `TaxDocumentNumber`, `TaxName`, `TaxTransactionNumber`

**ERD fields not found in org (2):**

- `Unapplied`
- `UnappliedDate`

### Refund
Domain: Billing (Core Object) | ERD fields: 11 | Org fields: 48

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `OrderPaymentSummaryId` | reference | OrderPaymentSummary |
| `PaymentGatewayId` | reference | PaymentGateway |
| `PaymentGroupId` | reference | PaymentGroup |
| `PaymentId` | reference | Payment |
| `PaymentIntentId` | reference | PaymentIntent |
| `PaymentMethodId` | reference | PaymentMethod |

**Data fields in org, missing from ERD (31):**

- *currency*: `Amount`, `Balance`, `ImpactAmount`, `NetApplied`, `TotalApplied`, `TotalUnapplied`
- *datetime*: `CancellationDate`, `CancellationEffectiveDate`, `CancellationGatewayDate`, `Date`, `EffectiveDate`, `GatewayDate`, `LastReferencedDate`, `LastViewedDate`
- *email*: `Email`
- *phone*: `Phone`
- *picklist*: `ProcessingMode`, `SfResultCode`, `Status`, `Type`
- *string*: `CancellationGatewayRefNumber`, `CancellationGatewayResultCode`, `CancellationSfResultCode`, `GatewayRefNumber`, `GatewayResultCode`, `GatewayResultCodeDescription`, `IpAddress`, `MacAddress`, `RefundNumber`
- *textarea*: `ClientContext`, `Comments`

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### Account
Domain: Transaction Management (Core Object) | ERD fields: 15 | Org fields: 44

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `MasterRecordId` | reference | Account |

**Data fields in org, missing from ERD (30):**

- *boolean*: `IsBuyer`, `IsCustomerPortal`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `BillingLatitude`, `BillingLongitude`, `ShippingLatitude`, `ShippingLongitude`
- *phone*: `Fax`
- *picklist*: `AccountSource`, `BillingGeocodeAccuracy`, `Ownership`, `ShippingGeocodeAccuracy`
- *string*: `AccountNumber`, `BillingPostalCode`, `ChannelProgramLevelName`, `ChannelProgramName`, `Jigsaw`, `JigsawCompanyId`, `ShippingCity`, `ShippingCountry`, `ShippingPostalCode`, `ShippingState`, `SicDesc`, `SourceSystemIdentifier`
- *textarea*: `BillingStreet`, `Description`, `ShippingStreet`
- *url*: `PhotoUrl`, `Website`

### FulfillmentOrderLineItem
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 36

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `FulfillmentAssetId` | reference | FulfillmentAsset |
| `MainFulfillmentOrderLineItemId` | reference | FulfillmentOrderLineItem |
| `OrderItemSummaryId` | reference | OrderItemSummary |
| `PrevFulfilOrderLineItemId` | reference | FulfillmentOrderLineItem |
| `UnitOfMeasureId` | reference | UnitOfMeasure |

**Data fields in org, missing from ERD (24):**

- *boolean*: `IsReship`
- *currency*: `GrossUnitPrice`, `TotalAdjustmentAmount`, `TotalAdjustmentAmountWithTax`, `TotalAdjustmentTaxAmount`, `TotalAmount`, `TotalLineAmount`, `TotalLineAmountWithTax`, `TotalLineTaxAmount`, `TotalTaxAmount`, `UnitPrice`
- *datetime*: `EndDate`, `ServiceDate`
- *double*: `OriginalQuantity`, `RejectedQuantity`
- *picklist*: `Action`, `RejectReason`, `ReshipReason`, `SupplementalAction`, `TypeCode`
- *string*: `FulfillmentOrderLineItemNumber`, `FulfmtOrdItmVerGrpIdentifier`, `QuantityUnitOfMeasure`, `ScopeIdentifierText`

### TransactionUsageEntitlement
Domain: Usage Management | ERD fields: 6 | Org fields: 31

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `EntitlementUomClassId` | reference | UnitOfMeasureClass |
| `EntitlementUomId` | reference | UnitOfMeasure |
| `GrantBindingTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `OrderItemId` | reference | OrderItem, WorkOrderLineItem |
| `PricebookEntryId` | reference | PricebookEntry |
| `ProductId` | reference | Product2 |
| `RatingFrequencyPolicyId` | reference | RatingFrequencyPolicy |
| `TokenResourceId` | reference | UsageResource |
| `UsageAggregationPolicyId` | reference | UsageResourceBillingPolicy |
| `UsageGrantRefreshPolicyId` | reference | UsageGrantRenewalPolicy |
| `UsageGrantRolloverPolicyId` | reference | UsageGrantRolloverPolicy |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (16):**

- *datetime*: `EffectiveEndDateTime`, `EffectiveStartDateTime`, `LastReferencedDate`, `LastViewedDate`
- *double*: `EntitlementQuantity`, `NetQuantity`, `TransactionQuantity`
- *int*: `ValidityPeriodTerm`
- *picklist*: `ChargeForOverage`, `DrawdownOrder`, `EntitlementProcessingStatus`, `GrantType`, `UsageModelType`, `ValidityPeriodUnit`
- *string*: `ExternalOrderItem`, `Name`

**ERD fields not found in org (3):**

- `Renewal`
- `UsageCommitmentPolicyId`
- `UsageOveragePolicyId`

### BillingScheduleGroup
Domain: Billing | ERD fields: 43 | Org fields: 64

**Data fields in org, missing from ERD (27):**

- *currency*: `TotalPendingAmount`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `BillingLatitude`, `BillingLongitude`, `ShipFromLatitude`, `ShipFromLongitude`, `ShippingLatitude`, `ShippingLongitude`
- *picklist*: `BillingGeocodeAccuracy`, `ShipFromGeocodeAccuracy`, `ShippingGeocodeAccuracy`
- *string*: `BillingCity`, `BillingCountry`, `BillingPostalCode`, `BillingState`, `ShipFromCity`, `ShipFromCountry`, `ShipFromPostalCode`, `ShipFromState`, `ShippingCity`, `ShippingCountry`, `ShippingPostalCode`, `ShippingState`
- *textarea*: `BillingStreet`, `ShipFromStreet`, `ShippingStreet`

**ERD fields not found in org (5):**

- `LastDayOfPeriod`
- `None`
- `UnitPrice`
- `UsageResourceId`
- `Year`

### CollectionPlan
Domain: Billing (Core Object) | ERD fields: 1 | Org fields: 27

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `BillingAccountId` | reference | BillingAccount |
| `CollectionAgencyAccountId` | reference | Account |
| `CollectionPlanReasonId` | reference | CollectionPlanReason |
| `ContactId` | reference | Contact |
| `LegalRepresentativeId` | reference | Contact |

**Data fields in org, missing from ERD (20):**

- *boolean*: `IsClosed`
- *currency*: `InitialDueAmount`, `TotalTaxAmount`
- *date*: `ClosedDate`, `Duedate`
- *datetime*: `FirstCallDateTime`, `FirstEmailDateTime`, `FirstSmsDateTime`, `LastReferencedDate`, `LastViewedDate`
- *double*: `RiskScore`
- *int*: `AutoDebitRequestCount`, `DaysPastDue`, `MaximumPromisetoPayCount`, `PromiseToPayCount`
- *picklist*: `CollectionPlanSegment`, `InteractionOutcome`, `Status`, `UsageType`
- *string*: `Name`

### FlowOrchestration
Domain: Dynamic Revenue Orchestrator | ERD fields: 0 | Org fields: 25

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ActiveVersionId` | reference | FlowOrchestrationVersion |
| `OverriddenById` | reference | FlowOrchestration |
| `OverriddenOrchestrationId` | reference | FlowOrchestration |
| `SourceTemplateId` | reference | FlowOrchestration |

**Data fields in org, missing from ERD (21):**

- *boolean*: `IsCitizenEnabled`, `IsOverridable`, `IsTemplate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *int*: `ApiVersion`, `AverageRunTime`, `FailedRunCount`, `RunCount`
- *percent*: `CompletionRate`
- *picklist*: `ManageableState`, `OrchestrationType`, `Status`, `TriggerType`
- *string*: `ApiName`, `InstalledPackageName`, `Name`, `NamespacePrefix`, `OrchestrationDefinition`, `OrchestrationLabel`
- *textarea*: `Description`

### IntegrationProviderDef
Domain: Dynamic Revenue Orchestrator | ERD fields: 1 | Org fields: 22

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ApexClassId` | reference | ApexClass |
| `InputDataProcessorId` | reference | OmniIntegrationProcConfig |
| `OmniUiCardConfigId` | reference | OmniUiCardConfig |
| `OutputDataProcessorId` | reference | OmniIntegrationProcConfig |

**Data fields in org, missing from ERD (17):**

- *boolean*: `CanUseInIntegrationOrch`, `IsActive`, `IsManual`, `IsServiceTypeIntegration`
- *picklist*: `Language`, `StorePayload`, `Type`
- *string*: `Description`, `ExternalServiceOperationName`, `FileBasedApexClass`, `FileBasedExternalService`, `FileBasedInputDataProcessor`, `FileBasedOmniUiCard`, `FileBasedOutputDataProcessor`, `JavaClassName`, `MasterLabel`, `NamespacePrefix`

### InvoiceLineTax
Domain: Billing | ERD fields: 6 | Org fields: 21

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `InvoiceLineId` | reference | InvoiceLine |
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `LegalEntityId` | reference | LegalEntity |
| `ShipFromAddressId` | reference | InvoiceAddressGroup |
| `ShippingAddressId` | reference | InvoiceAddressGroup |
| `TaxTreatmentId` | reference | TaxTreatment |

**Data fields in org, missing from ERD (13):**

- *currency*: `TaxAmount`, `TaxExemptAmount`
- *date*: `EndDate`, `StartDate`, `TaxEffectiveDate`
- *percent*: `TaxRate`
- *picklist*: `TaxProcessingStatus`
- *string*: `Description`, `InvoiceLineTaxNumber`, `TaxCode`, `TaxDocumentNumber`, `TaxName`, `TaxTransactionNumber`

**ERD fields not found in org (4):**

- `CorpCrcyCnvTaxAmount`
- `CorporateCurrencyCvsnDate`
- `CorporateCurrencyCvsnRate`
- `CorporateCurrencyIsoCode`

### PaymentLineInvoice
Domain: Billing (Core Object) | ERD fields: 2 | Org fields: 20

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AssociatedAccountId` | reference | Account |
| `AssociatedPaymentLineId` | reference | PaymentLineInvoice |
| `InvoiceId` | reference | Invoice |
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `PaymentId` | reference | Payment |

**Data fields in org, missing from ERD (14):**

- *currency*: `Amount`, `EffectiveImpactAmount`, `ImpactAmount`, `PaymentBalance`
- *datetime*: `AppliedDate`, `Date`, `EffectiveDate`, `LastReferencedDate`, `LastViewedDate`, `UnappliedDate`
- *picklist*: `HasBeenUnapplied`, `Type`
- *string*: `PaymentLineInvoiceNumber`
- *textarea*: `Comments`

**ERD fields not found in org (1):**

- `LegalEntyAccountingPeriod`

### UsageRatableSummary
Domain: Usage Management | ERD fields: 7 | Org fields: 25

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `GrantBindingTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `NetUnitRateUomId` | reference | UnitOfMeasure |
| `OverageQuantityUomId` | reference | UnitOfMeasure |
| `RatingRequestId` | reference | RatingRequest |
| `SourceUsageResourceId` | reference | UsageResource |
| `TierQuantityUomId` | reference | UnitOfMeasure |
| `UsageEntitlementAccountId` | reference | UsageEntitlementAccount |
| `UsageEntitlementBucketId` | reference | UsageEntitlementBucket |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (10):**

- *datetime*: `LastReferencedDate`, `RatingDecisionDateTime`, `StartDateTime`
- *double*: `NetUnitRate`, `OverageQuantity`, `TierQuantity`, `TotalAmount`
- *picklist*: `Status`
- *string*: `ErrorDescription`, `RatingExecutionIdentifier`

**ERD fields not found in org (1):**

- `Product2Id`

### EmailTemplate
Domain: Approvals | ERD fields: 4 | Org fields: 22

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BrandTemplateId` | reference | BrandTemplate |
| `EnhancedLetterheadId` | reference | EnhancedLetterhead |
| `FolderId` | reference | Folder, Organization, User |

**Data fields in org, missing from ERD (15):**

- *boolean*: `IsActive`, `IsBuilderContent`
- *datetime*: `LastUsedDate`
- *double*: `ApiVersion`
- *int*: `TimesUsed`
- *picklist*: `Encoding`, `RelatedEntityType`, `TemplateStyle`, `TemplateType`
- *string*: `Description`, `FolderName`, `Name`, `NamespacePrefix`
- *textarea*: `Body`, `Markup`

### UsageBillingPeriodItem
Domain: Usage Management | ERD fields: 1 | Org fields: 19

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AssetId` | reference | Asset |
| `GrantBindingTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `UoMId` | reference | UnitOfMeasure |
| `UsageEntitlementAccountId` | reference | UsageEntitlementAccount |
| `UsageEntitlementBucketId` | reference | UsageEntitlementBucket |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (12):**

- *currency*: `OverageAmount`
- *datetime*: `EndDateTime`, `LastReferencedDate`, `LastViewedDate`, `StartDateTime`
- *double*: `OverageAmountDerived`, `OverageQuantity`, `TotalUsedQuantity`
- *picklist*: `ErrorCode`, `Status`
- *string*: `ErrorDescription`, `UsageBillingPeriodItemNum`

### DebitMemo
Domain: Billing | ERD fields: 11 | Org fields: 28

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `InvoiceMatchingRefKeyId` | reference | Asset, Product2 |
| `LegalEntityId` | reference | LegalEntity |
| `ReferenceRecordId` | reference | CreditMemo |

**Data fields in org, missing from ERD (14):**

- *boolean*: `IsManuallyProcessed`
- *currency*: `TotalAmount`, `TotalChargeAmount`, `TotalTaxAmount`
- *date*: `NextBillingDate`, `PostedDate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `CorpCrcyCnvTotAmt`, `FuncCrcyCnvTotAmt`
- *picklist*: `ReasonCode`, `Status`
- *string*: `Description`, `InvoiceMatchingRefName`

### RefundLinePayment
Domain: Billing (Core Object) | ERD fields: 3 | Org fields: 19

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AssociatedAccountId` | reference | Account |
| `AssociatedRefundLinePaymentId` | reference | RefundLinePayment |
| `PaymentId` | reference | Payment |
| `RefundId` | reference | Refund |

**Data fields in org, missing from ERD (13):**

- *currency*: `Amount`, `EffectiveImpactAmount`, `ImpactAmount`, `PaymentBalance`, `RefundBalance`
- *datetime*: `AppliedDate`, `Date`, `EffectiveDate`, `UnappliedDate`
- *picklist*: `HasBeenUnapplied`, `Type`
- *string*: `RefundLinePaymentNumber`
- *textarea*: `Comments`

**ERD fields not found in org (1):**

- `LegalEntityAccountingPeriod`

### UsageSummary
Domain: Usage Management | ERD fields: 13 | Org fields: 19

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AssetId` | reference | Asset |
| `GrantBindingTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `LiableSummaryId` | reference | UsageBillingPeriodItem |
| `ParentUsageSummaryId` | reference | UsageSummary |
| `RatableSummaryId` | reference | UsageRatableSummary |
| `UomId` | reference | UnitOfMeasure |
| `UsageEntitlementAccountId` | reference | UsageEntitlementAccount |
| `UsageEntitlementBucketId` | reference | UsageEntitlementBucket |

**Data fields in org, missing from ERD (9):**

- *datetime*: `EndDateTime`, `LastReferencedDate`, `LastViewedDate`, `StartDateTime`
- *double*: `ConsumptionUnits`, `DebitedUnits`, `OverageUnits`
- *picklist*: `Status`
- *string*: `Name`

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

### DebitMemoLineTax
Domain: Billing | ERD fields: 2 | Org fields: 17

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `DebitMemoLineId` | reference | DebitMemoLine |
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `LegalEntityId` | reference | LegalEntity |
| `ShipFromAddressId` | reference | DebitMemoAddress |
| `ShippingAddressId` | reference | DebitMemoAddress |

**Data fields in org, missing from ERD (11):**

- *currency*: `TaxAmount`
- *date*: `EndDate`, `StartDate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *percent*: `TaxRate`
- *string*: `DebitMemoLineTaxNumber`, `Description`, `JurisdictionTaxCode`, `JurisdictionTaxName`, `TaxTransactionNumber`

### InvoiceLine
Domain: Billing | ERD fields: 49 | Org fields: 61

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `RelatedLineId` | reference | InvoiceLine |
| `ShipFromAddressId` | reference | InvoiceAddressGroup |
| `UsageProductBillSchdGrpId` | reference | BillingScheduleGroup |
| `UsageProductId` | reference | Product2 |

**Data fields in org, missing from ERD (12):**

- *currency*: `GrossUnitPrice`
- *date*: `InvoiceLineEndDate`, `TaxEffectiveDate`
- *double*: `Quantity`, `UsageOverageQuantity`
- *percent*: `TaxRate`
- *picklist*: `Type`
- *string*: `Description`, `TaxCode`, `TaxDocumentNumber`, `TaxName`, `TaxTransactionNumber`

**ERD fields not found in org (4):**

- `OverageUnitOfMeasure`
- `Product`
- `QuoteLineItem`
- `Tax`

### NamedCredential
Domain: Dynamic Revenue Orchestrator | ERD fields: 1 | Org fields: 17

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AuthProviderId` | reference | AuthProvider |

**Data fields in org, missing from ERD (15):**

- *boolean*: `CalloutOptionsAllowMergeFieldsInBody`, `CalloutOptionsAllowMergeFieldsInHeader`, `CalloutOptionsGenerateAuthorizationHeader`
- *int*: `JwtValidityPeriodSeconds`
- *picklist*: `Language`, `PrincipalType`
- *string*: `Description`, `JwtFormulaSubject`, `JwtIssuer`, `JwtTextSubject`, `MasterLabel`, `NamespacePrefix`
- *textarea*: `AuthTokenEndpointUrl`, `Endpoint`, `JwtAudience`

### ProductRelComponentOverride
Domain: Product Catalog Management | ERD fields: 0 | Org fields: 15

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `OverrideContextId` | reference | Product2, Promotion |
| `ProductRelatedComponentId` | reference | ProductRelatedComponent |
| `UnitOfMeasureId` | reference | UnitOfMeasure |

**Data fields in org, missing from ERD (12):**

- *boolean*: `DoesBundlePriceIncludeChild`, `IsComponentRequired`, `IsDefaultComponent`, `IsExcluded`, `IsQuantityEditable`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `MaxQuantity`, `MinQuantity`, `Quantity`
- *picklist*: `QuantityScaleMethod`
- *string*: `Name`

### TransactionJournal
Domain: Usage Management (Core Object) | ERD fields: 19 | Org fields: 26

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `GenlLdgrJournalEntryRuleId` | reference | GeneralLedgerJrnlEntryRule |
| `LegalEntityId` | reference | LegalEntity |
| `LegalEntyAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `QuantityUnitOfMeasureId` | reference | UnitOfMeasure |
| `ReferenceRecordId` | reference | Asset |
| `ReferenceTransactionRecordId` | reference | CreditMemo, CreditMemoInvApplication, CreditMemoLine, CreditMemoLineInvoiceLine, CreditMemoLineTax, DebitMemoLine, DebitMemoLineTax, Invoice, InvoiceLine, InvoiceLineTax, Payment, PaymentLineInvoice, PaymentLineInvoiceLine, Refund, RefundLinePayment |

**Data fields in org, missing from ERD (8):**

- *datetime*: `EndDate`, `LastReferencedDate`, `LastViewedDate`
- *double*: `Quantity`
- *picklist*: `Status`, `TransactionType`
- *string*: `Name`, `UniqueIdentifier`

**ERD fields not found in org (8):**

- `GeneralLedgerAccount`
- `Input`
- `RateUsageType`
- `State`
- `UnrealizedReversal`
- `UsageResource`
- `UsageSummary`
- `ZipCode`

### BillingSchedule
Domain: Billing | ERD fields: 40 | Org fields: 51

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (13):**

- *boolean*: `IsBilledThroughPeriodUpdated`
- *currency*: `UnitPrice`
- *date*: `BilledThroughPeriod`
- *double*: `BilledAmountDerived`, `BillingPeriodAmountDerived`, `LineAmountDerived`, `PendingAmountDerived`, `TotalAmountDerived`, `UnitPriceDerived`
- *int*: `GroupingKeyVersion`
- *picklist*: `BpiGenerationStatus`, `Type`
- *string*: `GroupingKey`

**ERD fields not found in org (3):**

- `LineItemCharge`
- `ReadyForInvoicing`
- `Year`

### Invoice
Domain: Billing | ERD fields: 56 | Org fields: 66

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillingProfileId` | reference | BillingAccount |

**Data fields in org, missing from ERD (13):**

- *currency*: `TotalAmount`, `WriteOffTotalChargeAmount`, `WriteOffTotalTaxAmount`
- *int*: `BillingArrangementVerNumber`, `ChildInvoiceCount`
- *picklist*: `AppType`, `CreationMode`, `Status`, `TaxLocaleType`
- *string*: `CorporateCurrencyIsoCode`, `Description`, `GroupingKey`, `InvoiceReference`

**ERD fields not found in org (3):**

- `InvoiceLine`
- `SequencePolicyId`
- `Settled`

### ContractLineItem
Domain: Transaction Management | ERD fields: 7 | Org fields: 20

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `LocationId` | reference | Location |
| `ParentContractLineItemId` | reference | ContractLineItem |
| `PricebookEntryId` | reference | PricebookEntry |
| `RootContractLineItemId` | reference | ContractLineItem |

**Data fields in org, missing from ERD (9):**

- *currency*: `ListPrice`, `Subtotal`, `TotalPrice`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *percent*: `Discount`
- *picklist*: `Status`
- *string*: `LineItemNumber`
- *textarea*: `Description`

### AssetAction
Domain: Transaction Management | ERD fields: 24 | Org fields: 31

**Data fields in org, missing from ERD (12):**

- *currency*: `TotalInitialSaleAmount`, `TotalMrr`, `TotalOtherAmount`, `TotalRenewalsAmount`, `TotalSwapsAmount`, `TotalTermsAndConditionsAmount`, `TotalTransfersAmount`, `TotalUpgradesAmount`, `TotalUpsellsAmount`
- *double*: `TotalQuantity`
- *picklist*: `Type`
- *textarea*: `AssetStatePeriodHistory`

**ERD fields not found in org (5):**

- `Lookup`
- `Other`
- `Renewals`
- `RolledbackAssetAction`
- `TransferTo`

### AssetTokenEvent
Domain: Transaction Management | ERD fields: 3 | Org fields: 13

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ConnectedAppId` | reference | ConnectedApplication |
| `ExternalClientApplicationId` | reference | ExternalClientApplication |
| `UserId` | reference | User |

**Data fields in org, missing from ERD (9):**

- *datetime*: `Expiration`
- *string*: `AssetName`, `AssetSerialNumber`, `DeviceId`, `EventUuid`, `Name`, `ReplayId`
- *textarea*: `ActorTokenPayload`, `DeviceKey`

**ERD fields not found in org (2):**

- `AssetWarrantyNumber`
- `EndDate`

### BillingAccount
Domain: Billing (Core Object) | ERD fields: 22 | Org fields: 28

**Data fields in org, missing from ERD (12):**

- *address*: `PrimaryBillAddr`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `PrimaryBillAddrLatitude`, `PrimaryBillAddrLongitude`
- *picklist*: `PrimaryBillAddrGeocodeAccuracy`
- *string*: `Name`, `PrimaryBillAddrCity`, `PrimaryBillAddrCountry`, `PrimaryBillAddrPostalCode`, `PrimaryBillAddrState`
- *textarea*: `PrimaryBillAddrStreet`

**ERD fields not found in org (6):**

- `BillDayOfMonth`
- `Contact`
- `PaymentTerm`
- `PaymentTermId`
- `SavedPaymentMethod`
- `ShippingAddress`

### BindingObjUsageRsrcPlcy
Domain: Transaction Management | ERD fields: 3 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BindingObjectId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `RatingFrequencyPolicyId` | reference | RatingFrequencyPolicy |
| `UsageAggregationPolicyId` | reference | UsageResourceBillingPolicy |
| `UsageCommitmentPolicyId` | reference | UsageCommitmentPolicy |
| `UsageOveragePolicyId` | reference | UsageOveragePolicy |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (6):**

- *datetime*: `EffectiveEndDate`, `EffectiveStartDate`, `LastReferencedDate`, `LastViewedDate`
- *picklist*: `DrawdownOrder`
- *string*: `Name`

**ERD fields not found in org (3):**

- `StartDate`
- `WarrantyTermId`
- `WarrantyType`

### ExpressionSet
Domain: Transaction Management | ERD fields: 0 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ExpressionSetDefinitionId` | reference | ExpressionSetDefinition |

**Data fields in org, missing from ERD (11):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `ExecutionMode`, `ExecutionScale`, `InterfaceSourceType`, `ResourceInitializationType`, `UsageSubtype`, `UsageType`
- *string*: `ApiName`, `Description`, `Name`

### PaymentLineInvoiceLine
Domain: Billing | ERD fields: 10 | Org fields: 20

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `LegalEntityAccountingPeriodId` | reference | LegalEntyAccountingPeriod |
| `LegalEntityId` | reference | LegalEntity |
| `PaymentId` | reference | Payment |
| `RelatedPaymentLineInvcLineId` | reference | PaymentLineInvoiceLine |

**Data fields in org, missing from ERD (8):**

- *currency*: `PaymentBalance`
- *datetime*: `LastReferencedDate`, `LastViewedDate`, `UnappliedDateTime`
- *picklist*: `Type`, `UnappliedStatus`
- *string*: `PaymentLineInvoiceLineNumber`
- *textarea*: `Description`

**ERD fields not found in org (2):**

- `TotalScheduleItemsApplied`
- `TotalScheduleItemsApplyFailed`

### Product2
Domain: Product Catalog Management (Core Object) | ERD fields: 34 | Org fields: 32

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BasedOnId` | reference | ProductClassification |
| `ExternalDataSourceId` | reference | ExternalDataSource |

**Data fields in org, missing from ERD (10):**

- *boolean*: `IsArchived`
- *datetime*: `AvailabilityDate`, `DiscontinuedDate`, `EndOfLifeDate`, `LastReferencedDate`, `LastViewedDate`
- *picklist*: `ProductClass`
- *string*: `ExternalId`, `Name`
- *textarea*: `HelpText`

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

### BindingObjectRateCardEntry
Domain: Rate Management | ERD fields: 6 | Org fields: 15

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `RateCardEntryId` | reference | RateCardEntry |
| `RateCardId` | reference | RateCard |
| `RateUnitOfMeasureId` | reference | UnitOfMeasure |
| `SourceAssetId` | reference | Asset |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (5):**

- *datetime*: `EffectiveTo`, `LastReferencedDate`, `LastViewedDate`
- *double*: `NegotiatedRate`
- *picklist*: `RateCardType`

**ERD fields not found in org (1):**

- `UpperBound`

### OmniProcess
Domain: Product Catalog Management | ERD fields: 23 | Org fields: 33

**Data fields in org, missing from ERD (10):**

- *boolean*: `IsActive`, `IsIntegProcdSignatureAvl`, `IsManagedUsingStdDesigner`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `DiscoveryFrameworkUsageType`
- *string*: `Name`
- *textarea*: `CustomHtmlTemplates`, `IntegrationProcedureInput`, `IntegrationProcedureOutput`

### CreditMemo
Domain: Billing | ERD fields: 40 | Org fields: 44

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillingProfileId` | reference | BillingAccount |

**Data fields in org, missing from ERD (8):**

- *currency*: `TotalChargeAmountWithTax`, `TotalChargeTaxAmount`, `TotalCreditAmountApplied`, `TotalCreditAmountUnapplied`, `TotalTaxAmount`, `TotalTaxesCapturedAtHeader`
- *picklist*: `TaxLocaleType`
- *string*: `Description`

**ERD fields not found in org (4):**

- `Name`
- `ProductRelationshipTypeId`
- `Set`
- `Voided`

### CreditMemoAddressGroup
Domain: Billing | ERD fields: 8 | Org fields: 13

**Data fields in org, missing from ERD (9):**

- *datetime*: `LastViewedDate`
- *double*: `Latitude`, `Longitude`
- *picklist*: `GeocodeAccuracy`
- *string*: `City`, `Country`, `PostalCode`, `State`
- *textarea*: `Street`

**ERD fields not found in org (4):**

- `TotalChargeAmountWithTax`
- `TotalChargeTaxAmount`
- `TotalTaxAmount`
- `TotalTaxesCapturedAtHeader`

### PaymentBatchRun
Domain: Billing | ERD fields: 7 | Org fields: 14

**Data fields in org, missing from ERD (9):**

- *datetime*: `LastViewedDate`, `StartTime`
- *int*: `TotalFailedScheduleItems`, `TotalFilteredScheduleItems`, `TotalProcessedScheduleItems`, `TotalScheduleItemsApplied`, `TotalScheduleItemsApplyFailed`
- *picklist*: `Status`
- *string*: `PaymentBatchRunNumber`

**ERD fields not found in org (2):**

- `TotalLiabilitiesAmount`
- `TotalRevenueAmount`

### TaxRate
Domain: Billing (Core Object) | ERD fields: 13 | Org fields: 19

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `GeoCountryId` | reference | GeoCountry |
| `GeoStateId` | reference | GeoState |

**Data fields in org, missing from ERD (7):**

- *date*: `StartDate`
- *double*: `Rate`
- *int*: `Priority`
- *picklist*: `RateUsageType`
- *string*: `State`, `TaxCode`, `ZipCode`

**ERD fields not found in org (1):**

- `LegalEntity`

### CustomPermission
Domain: Transaction Management | ERD fields: 0 | Org fields: 8

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ExternalClientApplicationId` | reference | ExternalClientApplication |

**Data fields in org, missing from ERD (7):**

- *boolean*: `IsLicensed`, `IsProtected`
- *picklist*: `Language`
- *string*: `DeveloperName`, `MasterLabel`, `NamespacePrefix`
- *textarea*: `Description`

### DebitMemoAddress
Domain: Billing | ERD fields: 5 | Org fields: 13

**Data fields in org, missing from ERD (8):**

- *double*: `Latitude`, `Longitude`
- *picklist*: `GeocodeAccuracy`
- *string*: `City`, `Country`, `PostalCode`, `State`
- *textarea*: `Street`

### DebitMemoLine
Domain: Billing | ERD fields: 23 | Org fields: 31

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ShipFromAddressId` | reference | DebitMemoAddress |

**Data fields in org, missing from ERD (7):**

- *currency*: `LineAmount`, `TaxAmount`
- *date*: `TaxEffectiveDate`
- *double*: `CorpCurrencyCnvTotalTaxAmt`
- *picklist*: `CalculationStatus`
- *string*: `Description`, `TaxDocumentNumber`

### FulfillmentAsset
Domain: Dynamic Revenue Orchestrator | ERD fields: 2 | Org fields: 9

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProductId` | reference | Product2 |
| `UnitOfMeasureId` | reference | UnitOfMeasure |

**Data fields in org, missing from ERD (6):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `Quantity`
- *picklist*: `Status`
- *string*: `Name`, `ScopeIdentifierText`

**ERD fields not found in org (1):**

- `Lookup`

### InvoiceAddressGroup
Domain: Billing | ERD fields: 5 | Org fields: 11

**Data fields in org, missing from ERD (8):**

- *double*: `Latitude`, `Longitude`
- *picklist*: `GeocodeAccuracy`
- *string*: `City`, `Country`, `PostalCode`, `State`
- *textarea*: `Street`

**ERD fields not found in org (2):**

- `WriteOffTotalChargeAmount`
- `WriteOffTotalTaxAmount`

### LegalEntity
Domain: Billing | ERD fields: 10 | Org fields: 17

**Data fields in org, missing from ERD (8):**

- *address*: `LegalEntityAddress`
- *boolean*: `ShouldAttachInvoiceDocToEmail`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `LegalEntityLatitude`, `LegalEntityLongitude`
- *picklist*: `LegalEntityGeocodeAccuracy`
- *string*: `Name`

### PaymentScheduleTreatmentDtl
Domain: Billing | ERD fields: 7 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentScheduleTreatmentId` | reference | PaymentScheduleTreatment |
| `PymtSchdDistributionMethodId` | reference | PymtSchdDistributionMethod |

**Data fields in org, missing from ERD (6):**

- *datetime*: `LastViewedDate`
- *picklist*: `PaymentMethodSelectionType`, `PaymentRunMatchingValue`, `ProcessingDateReference`
- *string*: `PaymentScheduleTreatmentDetailNumber`
- *textarea*: `Description`

**ERD fields not found in org (3):**

- `Inactive`
- `Status`
- `TriggerSource`

### ProductComponentGrpOverride
Domain: Product Catalog Management | ERD fields: 0 | Org fields: 8

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `OverrideContextId` | reference | Product2, Promotion |
| `ProductComponentGroupId` | reference | ProductComponentGroup |

**Data fields in org, missing from ERD (6):**

- *boolean*: `IsExcluded`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *int*: `MaxBundleComponents`, `MinBundleComponents`
- *string*: `Name`

### TaxEngine
Domain: Billing | ERD fields: 14 | Org fields: 21

**Data fields in org, missing from ERD (8):**

- *double*: `TaxEngineLatitude`, `TaxEngineLongitude`
- *picklist*: `Type`
- *string*: `TaxEngineCity`, `TaxEnginePostalCode`, `TaxEngineState`, `TaxPrvdAccountIdentifier`
- *textarea*: `TaxEngineStreet`

**ERD fields not found in org (1):**

- `Inactive`

### ContractItemPriceAdjTier
Domain: Transaction Management | ERD fields: 1 | Org fields: 8

**Data fields in org, missing from ERD (7):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *double*: `LowerBound`, `TierValue`, `UpperBound`
- *picklist*: `TierType`
- *string*: `Name`

### FulfillmentStepDefinition
Domain: Dynamic Revenue Orchestrator | ERD fields: 21 | Org fields: 27

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ExecuteOnRuleId` | reference | ExpressionSet, Ruleset |
| `RunAsUserId` | reference | User |

**Data fields in org, missing from ERD (5):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`
- *textarea*: `ExecuteOnConditionData`, `ResumeOnConditionData`

**ERD fields not found in org (1):**

- `Lookup`

### IndexRate
Domain: Salesforce Pricing | ERD fields: 3 | Org fields: 9

**Data fields in org, missing from ERD (7):**

- *boolean*: `IsActive`
- *date*: `ValidEndDate`, `ValidStartDate`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *percent*: `Rate`
- *string*: `Name`

**ERD fields not found in org (1):**

- `Resources`

### OrderItemGroup
Domain: Transaction Management | ERD fields: 48 | Org fields: 22

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `OrderId` | reference | Order |

**Data fields in org, missing from ERD (6):**

- *currency*: `SummarySubtotal`
- *int*: `SortOrder`
- *picklist*: `RLM_RampMode__c`, `Type`
- *string*: `Description`, `Name`

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

### PaymentSchedule
Domain: Billing | ERD fields: 16 | Org fields: 21

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentScheduleTreatmentDtlId` | reference | PaymentScheduleTreatmentDtl |

**Data fields in org, missing from ERD (6):**

- *currency*: `AvailableRequestedAmount`, `TotalPaymentsReceived`, `TotalProcessedAmount`, `TotalRequestedAmount`
- *picklist*: `Type`, `UsageType`

**ERD fields not found in org (1):**

- `Name`

### PricingAPIExecution
Domain: Salesforce Pricing | ERD fields: 2 | Org fields: 8

**Data fields in org, missing from ERD (7):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `ApiType`, `Status`
- *string*: `ExecutionKey`, `Name`, `ReferenceKey`

**ERD fields not found in org (1):**

- `TargetRecord`

### UsageEntitlementBucket
Domain: Usage Management | ERD fields: 11 | Org fields: 16

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ParentId` | reference | UsageEntitlementAccount, UsageEntitlementBucket |
| `TransactionUsageEntitlementId` | reference | TransactionUsageEntitlement |
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (4):**

- *double*: `ProvisionalBucketBalance`, `TotalAsOfBalance`, `TotalConsumedEntitlement`, `TotalProvisionalBalance`

**ERD fields not found in org (1):**

- `ProductId`

### Asset
Domain: Transaction Management | ERD fields: 72 | Org fields: 57

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BindingInstanceTargetId` | reference | Account, Asset, BindingObjectCustomExt, Contract |
| `CurrentQuantityUnitId` | reference | UnitOfMeasure |

**Data fields in org, missing from ERD (4):**

- *boolean*: `DoesAutomaticallyRenew`
- *date*: `ManufactureDate`
- *percent*: `UnitPriceUplift`
- *textarea*: `Description`

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

### CollectionPlanItem
Domain: Billing (Core Object) | ERD fields: 1 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `CollectionPlanId` | reference | CollectionPlan |
| `InvoiceId` | reference | Invoice |

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `Status`
- *string*: `Name`

### FulfillmentStep
Domain: Dynamic Revenue Orchestrator | ERD fields: 40 | Org fields: 39

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `TaskId` | reference | Task |

**Data fields in org, missing from ERD (5):**

- *boolean*: `IsVisibleByExternalUsers`
- *datetime*: `LastViewedDate`
- *picklist*: `UsageType`
- *string*: `CustomBaseExecutionDate`, `StepDefIdentifier`

**ERD fields not found in org (6):**

- `Lookup`
- `Minutes`
- `RequestedCompletionDate`
- `RequestedStartDate`
- `RoundRobin`
- `Skipped`

### FulfillmentTaskAssignmentRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 6 | Org fields: 10

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `SourceId` | reference | Group |

**Data fields in org, missing from ERD (5):**

- *datetime*: `LastViewedDate`
- *int*: `Priority`
- *picklist*: `TaskAllocationType`, `UsageType`
- *string*: `Name`

**ERD fields not found in org (2):**

- `StepId`
- `VersionGroupIdentifier`

### OrderItemAttribute
Domain: Transaction Management | ERD fields: 3 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AttributePicklistValueId` | reference | AttributePicklistValue |
| `OrderItemId` | reference | OrderItem |

**Data fields in org, missing from ERD (4):**

- *boolean*: `IsPriceImpacting`
- *string*: `AttributeName`, `AttributeValue`, `ExternalId`

**ERD fields not found in org (2):**

- `Lookup`
- `ShippingCarrierMethod`

### AccountBillingAccount
Domain: Billing (Core Object) | ERD fields: 2 | Org fields: 6

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `BillingAccountId` | reference | BillingAccount |

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

**ERD fields not found in org (1):**

- `Account`

### AssessmentQuestion
Domain: Product Catalog Management | ERD fields: 11 | Org fields: 13

**Data fields in org, missing from ERD (5):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `FormulaResponseDataType`
- *string*: `Name`, `Namespace`

**ERD fields not found in org (2):**

- `ShouldExcludeFromMetadata`
- `ShouldHideInDesigner`

### BillingMilestonePlan
Domain: Billing | ERD fields: 6 | Org fields: 10

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AccountId` | reference | Account |
| `ReferenceItemId` | reference | BillingSchedule, OrderItem, QuoteLineItem |

**Data fields in org, missing from ERD (3):**

- *currency*: `ReferenceItemAmount`
- *picklist*: `Status`
- *string*: `Description`

**ERD fields not found in org (1):**

- `Value`

### FulfillmentAssetAttribute
Domain: Dynamic Revenue Orchestrator | ERD fields: 1 | Org fields: 6

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `AttributePicklistValueId` | reference | AttributePicklistValue |
| `FulfillmentAssetId` | reference | FulfillmentAsset |

**Data fields in org, missing from ERD (3):**

- *string*: `AttributeName`, `AttributeValue`, `ExternalId`

### PaymentScheduleTreatment
Domain: Billing | ERD fields: 7 | Org fields: 9

**Data fields in org, missing from ERD (5):**

- *boolean*: `IsApprovalRequired`
- *picklist*: `Status`, `TriggerSource`
- *textarea*: `Description`, `PaymentPlanTag`

**ERD fields not found in org (2):**

- `Inactive`
- `TreatmentSelection`

### RevenueTransactionErrorLog
Domain: Billing | ERD fields: 12 | Org fields: 15

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `BillingScheduleGroupId` | reference | BillingScheduleGroup |

**Data fields in org, missing from ERD (4):**

- *picklist*: `Severity`
- *string*: `PrimaryTextRecord`
- *textarea*: `ConfiguratorErrorMessage`, `Request`

**ERD fields not found in org (2):**

- `Days`
- `InvoiceLineTax`

### AssessmentQuestionSet
Domain: Product Catalog Management | ERD fields: 2 | Org fields: 6

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`, `Namespace`

### AssessmentQuestionVersion
Domain: Product Catalog Management | ERD fields: 15 | Org fields: 17

**Data fields in org, missing from ERD (4):**

- *datetime*: `ActivationDateTime`, `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

**ERD fields not found in org (1):**

- `ExternalAsmtContentVersion`

### AssetRelationship
Domain: Transaction Management | ERD fields: 14 | Org fields: 15

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProductRelatedComponentId` | reference | ProductRelatedComponent |

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`, `ToDate`

**ERD fields not found in org (2):**

- `ProductRelatedComponent`
- `UsageResourceId`

### AssetStatePeriod
Domain: Transaction Management | ERD fields: 18 | Org fields: 19

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PriceRevisionPolicyId` | reference | PriceRevisionPolicy |

**Data fields in org, missing from ERD (3):**

- *currency*: `UnitPrice`
- *datetime*: `StartDate`
- *percent*: `UnitPriceUplift`

**ERD fields not found in org (3):**

- `Lookup`
- `PriceRevisionPolicy`
- `UserOrGroupId`

### DocumentClauseSet
Domain: Transaction Management | ERD fields: 3 | Org fields: 7

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *picklist*: `Category`
- *string*: `Name`

### InvoiceBatchRun
Domain: Billing | ERD fields: 31 | Org fields: 30

**Data fields in org, missing from ERD (4):**

- *int*: `TotalInvoicesCanceled`, `TotalInvoicesFailed`, `TotalInvoicesGenerated`, `TotalPostedInvoices`

**ERD fields not found in org (4):**

- `Address`
- `InvoiceAddressGroupNumber`
- `InvoiceId`
- `NotApplicable`

### ObjectStateActionDefinition
Domain: Transaction Management | ERD fields: 5 | Org fields: 9

**Data fields in org, missing from ERD (4):**

- *boolean*: `IsSystem`
- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ObjectStateDefinition
Domain: Transaction Management | ERD fields: 7 | Org fields: 11

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`
- *textarea*: `Description`

### ObjectStateValue
Domain: Transaction Management | ERD fields: 4 | Org fields: 8

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `CustomPermissionId` | reference | CustomPermission |

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### OrderItemDetail
Domain: Transaction Management | ERD fields: 11 | Org fields: 14

**Data fields in org, missing from ERD (4):**

- *currency*: `TotalLineAmount`, `TotalPrice`, `UnitPrice`
- *string*: `ReferenceNumber`

**ERD fields not found in org (1):**

- `IsPriceImpacting`

### PaymentRetryRule
Domain: Billing | ERD fields: 12 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentRetryRuleSetId` | reference | PaymentRetryRuleSet |

**Data fields in org, missing from ERD (3):**

- *picklist*: `RetryIntervalType`
- *string*: `Description`, `PaymentRetryRuleNumber`

**ERD fields not found in org (4):**

- `Minutes`
- `Unapplied`
- `UnappliedDateTime`
- `UnappliedStatus`

### PaymentScheduleItem
Domain: Billing | ERD fields: 23 | Org fields: 27

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PaymentScheduleId` | reference | PaymentSchedule |

**Data fields in org, missing from ERD (3):**

- *boolean*: `IsRetriableAsSameRequest`
- *int*: `MaximumRetryCount`
- *picklist*: `UsageType`

### ProductCatalog
Domain: Product Catalog Management | ERD fields: 5 | Org fields: 9

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *int*: `NumberOfCategories`
- *string*: `Name`

### ProductClassificationAttr
Domain: Product Catalog Management | ERD fields: 21 | Org fields: 25

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `OverriddenInheritedAttributeId` | reference | ProductClassificationAttr |

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductConfigFlowAssignment
Domain: Product Configurator | ERD fields: 6 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProductId` | reference | Product2 |

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

**ERD fields not found in org (3):**

- `FlowIdentifier`
- `IsDefault`
- `Status`

### ProductConfigurationRule
Domain: Product Configurator | ERD fields: 11 | Org fields: 13

**Data fields in org, missing from ERD (4):**

- *int*: `Sequence`
- *picklist*: `RuleType`, `Status`
- *string*: `Description`

**ERD fields not found in org (1):**

- `ProductId`

### QuoteLineDetail
Domain: Transaction Management | ERD fields: 10 | Org fields: 14

**Data fields in org, missing from ERD (4):**

- *currency*: `TotalLineAmount`, `TotalPrice`, `UnitPrice`
- *string*: `ReferenceNumber`

### QuoteLineGroup
Domain: Transaction Management | ERD fields: 24 | Org fields: 23

**Data fields in org, missing from ERD (4):**

- *percent*: `RLM_UpliftPercent__c`
- *picklist*: `RLM_RampMode__c`, `Type`
- *string*: `Description`

**ERD fields not found in org (5):**

- `ReferenceNumber`
- `TotalLineAmount`
- `TotalPrice`
- `UnitPrice`
- `Yearly`

### RateAdjustmentByAttribute
Domain: Rate Management | ERD fields: 14 | Org fields: 18

**Data fields in org, missing from ERD (4):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *int*: `AttributeCount`
- *string*: `AttributeAdjConditionsHash`

### UsageRatableSumCmtAssetRt
Domain: Usage Management | ERD fields: 6 | Org fields: 9

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageRatableSummaryId` | reference | UsageRatableSummary |

**Data fields in org, missing from ERD (3):**

- *datetime*: `RatingDecisionDateTime`
- *double*: `NetUnitRate`
- *string*: `Name`

**ERD fields not found in org (1):**

- `UsageResourceId`

### AssessmentQuestionAssignment
Domain: Product Catalog Management | ERD fields: 2 | Org fields: 5

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### AssetActionSource
Domain: Transaction Management | ERD fields: 34 | Org fields: 35

**Data fields in org, missing from ERD (3):**

- *currency*: `TotalPrice`, `UnitPrice`
- *datetime*: `TransactionDate`

**ERD fields not found in org (2):**

- `LastDayOfPeriod`
- `Lookup`

### AttributeCategoryAttribute
Domain: Product Catalog Management | ERD fields: 2 | Org fields: 5

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### BillingMilestonePlanItem
Domain: Billing | ERD fields: 22 | Org fields: 20

**Data fields in org, missing from ERD (3):**

- *double*: `MilestoneAmountDerived`
- *picklist*: `Type`
- *string*: `Description`

**ERD fields not found in org (5):**

- `Event`
- `OrderProductActivation`
- `ReferenceItemAmount`
- `ReferenceItemId`
- `Years`

### BillingTreatmentItem
Domain: Billing | ERD fields: 16 | Org fields: 18

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ChannelProgram
Domain: Transaction Management (Core Object) | ERD fields: 3 | Org fields: 6

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ChannelProgramLevel
Domain: Transaction Management (Core Object) | ERD fields: 4 | Org fields: 7

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ChannelProgramMember
Domain: Transaction Management (Core Object) | ERD fields: 3 | Org fields: 6

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### CostBookEntry
Domain: Salesforce Pricing | ERD fields: 9 | Org fields: 9

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

**ERD fields not found in org (2):**

- `SellingModelType`
- `StartDate`

### CreditMemoInvApplication
Domain: Billing | ERD fields: 14 | Org fields: 15

**Data fields in org, missing from ERD (3):**

- *datetime*: `UnappliedDate`
- *picklist*: `Type`
- *string*: `Description`

**ERD fields not found in org (2):**

- `LastViewedDate`
- `Yes`

### ObjectStateTransition
Domain: Transaction Management | ERD fields: 5 | Org fields: 8

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ObjectStateTransitionAction
Domain: Transaction Management | ERD fields: 5 | Org fields: 8

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### OmniProcessAsmtQuestionVer
Domain: Product Catalog Management | ERD fields: 4 | Org fields: 7

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### OmniProcessElement
Domain: Product Catalog Management | ERD fields: 15 | Org fields: 18

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### PriceAdjustmentSchedule
Domain: Salesforce Pricing | ERD fields: 10 | Org fields: 11

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ContractId` | reference | Contract |

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

### ProdtAttrScope
Domain: Product Catalog Management | ERD fields: 2 | Org fields: 5

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductCategoryDisqual
Domain: Product Catalog Management | ERD fields: 5 | Org fields: 8

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductCategoryQualification
Domain: Product Catalog Management | ERD fields: 4 | Org fields: 7

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductClassification
Domain: Product Catalog Management | ERD fields: 3 | Org fields: 6

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductComponentGroup
Domain: Product Catalog Management | ERD fields: 7 | Org fields: 10

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductDecompEnrichmentRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 15 | Org fields: 18

**Data fields in org, missing from ERD (3):**

- *picklist*: `SourceType`
- *string*: `SourceAttributeIdentifier`, `SourceContextTag`

### ProductDisqualification
Domain: Product Catalog Management | ERD fields: 7 | Org fields: 10

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductQualification
Domain: Product Catalog Management | ERD fields: 6 | Org fields: 9

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ProductRampSegment
Domain: Salesforce Pricing | ERD fields: 5 | Org fields: 8

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### TaxEngineInteractionLog
Domain: Billing | ERD fields: 22 | Org fields: 21

**Data fields in org, missing from ERD (3):**

- *base64*: `ResponseBody`
- *string*: `TaxEngineInteractionLogNumber`
- *textarea*: `Description`

**ERD fields not found in org (4):**

- `TaxPrvdAccountIdentifier`
- `ValidationError`
- `Void`
- `VoidOrDebit`

### UsageResourceBillingPolicy
Domain: Usage Management | ERD fields: 4 | Org fields: 7

**Data fields in org, missing from ERD (3):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`
- *string*: `Name`

### ApprovalSubmission
Domain: Advanced Approvals | ERD fields: 21 | Org fields: 11

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `SmartApprvlBasisSubmissionId` | reference | ApprovalSubmission |

**Data fields in org, missing from ERD (1):**

- *boolean*: `IsSmartApprovalRun`

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

### AssetRateAdjustment
Domain: Transaction Management | ERD fields: 6 | Org fields: 6

**Data fields in org, missing from ERD (2):**

- *double*: `LowerBound`, `UpperBound`

**ERD fields not found in org (2):**

- `GroupId`
- `UserOrGroupId`

### BillingBatchScheduler
Domain: Billing | ERD fields: 23 | Org fields: 23

**Data fields in org, missing from ERD (2):**

- *boolean*: `ShouldRunDpeOnCore`
- *picklist*: `TimeZone`

**ERD fields not found in org (1):**

- `Saturday`

### BillingPeriodItem
Domain: Billing | ERD fields: 14 | Org fields: 16

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UnitOfMeasureId` | reference | UnitOfMeasure |

**Data fields in org, missing from ERD (1):**

- *double*: `TotalUsedQuantity`

### BindingObjectRateAdjustment
Domain: Rate Management | ERD fields: 6 | Org fields: 8

**Data fields in org, missing from ERD (2):**

- *double*: `UpperBound`
- *string*: `Name`

### CreditMemoLineInvoiceLine
Domain: Billing | ERD fields: 19 | Org fields: 16

**Data fields in org, missing from ERD (2):**

- *picklist*: `Type`
- *textarea*: `Description`

**ERD fields not found in org (5):**

- `StartDate`
- `Status`
- `TaxAmount`
- `TaxTreatmentId`
- `Unapplied`

### FulfillmentPlan
Domain: Dynamic Revenue Orchestrator | ERD fields: 9 | Org fields: 9

**Data fields in org, missing from ERD (2):**

- *picklist*: `State`, `UsageType`

**ERD fields not found in org (1):**

- `Bulk`

### FulfillmentStepSource
Domain: Dynamic Revenue Orchestrator | ERD fields: 3 | Org fields: 5

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `StepId` | reference | FulfillmentStep |

**Data fields in org, missing from ERD (1):**

- *string*: `VersionGroupIdentifier`

### InvoiceBatchRunCriteria
Domain: Billing | ERD fields: 13 | Org fields: 10

**Data fields in org, missing from ERD (2):**

- *date*: `TargetDate`
- *int*: `TargetDateOffset`

**ERD fields not found in org (4):**

- `TotalInvoicesCanceled`
- `TotalInvoicesFailed`
- `TotalInvoicesGenerated`
- `TotalPostedInvoices`

### InvoiceBatchRunRecovery
Domain: Billing | ERD fields: 8 | Org fields: 8

**Data fields in org, missing from ERD (2):**

- *datetime*: `StartTime`
- *picklist*: `Status`

**ERD fields not found in org (2):**

- `TargetDate`
- `TargetDateOffset`

### LegalEntyAccountingPeriod
Domain: Billing | ERD fields: 14 | Org fields: 12

**Data fields in org, missing from ERD (2):**

- *currency*: `TotalLiabilitiesAmount`, `TotalRevenueAmount`

**ERD fields not found in org (3):**

- `CreateUnrealizedGainOrLossTransactionJournals`
- `Reopened`
- `ShouldAttachInvoiceDocToEmail`

### OrderDeliveryMethod
Domain: Transaction Management | ERD fields: 11 | Org fields: 10

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ShippingCarrierMethodId` | reference | ShippingCarrierMethod |

**Data fields in org, missing from ERD (1):**

- *textarea*: `Description`

**ERD fields not found in org (2):**

- `NewValue`
- `OldValue`

### OrderItemUsageRsrcGrant
Domain: Transaction Management | ERD fields: 9 | Org fields: 11

**Data fields in org, missing from ERD (2):**

- *int*: `ValidityPeriodTerm`
- *picklist*: `ValidityPeriodUnit`

### OrderItemUsageRsrcPlcy
Domain: Transaction Management | ERD fields: 10 | Org fields: 9

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageOveragePolicyId` | reference | UsageOveragePolicy |
| `UsageResourceId` | reference | UsageResource |

**ERD fields not found in org (3):**

- `GrantedLast`
- `ValidityPeriodTerm`
- `ValidityPeriodUnit`

### PaymentSchedulePolicy
Domain: Billing | ERD fields: 11 | Org fields: 8

**Data fields in org, missing from ERD (2):**

- *picklist*: `TreatmentSelection`
- *textarea*: `Description`

**ERD fields not found in org (4):**

- `TotalPaymentsReceived`
- `TotalProcessedAmount`
- `TotalRequestedAmount`
- `UsageType`

### PriceBookEntryDerivedPrice
Domain: Salesforce Pricing | ERD fields: 13 | Org fields: 13

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

### PriceRevisionPolicy
Domain: Salesforce Pricing | ERD fields: 7 | Org fields: 8

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

### ProcedurePlanCriterion
Domain: Salesforce Pricing | ERD fields: 7 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProcedurePlanOptionId` | reference | ProcedurePlanOption |

**Data fields in org, missing from ERD (1):**

- *int*: `Sequence`

**ERD fields not found in org (2):**

- `NotIn`
- `ProrationPolicyId`

### ProdtDecompEnrchVarMap
Domain: Dynamic Revenue Orchestrator | ERD fields: 8 | Org fields: 7

**Data fields in org, missing from ERD (2):**

- *picklist*: `VariableType`
- *string*: `Name`

**ERD fields not found in org (3):**

- `SourceAttributeIdentifier`
- `SourceContextTag`
- `SourceType`

### ProductConfigurationFlow
Domain: Product Configurator | ERD fields: 10 | Org fields: 6

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

**ERD fields not found in org (5):**

- `AssignmentType`
- `Lookup`
- `ProductClassificationId`
- `ProductConfigurationFlowId`
- `ReferenceObjectId`

### ProductFulfillmentScenario
Domain: Dynamic Revenue Orchestrator | ERD fields: 15 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ScenarioRuleId` | reference | Ruleset |

**Data fields in org, missing from ERD (1):**

- *picklist*: `UsageType`

**ERD fields not found in org (4):**

- `FulfillmentProcessId`
- `Lookup`
- `Renew`
- `Type`

### ProductUsageGrant
Domain: Usage Management | ERD fields: 24 | Org fields: 23

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProductId` | reference | Product2 |
| `UsageRsrcId` | reference | UsageResource |

**ERD fields not found in org (2):**

- `ProductOfferId`
- `UsageResourceId`

### QuotLineItmUseRsrcGrant
Domain: Transaction Management | ERD fields: 12 | Org fields: 13

**Data fields in org, missing from ERD (2):**

- *int*: `ValidityPeriodTerm`
- *picklist*: `ValidityPeriodUnit`

**ERD fields not found in org (1):**

- `IsPriceImpacting`

### QuoteLineItemAttribute
Domain: Transaction Management | ERD fields: 5 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `QuoteLineItemId` | reference | QuoteLineItem |

**Data fields in org, missing from ERD (1):**

- *boolean*: `IsPriceImpacting`

### QuoteLineRateAdjustment
Domain: Transaction Management | ERD fields: 5 | Org fields: 6

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `QuoteLineRateCardEntryId` | reference | QuoteLineRateCardEntry |

**Data fields in org, missing from ERD (1):**

- *double*: `UpperBound`

**ERD fields not found in org (1):**

- `Percentage`

### RateCardEntry
Domain: Rate Management | ERD fields: 17 | Org fields: 19

**Data fields in org, missing from ERD (2):**

- *datetime*: `LastReferencedDate`, `LastViewedDate`

### SalesTrxnDeleteEvent
Domain: Dynamic Revenue Orchestrator | ERD fields: 2 | Org fields: 3

**Data fields in org, missing from ERD (2):**

- *string*: `EventUuid`, `ReplayId`

**ERD fields not found in org (1):**

- `UsageType`

### UsageCmtAssetRelatedObj
Domain: Usage Management | ERD fields: 6 | Org fields: 7

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `RelatedObjectId` | reference | Account, Asset, BindingObjectCustomExt, Contract |

**Data fields in org, missing from ERD (1):**

- *string*: `UsageCmtAssetRelatedObjNumber`

**ERD fields not found in org (1):**

- `UsageResourceId`

### UsageEntitlementAccount
Domain: Usage Management | ERD fields: 14 | Org fields: 14

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `PricebookEntryId` | reference | PricebookEntry |
| `ProductId` | reference | Product2 |

**ERD fields not found in org (1):**

- `MONTH`

### UsageEntitlementEntry
Domain: Usage Management | ERD fields: 17 | Org fields: 17

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageSummaryId` | reference | UsageSummary |

**Data fields in org, missing from ERD (1):**

- *picklist*: `TransactionType`

**ERD fields not found in org (2):**

- `Expired`
- `Rollover`

### UsageResourcePolicy
Domain: Usage Management | ERD fields: 6 | Org fields: 8

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageResourceId` | reference | UsageResource |

**Data fields in org, missing from ERD (1):**

- *string*: `UsageResourcePolicyNum`

### ValTfrm
Domain: Dynamic Revenue Orchestrator | ERD fields: 12 | Org fields: 14

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ValueTransformGroupId` | reference | ValTfrmGrp |

**Data fields in org, missing from ERD (1):**

- *date*: `OutputDate`

### ApprovalAlertContentDef
Domain: Approvals | ERD fields: 4 | Org fields: 5

**Data fields in org, missing from ERD (1):**

- *string*: `Name`

### AssessmentQuestionConfig
Domain: Product Catalog Management | ERD fields: 3 | Org fields: 4

**Data fields in org, missing from ERD (1):**

- *string*: `NamespacePrefix`

### AssessmentQuestionSetConfig
Domain: Product Catalog Management | ERD fields: 3 | Org fields: 4

**Data fields in org, missing from ERD (1):**

- *string*: `NamespacePrefix`

### AssetRateCardEntry
Domain: Transaction Management | ERD fields: 13 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `UsageResourceId` | reference | UsageResource |

**ERD fields not found in org (1):**

- `UpperBound`

### AssetStatePeriodAttribute
Domain: Transaction Management | ERD fields: 12 | Org fields: 6

**Data fields in org, missing from ERD (1):**

- *string*: `ExternalId`

**ERD fields not found in org (7):**

- `ItemId`
- `Lookup`
- `Name`
- `StartDate`
- `TagDefinitionId`
- `UnitPrice`
- `UnitPriceUplift`

### AttributeAdjustmentCondition
Domain: Salesforce Pricing | ERD fields: 15 | Org fields: 14

**Data fields in org, missing from ERD (1):**

- *picklist*: `UsageType`

**ERD fields not found in org (2):**

- `Lookup`
- `True`

### BillingArrangementLine
Domain: Billing | ERD fields: 7 | Org fields: 8

**Data fields in org, missing from ERD (1):**

- *double*: `PercentageInternal`

### ContractItemPrice
Domain: Salesforce Pricing | ERD fields: 17 | Org fields: 14

**Data fields in org, missing from ERD (1):**

- *datetime*: `StartDate`

**ERD fields not found in org (3):**

- `AdjustmentPercentage`
- `Lookup`
- `UsageResourceId`

### ContractItemPriceHistory
Domain: Transaction Management | ERD fields: 46 | Org fields: 5

**Data fields in org, missing from ERD (1):**

- *picklist*: `Field`

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

### CreditMemoLineTax
Domain: Billing | ERD fields: 30 | Org fields: 20

**Data fields in org, missing from ERD (1):**

- *string*: `Description`

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

### FulfillmentLineRel
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 9

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ProductRelationshipTypeId` | reference | ProductRelationshipType |

**ERD fields not found in org (2):**

- `ExternalId`
- `FulfillmentOrderLineItemId`

### FulfillmentStepDependency
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 5

**Data fields in org, missing from ERD (1):**

- *picklist*: `PropagateStateToDependentStep`

**ERD fields not found in org (3):**

- `DependencyScope`
- `DependsOnStepDefinitionId`
- `FulfillmentStepDefinitionId`

### GeneralLdgrAcctPrdSummary
Domain: Billing | ERD fields: 8 | Org fields: 9

**Data fields in org, missing from ERD (1):**

- *string*: `Name`

### OrderItemRateAdjustment
Domain: Transaction Management | ERD fields: 10 | Org fields: 6

**Data fields in org, missing from ERD (1):**

- *double*: `UpperBound`

**ERD fields not found in org (5):**

- `Percentage`
- `ReferenceNumber`
- `TotalLineAmount`
- `TotalPrice`
- `UnitPrice`

### PaymentRetryRuleSet
Domain: Billing | ERD fields: 15 | Org fields: 11

**Data fields in org, missing from ERD (1):**

- *string*: `Description`

**ERD fields not found in org (5):**

- `AvailableRequestedAmount`
- `Minutes`
- `PaymentRetryRuleSetId`
- `RetryIntervalType`
- `Staggered`

### PriceBookRateCard
Domain: Rate Management | ERD fields: 5 | Org fields: 6

**Data fields in org, missing from ERD (1):**

- *string*: `Name`

### PricingAdjBatchJobLog
Domain: Salesforce Pricing | ERD fields: 9 | Org fields: 10

**Data fields in org, missing from ERD (1):**

- *string*: `TargetRecord`

### ProductAttributeDefinition
Domain: Product Catalog Management | ERD fields: 27 | Org fields: 27

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `OverrideContextId` | reference | Product2, Promotion |

### ProductCategory
Domain: Product Catalog Management | ERD fields: 10 | Org fields: 10

**Data fields in org, missing from ERD (1):**

- *int*: `NumberOfProducts`

### ProductCategoryProduct
Domain: Product Catalog Management | ERD fields: 10 | Org fields: 6

**Data fields in org, missing from ERD (1):**

- *string*: `ProductToCategory`

**ERD fields not found in org (4):**

- `CategoryId`
- `DisplaySequence`
- `LastReferencedDate`
- `LastViewedDate`

### ProductFulfillmentDecompRule
Domain: Dynamic Revenue Orchestrator | ERD fields: 13 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ExecuteOnRuleId` | reference | Ruleset |

**ERD fields not found in org (1):**

- `VariableType`

### ProductUsageResource
Domain: Usage Management | ERD fields: 11 | Org fields: 10

**Data fields in org, missing from ERD (1):**

- *string*: `ProductUsageResourceNum`

**ERD fields not found in org (2):**

- `ValidityPeriodTerm`
- `ValidityPeriodUnit`

### ProductUsageResourcePolicy
Domain: Usage Management | ERD fields: 8 | Org fields: 9

**Data fields in org, missing from ERD (1):**

- *string*: `ProductUsageResourcePolicyNum`

### PymtSchdDistributionMethod
Domain: Billing | ERD fields: 6 | Org fields: 6

**Data fields in org, missing from ERD (1):**

- *textarea*: `Description`

### QuoteAction
Domain: Transaction Management | ERD fields: 7 | Org fields: 7

**Data fields in org, missing from ERD (1):**

- *picklist*: `Type`

### SalesTransactionFulfillReq
Domain: Dynamic Revenue Orchestrator | ERD fields: 18 | Org fields: 12

**Relationships in org, missing from ERD:**

| Field | Type | References |
|-------|------|------------|
| `ReferenceObjectId` | reference | Order, Quote |

**ERD fields not found in org (6):**

- `Completed`
- `Failed`
- `Freezing`
- `InProgress`
- `NotStarted`
- `Rejected`

### TransactionProcessingType
Domain: Transaction Management | ERD fields: 9 | Org fields: 10

**Data fields in org, missing from ERD (1):**

- *string*: `NamespacePrefix`

### AccountingPeriod
Domain: Billing | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `Open`

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

### AssetFulfillmentDecomp
Domain: Dynamic Revenue Orchestrator | ERD fields: 9 | Org fields: 7

**ERD fields not found in org (1):**

- `SourceLineItem`

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

### BillingPolicy
Domain: Billing | ERD fields: 11 | Org fields: 7

**ERD fields not found in org (4):**

- `Manual`
- `Reviewed`
- `TotalUsedQuantity`
- `UnitOfMeasureId`

### BillingTreatment
Domain: Billing | ERD fields: 14 | Org fields: 10

**ERD fields not found in org (3):**

- `TotalPendingAmount`
- `UsageType`
- `Yes`

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

### CostBook
Domain: Salesforce Pricing | ERD fields: 8 | Org fields: 6

**ERD fields not found in org (1):**

- `Lookup`

### FulfillmentAssetRelationship
Domain: Dynamic Revenue Orchestrator | ERD fields: 7 | Org fields: 6

**ERD fields not found in org (1):**

- `FulfillmentAssetId`

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

### FulfillmentLineSourceRel
Domain: Dynamic Revenue Orchestrator | ERD fields: 12 | Org fields: 8

**ERD fields not found in org (3):**

- `NoChange`
- `ProductRelationshipTypeId`
- `SourceLineItem`

### FulfillmentStepDefinitionGroup
Domain: Dynamic Revenue Orchestrator | ERD fields: 6 | Org fields: 4

**ERD fields not found in org (1):**

- `ContextBased`

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

### InvBatchDraftToPostedRun
Domain: Billing | ERD fields: 17 | Org fields: 13

**ERD fields not found in org (4):**

- `GeneralLedgerAcctAsgntRuleId`
- `NotApplicable`
- `Percentage`
- `TransactionAmountField`

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

### OrderItemRateCardEntry
Domain: Transaction Management | ERD fields: 9 | Org fields: 8

**ERD fields not found in org (1):**

- `UpperBound`

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

### PricingAdjBatchJob
Domain: Salesforce Pricing | ERD fields: 21 | Org fields: 14

**ERD fields not found in org (6):**

- `Amount`
- `Override`
- `Percentage`
- `PricebookEntry`
- `Region`
- `Rerun`

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

### SalesTransactionType
Domain: Transaction Management | ERD fields: 6 | Org fields: 3

**ERD fields not found in org (2):**

- `UsageOveragePolicyId`
- `UsageResourceId`

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

### UsageCommitmentPolicy
Domain: Usage Management | ERD fields: 5 | Org fields: 4

**ERD fields not found in org (1):**

- `RelatedObjectId`

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

### UsageResource
Domain: Usage Management | ERD fields: 14 | Org fields: 12

**ERD fields not found in org (1):**

- `Inactive`

### ValTfrmGrp
Domain: Dynamic Revenue Orchestrator | ERD fields: 10 | Org fields: 8

**ERD fields not found in org (1):**

- `Text`

## Complete Objects (11)

These objects have no gaps between ERD and org:

- `BindingObjectCustomExt` (4 fields)
- `ClauseCatgConfiguration` (6 fields)
- `CurrencyType` (5 fields)
- `ExpressionSetConstraintObj` (8 fields)
- `FulfillmentWorkspace` (4 fields)
- `FulfillmentWorkspaceItem` (5 fields)
- `GeneralLedgerJrnlEntryRule` (7 fields)
- `OmniScriptConfig` (3 fields)
- `PriceBookEntry` (11 fields)
- `PricingProcessExecution` (10 fields)
- `TaxTreatment` (13 fields)
