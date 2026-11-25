---
page_id: sforce-api-objects-refundlinecreditmemoline
title: RefundLineCreditMemoLine
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-refundlinecreditmemoline.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_refundlinecreditmemoline.htm
fetched_at: 2026-11-25
---

# RefundLineCreditMemoLine

Represents a junction between a refund and a credit memo line. This object is available in API version 68.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

To access this object, you need the Billing permission set licenses and the Billing Admin permission set.

## Fields

### Amount

- **Type**: currency

- **Properties**: Create, Filter, Sort

- **Description**: Required. The refund amount that’s been applied to or unapplied from the credit memo line.

### AppliedDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort

- **Description**: The date and time when the refund was applied to the credit memo line.

### Comments

- **Type**: textarea

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Additional details about the credit memo line refund.

### CreditMemoLineBalance

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The balance of the credit memo line after the refund was applied or unapplied.

### CreditMemoLineId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Required. The credit memo line to which the refund has been applied or unapplied.

This field is a relationship field.

- **Relationship Name**: CreditMemoLine

- **Relationship Type**: Master-detail

- **Refers To**: CreditMemoLine (the master object)

### CreditMemoLineRefundNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. An auto-generated number identifying the credit memo line refund.

### EffectiveDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort

- **Description**: The date and time when the refund’s application or unapplication takes effect.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferencedDate` isn’t null, the user accessed this record or list view indirectly.

### LegalEntityAccountingPeriodId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The legal entity accounting period record that’s related to the credit memo line refund.

This field is a relationship field.

- **Relationship Name**: LegalEntityAccountingPeriod

- **Refers To**: LegalEntyAccountingPeriod

### LegalEntityId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The legal entity related to the credit memo line refund.

This field is a relationship field.

- **Relationship Name**: LegalEntity

- **Refers To**: LegalEntity

### RefundBalance

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The balance of the refund after the refund was applied or unapplied.

### RefundId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Required. The refund associated with the credit memo line.

This field is a relationship field.

- **Relationship Name**: Refund

- **Refers To**: Refund

### RelatedCreditMemoLineRefundId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The applied credit memo line refund that’s being unapplied.

This field is a relationship field.

- **Relationship Name**: RelatedCreditMemoLineRefund

- **Refers To**: CreditMemoLineRefund

### Type

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort

- **Description**: Required. Specifies whether the refund has been applied to or unapplied from the credit memo line.

Valid values are `Applied` or `Unapplied`.

### UnappliedDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort

- **Description**: The date and time when the refund was unapplied from the credit memo line.

### UnappliedStatus

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort

- **Description**: Required. Specifies whether the refund has been unapplied from the credit memo line.

Valid values are `NA`, `No`, or `Yes`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-refundlinecreditmemoline.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
