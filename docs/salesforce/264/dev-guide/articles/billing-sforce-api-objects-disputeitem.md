---
page_id: billing-sforce-api-objects-disputeitem
title: Billing Fields on DisputeItem
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-disputeitem.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-extended-standard-object-fields
legacy_page_id: billing_sforce_api_objects_disputeitem.htm
fetched_at: 2026-11-25
---

# Billing Fields on DisputeItem

Represents a specific invoice line or charge that’s being disputed. The details include the total transaction amount, transaction date, disputed amount, reason, and status of the dispute. This object is available in API version 66.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Operations User or the Billing Customer Service User permission set to access this object.

**See Also**

- [*Financial Services Cloud Developer Guide*: DisputeItem](https://developer.salesforce.com/docs/atlas.en-us.financial_services_cloud_object_reference.meta/financial_services_cloud_object_reference/sforce_api_objects_disputeitem.htm)

## Fields

### ApprovedAmount

**Type:** currency

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The amount that’s approved to be credited to the customer.

### InvoiceLineId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort, Update

**Description:** The invoice line ID associated with the dispute.

This field is a relationship field.

**Relationship Name:** Invoice Line

**Refers To:** Invoice Line

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-disputeitem.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
