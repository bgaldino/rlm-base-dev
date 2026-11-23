---
page_id: sforce_api_objects_paymentadviceinvoicerecile.htm
title: PaymentAdviceInvoiceRecile
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentadviceinvoicerecile.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# PaymentAdviceInvoiceRecile

Represents an invoice match with a payment advice line, linking a payment advice line to an open invoice. This object is available in API version 68.0 and later.

![Important](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the Payment Operations User permission set to access this object.

## Fields

### AppliedAmount

- **Type**: currency
- **Properties**: Create, Filter, Sort, Update
- **Description**: Required. The net amount from the payment advice line record that indicates the amount the payer intends to clear against the specific invoice.

### DeductionAmount

- **Type**: currency
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The deduction or discount amount applied by the payer on the payment advice invoice reconciliation record.

### DeductionCode

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The reason code for the deduction applied on the payment advice invoice reconciliation record.

### InvoiceId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the open invoice record that matched this payment advice invoice reconciliation record. A null value indicates that no matching invoice was found.

This field is a relationship field.

- **Relationship Name**: Invoice
- **Refers To**: Invoice

### InvoiceNumber

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: Required. The invoice number on the payment advice line record that’s used to match open invoices.

### InvoiceTotalAmount

- **Type**: currency
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The total invoice amount. A null value indicates that no matching invoice was found.

### MatchMethodType

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Required. Indicates the method that produced the line-level match.

Valid values are `Exact Invoice Number` or `Manual`.

### MatchType

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Required. Specifies whether this line item was successfully matched to an invoice, remains unmatched, or was manually overridden.

Valid values are `Manual Override`, `Matched`, or `Unmatched Line`.

### OwnerId

- **Type**: reference
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Required. The ID of the owner of this record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Refers To**: Group, User

### PaymentAdviceInvoiceRecileNumber

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: Required. An auto-generated number identifying the payment advice invoice reconciliation.

### PaymentAdviceReconciliationId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the parent payment advice reconciliation related to this payment advice invoice reconciliation record. Each line-level invoice matches back to the overall payment advice reconciliation record that paired the payment advice with a bank transaction and a resolved account.

This field is a relationship field.

- **Relationship Name**: PaymentAdviceReconciliation
- **Refers To**: PaymentAdviceReconciliation

### ReviewStatus

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Required. The status of the payment advice invoice reconciliation record in the review process.

Valid values are `Accepted`, `Pending`, `Rejected`, or `Resolved Manually`.

### ReviewedById

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the user that reviewed the payment advice invoice reconciliation record.

This field is a relationship field.

- **Relationship Name**: ReviewedBy
- **Refers To**: User

### ReviewedDateTime

- **Type**: dateTime
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The date and time when the reviewer reviewed the payment advice invoice reconciliation record.

### SourceSystemName

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The name or identifier of the system from which this record was sourced.

### SourceSystemRecordIdentifier

- **Type**: string
- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update
- **Description**: The unique identifier of this record in the source system from which the data originated.

### UnmatchedReasonText

- **Type**: picklist
- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update
- **Description**: Indicates the reason the payment advice invoice reconciliation record couldn’t be matched to an invoice.

Valid values are `Invoice Already Paid`, `Invoice For Different Account`, `No Matching Invoice`, or `Other`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PaymentAdviceInvoiceRecileShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object."):** Sharing is available for the object.

**[PaymentAdviceInvoiceRecileHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentadviceinvoicerecile.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
