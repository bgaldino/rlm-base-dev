---
page_id: billing_sforce_api_objects_dispute.htm
title: Billing Fields on Dispute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_dispute.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-11-23
---

# Billing Fields on Dispute

Represents the details of a billing dispute that involves one invoice and one or more disputed invoice lines. The details include the disputed amount, the approved amount, and the dispute type, subtype and status. This object is available in API version 66.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Operations User or the Billing Customer Service User permission set to access this object.

#### See Also

- [*Financial Services Cloud Developer Guide*: Dispute](https://developer.salesforce.com/docs/atlas.en-us.264.0.financial_services_cloud_object_reference.meta/financial_services_cloud_object_reference/sforce_api_objects_dispute.htm)

## Fields

### InvoiceId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The invoice ID associated with the dispute.

This field is a relationship field.

**Relationship Name:** Invoice

**Refers To:** Invoice

### RevisedDueDate

**Type:** dateTime

**Properties:** Filter, Nillable, Sort

**Description:** The revised due date for the invoice.

### BillingSuspensionDate

**Type:** dateTime

**Properties:** Filter, Nillable, Sort

**Description:** The date when billing for the account is suspended.

### BillingResumptionDate

**Type:** dateTime

**Properties:** Filter, Nillable, Sort

**Description:** The date when billing for the account is resumed.

### RevisedBillToContact

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The revised billing contact for the invoice.

This field is a relationship field.

**Relationship Name:** Contact

**Refers To:** Contact

### ResolutionAction

**Type:** picklist

**Properties:** Filter, Group, Nillable, Restricted picklist, Sort

**Description:** The action taken to resolve the dispute.

Valid values are `Resolve with No Action` or `Issue Credit Memo`

### ResolutionActionStatus

**Type:** picklist

**Properties:** Filter, Group, Nillable, Restricted picklist, Sort

**Description:** The status of the resolution action.

Valid values are `In Progress`, `Closed`, or `Error`

### MaySetContactAsDefault

**Type:** boolean

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

**Description:** Indicates whether the revised billing contact is set as default for future invoices ( `true`) or not ( `false`).

The default value is `false`.

### UsageType

**Type:** picklist

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** Specifies the name of the cloud or function that uses the Dispute object.

Valid value is `Billing`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_dispute.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
