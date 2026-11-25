---
page_id: sforce-api-objects-billingarrangementline
title: BillingArrangementLine
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingarrangementline.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_billingarrangementline.htm
fetched_at: 2026-11-25
---

# BillingArrangementLine

Represents the billing account, billing profile, and the percentage of billing amount to be invoiced. Each billing arrangement line results in a separate invoice addressed to the selected billing account. This object is available in API version 66.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AccountId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The ID of the account that’s related to the billing arrangement line.

This field is a relationship field.

- **Relationship Name**: Account

- **Refers To**: Account

### BillingAccountId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The ID of the billing account record that’s related to the billing arrangement line.

This field is a relationship field.

- **Relationship Name**: BillingAccount

- **Refers To**: BillingAccount

### BillingArrangementId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Required. The ID of the billing arrangement record that’s related to the billing arrangement line.

This field is a relationship field.

- **Relationship Name**: BillingArrangement

- **Relationship Type**: Master-detail

- **Refers To**: BillingArrangement (the master object)

### BillingArrangementLineName

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

### BillingPercentage

- **Type**: double

- **Properties**: Create, Defaulted on create, Filter, Sort, Update

- **Description**: Required. The percentage of the billing amount to be assigned to the billing account of the billing arrangement line.

### ShouldBillRemainder

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the remainder percentage must be billed to the billing account of the billing arrangement line (`true`) or not (`false`).

The default value is `false`.

### VersionNumber

- **Type**: int

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: A numerical value indicating the current version of the billing arrangement record. The version number increases when new billing arrangement line records are added or existing billing arrangement line records are updated.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-billingarrangementline.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
