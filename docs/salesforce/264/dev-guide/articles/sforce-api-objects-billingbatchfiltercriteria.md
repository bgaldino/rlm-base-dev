---
page_id: sforce-api-objects-billingbatchfiltercriteria
title: BillingBatchFilterCriteria
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingbatchfiltercriteria.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_billingbatchfiltercriteria.htm
fetched_at: 2026-11-25
---

# BillingBatchFilterCriteria

Represents the filter that all eligible billing schedules must satisfy in order to be picked up by an invoice run. This object is available in API version 62.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### BatchCriteriaId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the batch criteria record.

This field is a polymorphic relationship field.

- **Relationship Name**: BatchCriteria

- **Refers To**: InvoiceBatchRunCriteria

### BillingBatchFilterCriteriaNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The auto-generated reference number for the billing batch filter criteria.

### ColumnEnum

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. The column or field to which the filter criteria are applied.

### CriteriaFieldType

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The data type of the custom or standard criteria field.

Valid values are:Available in API version 63.0 and later.

- `CustomBoolean`

- `CustomCurrency`

- `CustomDate`

- `CustomLookup`

- `CustomNumber`

- `CustomPercent`

- `CustomText`

### CriteriaSequence

- **Type**: int

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The order in which the filter criteria are applied on the billing batch.

### CustomCriteriaFieldName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The API name of the custom field on the object specified in the `ObjectName` field. The filter criteria is applied on the custom field. This object is available in API version 65.0 and later.

### InvoiceRunMatchingValue

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: A value to match during an invoice run. This field is useful for filtering the invoices based on specific criteria during the billing process.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferenceDate` is not null, the user accessed this record or list view indirectly.

### ObjectName

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. The object on which the filter criteria are applied.

Valid values are:

- `AccountBillingAccount` — Available in API version 63.0 and later.

- `BillingAccount` — Available in API version 63.0 and later.

- `BillingSchedule`

- `BillingScheduleGroup`

- `CreditMemo` — Available in API version 63.0 and later.

- `CreditMemoInvApplication` — Available in API version 63.0 and later.

- `CreditMemoLine` — Available in API version 63.0 and later.

- `CreditMemoLineInvoiceLine` — Available in API version 63.0 and later.

- `CreditMemoLineTax` — Available in API version 63.0 and later.

- `DebitMemoLine` — Available in API version 65.0 and later.

- `Invoice` — Available in API version 63.0 and later.

- `InvoiceLine` — Available in API version 63.0 and later.

- `InvoiceLineTax` — Available in API version 63.0 and later.

- `Payment` — Available in API version 64.0 and later.

- `PaymentGateway` — Available in API version 64.0 and later.

- `PaymentLineInvoice` — Available in API version 64.0 and later.

- `PaymentLineInvoiceLine` — Available in API version 64.0 and later.

- `PaymentSchedule` — Available in API version 64.0 and later.

- `PaymentScheduleItem` — Available in API version 64.0 and later.

- `Refund` — Available in API version 64.0 and later.

- `RefundLinePayment` — Available in API version 64.0 and later.

### Operation

- **Type**: picklist

- **Properties**: Filter, Group, Restricted picklist, Sort

- **Description**: Required. The type of comparison or logical operation to be performed on the specified column or field.

Valid values are:

- `Contains` — Available in API version 63.0 and later.

- `Equals`

- `GreaterThan` — Available in API version 63.0 and later.

- `GreaterThanOrEqualTo` — Available in API version 63.0 and later.

- `InList`

- `LessThan` — Available in API version 63.0 and later.

- `LessThanOrEqualTo`

- `NotEquals` — Available in API version 63.0 and later.

- `OfType`

- `StartsWith` — Available in API version 63.0 and later.

### OwnerId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. The ID of the user who created the billing batch filter criteria.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### PaymentRunMatchingValue

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: A value to match during a payment run. This field is useful for filtering the payments based on specific criteria during the billing process. This field is visible but isn’t used in API version 62.0.

### StandardCriteriaField

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The name of the standard field for the object specified in the `ObjectName` field. The filter criteria is applied on the standard field. Available in API version 63.0 and later.

### Value

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: Required. The value to be used in the filter criteria.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[BillingBatchFilterCriteriaHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingbatchfiltercriteria.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
