---
page_id: sforce_api_objects_revenuetransactionerrorlog.htm
title: RevenueTransactionErrorLog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_revenuetransactionerrorlog.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RevenueTransactionErrorLog

Represents the details of errors that occurred during the processing of a
request. The error record persists until a new error with the same category, primary
record, and, if necessary, related record occurs. This object is available in API
version 62.0 and later.

## Supported Calls

`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`

## Special Access Rules

You need the Billing Operations User permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AsyncOperationTrackerId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the async operation tracker record created by the request. Async operation tracker records contain information about the status of the asynchronous process initiated by the request.  This field is a relationship field.  Relationship Name  AsyncOperationTracker  Refers To  AsyncOperationTracker |
| BillingScheduleGroupId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the group related to the billing schedule with errors. This field is available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  BillingScheduleGroup  Refers To  BillingScheduleGroup |
| Category | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the context of the source of error.  Valid values are:  - `ApplyAPI` - AutomatedNegativeInvoiceLineConversion - AutomaticRefunds - `ConvertNegativeInvoiceLineToCredit`—Available   in API version 56.0 and later. - `Core Invoice Generation   Failure` - `CreditInvoiceAPI` - `CreditMemoRecoveryApi`—Available in API   version 66.0 and later. - `CreditTaxIntegrationAPI` - `BulkCurrencyConversion`—Available in API   version 66.0 and later. - `InitiateAmendment`—Available in API version   56.0 and later. - `InitiateCancel` - `InitiateRenewal` - `InsufficientAccess`—Insufficient Access to   start invoice run. - `InvoiceBatchRun` - `InvoiceBatchRunDebitConversion`—Available   in API version 66.0 and later. - `InvoiceBatchRunInvoiceGeneration` - `InvoiceBatchRunPostProcessor` - `InvoiceBatchRunPreProcessor` - `InvoiceBatchRunRecovery` - `InvoiceBatchRunSelectionStep` - `InvoiceBatchRunSplitInvoiceGeneration`—Available   in API version 66.0 and later. - `InvoiceBatchRunSummarizer` - `InvoiceBatchRunTaxProcessor` - `MaterialLineGeneration`—Available in API   version 58.0 and later. - `Invalid Tax API   Input` - `Invalid Tax Integration   Input` - `LoadSalesRecipientData`—Available in API   version 66.0 and later. - `OrderTaxCalculationFailure`—Available in   API version 61.0 and later. - `OrderToAsset` - `OrderItemToAsset`—Available in API version   59.0 and later. - `OrderToBillingSchedule` - `PaymentSale` - `PaymentScheduleGeneration`—Available in   API version 56.0 and later. - `ProcessAutoQuote`—Available in API version   66.0 and later. - `PstBaseStepFailure`—Available in API version   66.0 and later. - `QuotePriceCalculationFailure`—Available in   API version 61.0 and later. - `QuoteTaxCalculationFailure`—Available in   API version 61.0 and later. - `QuoteToOrder`—Available in API version 56.0   and later. - `Post Tax API   Failure` - `Post-Credit Tax   Failure` - `Pre-Credit Tax   Failure` - `SetupEnergyAgreement`—Available in API   version 66.0 and later. - `StandaloneCreditAPI` - `StatementOfAccountGeneration`—Available in   API version 66.0 and later. - `Tax API Failure` - `TransactionToContract`—Available in API   version 59.0 and later. - `Unknown   Failure`—Available in API version 56.0 and   later. - `VoidCreditMemo`—Available in API version 66.0   and later. - `VoidPostedInvoiceAPI` |
| ConfiguratorErrorMessage | Type  textarea  Properties  Nillable  Description  The text of the error message. This field is available in API version 66.0 and later. |
| ErrorCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The error code shown during the request processing, such as INVALID\_INPUT. |
| ErrorLogNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. An auto-generated unique ID that identifies the error. |
| ErrorMessage | Type  textarea  Properties  Create  Description  This field contains information about the error and how to resolve it. |
| OwnerId | Type  reference  Properties  Filter, Group, Sort  Description  Required. The ID of the user who made the request that resulted in the creation of the error log.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| PrimaryRecord2Id | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the record that’s associated with this error. For example, if the error occurred while creating an invoice line from an order line, the primary2 ID is the ID of the order line. This field is available in API version 66.0 and later.  This field is a polymorphic relationship field.  Relationship Name  PrimaryRecord2  Refers To  Account, CreditMemoInvApplication, CreditMemoLine, CreditMemoLineInvoiceLine, CreditMemoLineTax, DebitMemo, DebitMemoLine, InvoiceLine, InvoiceLineTax, LegalEntyAccountingPeriod, Order, PaymentLineInvoice, PaymentLineInvoiceLine, RefundLinePayment |
| PrimaryRecordId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the record that’s associated with this error. For example, if the error occurred while creating an invoice from an order, the primary ID is the ID of the order.  This field is a polymorphic relationship field.  Relationship Name  PrimaryRecord  Refers To  Asset, AsyncOperationTracker, BillingBatchScheduler, BillingSchedule, CreditMemo, InvBatchDraftToPostedRun, Invoice, InvoiceBatchRun, InvoiceBatchRunRecovery, Order, OrderItem, RevenueAsyncOperation, RuleLibraryVersion |
| PrimaryTextRecord | Type  string  Properties  Create, Filter, Group, Nillable, Sort  Description  The identifier of the primary record associated with the error log. For example, if the error occurred while creating an invoice from an order, the primary text Record ID is the ID of the order.  There are two other fields in the same entity, PrimaryRecord and PrimaryRecord2, that are polymorphic fields, so they’re limited to storing IDs from objects in their respective domains. Use this text field for all objects. This field is available in API version 63.0 and later. |
| RelatedRecord2Id | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Optional. The ID of a record that can provide additional context about the error. For example, if `PrimaryRecord2Id` is the ID of an order, this field could be the ID of an invoice line. This field is available in API version 66.0 and later.  This field is a polymorphic relationship field.  Relationship Name  RelatedRecord2  Refers To  CreditMemoLine, CreditMemoLineInvoiceLine, CreditMemoLineTax, DebitMemo, GeneralLedgerAccount, GeneralLedgerAcctAsgntRule, InvoiceLine, InvoiceLineTax, Payment, PaymentLineInvoice, PaymentLineInvoiceLine, Refund, RefundLinePayment |
| RelatedRecordId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of a record that can provide additional context about the error. For example, if `PrimaryRecordId` is the ID of an order, this field could be the ID of an order item.  This field is a polymorphic relationship field.  Relationship Name  RelatedRecord  Refers To  Asset, BillingBatchScheduler, BillingSchedule, BillingScheduleGroup, CreditMemo, CreditMemoLine, InvBatchDraftToPostedRun, Invoice, InvoiceBatchRun, InvoiceLine, OrderItem |
| Request | Type  textarea  Properties  Nillable  Description  Optional. A field providing additional information linking the error with the request. This field is available in API version 66.0 and later. |
| RequestIdentifier | Type  string  Properties  Filter, Group, idLookup, Nillable, Sort  Description  A unique ID returned by the request. Use this ID to identify the revenue transaction error log records for a specific request. |
| RevenueAsyncOperationId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the revenue async operation record created by the request. Revenue async operation records contain information about the status of the asynchronous process initiated by the request. This field is available in API version 57.0 and later.  This field is a relationship field.  Relationship Name  RevenueAsyncOperation  Relationship Type  Lookup  Refers To  RevenueAsyncOperation |
| Severity | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The severity type for the error message. This field is available in API version 66.0 and later.  Valid values are:  - `Error` - `Warning` |
