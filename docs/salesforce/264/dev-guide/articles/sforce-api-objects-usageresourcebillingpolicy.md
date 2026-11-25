---
page_id: sforce-api-objects-usageresourcebillingpolicy
title: UsageResourceBillingPolicy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usageresourcebillingpolicy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-std-objects-parent
legacy_page_id: sforce_api_objects_usageresourcebillingpolicy.htm
fetched_at: 2026-11-25
---

# UsageResourceBillingPolicy

Represents information about how the usage is accumulated before rating a usage resource.This object is available in API version 62.0 and later.

A usage resource billing policy object is used to configure the properties of usage resources related to how aggregation is performed on the usage records before rating. Usage resource billing policies are defined at the usage resource level and can be reused across multiple usage resources.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### Code

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: A unique user-defined string for the usage resource billing policy.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when this record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the usage resource billing policy record.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The status of the policy.

Valid values are `Active`, `Draft`, or `Inactive`.

### UsageAccumulationMethod

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update, Defaulted On Create

- **Description**: The method used to accumulate the usage.

Valid values are `Peak` or `Sum`.

### UsageAccumulationPeriod

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The duration for which the usage is accumulated.

Valid values are `Daily` or `Monthly`.

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[UsageResourceBillingPolicyFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[UsageResourceBillingPolicyHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usageresourcebillingpolicy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
