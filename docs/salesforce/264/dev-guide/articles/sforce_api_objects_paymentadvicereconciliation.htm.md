---
page_id: sforce_api_objects_paymentadvicereconciliation.htm
title: PaymentAdviceReconciliation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentadvicereconciliation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# PaymentAdviceReconciliation

Represents the reconciliation of a payment advice with a bank transaction and a resolved account, including match confidence and the reviewer’s decision. This object is available in API version 68.0 and later.

![Important](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

To access this object, you need the Billing permission set licenses and the Billing Admin permission set.

## Fields

### AccountId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the customer account record associated with the payment.

This field is a relationship field.

- **Relationship Name**: Account
- **Refers To**: Account

### AccountName

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The account name in the Account record.

### AmountVariancePercent

- **Type**: double
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The percentage difference between the payment advice amount and the payment proof amount that’s used to determine if the match falls within the configured tolerance.

### BatchRunReference

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the batch run that produced the payment advice reconciliation record.

### DateVarianceDaysCount

- **Type**: int
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The number of days between the payment date stated on the payment advice and the date the bank recorded the transaction.

### MatchMethodType

- **Type**: picklist
- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update
- **Description**: Indicates the method that produced the payment advice reconciliation.

Valid values are `Manual`, `Reference Number`, `Tolerance`, or `Vector Search`.

### MatchType

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Required. Indicates the completeness of the match based on whether the payment advice, bank transaction, and account are matched or if any component is missing.

Valid values are `Matched`, `Unmatched Account`, `Unmatched Intent`, or `Unmatched Proof`.

### OwnerId

- **Type**: reference
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Required. The ID of the owner of this record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Refers To**: Group, User

### PaymentAdviceAccountScoreNbr

- **Type**: double
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: A confidence score between 0 and 1 that indicates how closely the payer name on the payment advice matched the resolved account.

### PaymentAdvicePayerName

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The payer name from the payment advice record.

### PaymentAdvicePaymentDate

- **Type**: date
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The payment date from the payment advice record.

### PaymentAdviceReconciliationNumber

- **Type**: string
- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort
- **Description**: Required. An auto-generated number identifying the payment advice reconciliation.

### PaymentAdviceReferenceNumber

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The reference number from the payment advice record.

### PaymentAdviceTotalAmount

- **Type**: currency
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The total amount from the payment advice record.

### ProofAccountScoreNumber

- **Type**: double
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: A confidence score between 0 and 1 that indicates how closely the payer name on the payment proof matched the resolved account.

### ProofAmount

- **Type**: currency
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The transaction amount from the payment proof record.

### ProofPayerName

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The payer name on the payment proof record as indicated by the bank records.

### ProofPaymentDate

- **Type**: date
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The booking date from the payment proof record.

### ProofTransactionReferenceNbr

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The reference number from the payment proof (bank) transaction.

### RejectionReasonText

- **Type**: picklist
- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update
- **Description**: The reason for rejecting the payment advice reconciliation, such as wrong account, wrong proof, or duplicate.

Valid values are `Duplicate`, `Other`, `Wrong Account`, or `Wrong Proof`.

### ResolutionNotesText

- **Type**: textarea
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: An explanation about the manual resolution provided by the reviewer.

### ReviewStatus

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Required. The processing status of the payment advice reconciliation record such as pending review, accepted, or rejected.

Valid values are:

- `Accepted`
- `Deferred`
- `Pending`
- `Rejected`
- `Resolved Manually`
- `Superseded`

### ReviewedById

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The ID of the user who reviewed the payment advice reconciliation record.

This field is a relationship field.

- **Relationship Name**: ReviewedBy
- **Refers To**: User

### ReviewedDateTime

- **Type**: dateTime
- **Properties**: Create, Filter, Nillable, Sort, Update
- **Description**: The date and time when a user reviewed the payment advice reconciliation record.

### SourceSystemName

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The name or identifier of the system from which this record was sourced.

### SourceSystemRecordIdentifier

- **Type**: string
- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update
- **Description**: The unique identifier of this record in the source system from which the data originated.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PaymentAdviceReconciliationShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object."):** Sharing is available for the object.

**[PaymentAdviceReconciliationHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentadvicereconciliation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
