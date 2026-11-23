---
page_id: sforce_api_objects_productusageresourcepolicy.htm
title: ProductUsageResourcePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productusageresourcepolicy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-11-23
---

# ProductUsageResourcePolicy

Represents the policies applicable to the usage resource when it’s associated with a sellable product. These policies are derived from the parent usage resource and can be overridden when setting up usage modeling.This object is available in API version 65 and later.

![Important](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: Date and time when the current user last viewed or modified this record, a record related to this record, or a list view.

### LastViewedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: Date and time when the current user last viewed or modified this record.

### ProductSellingModelId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The product selling model associated with this policy.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel
- **Refers To**: ProductSellingModel

### ProductUsageResourceId

- **Type**: reference
- **Properties**: Create, Filter, Group, Sort
- **Description**: The product usage resource associated with this policy.

This field is a relationship field.

- **Relationship Name**: ProductUsageResource
- **Relationship Type**: Master-detail
- **Refers To**: ProductUsageResource (the master object)

### RatingFrequencyPolicyId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The rating frequency policy associated with the usage resource.

This field is a relationship field.

- **Relationship Name**: RatingFrequencyPolicy
- **Refers To**: RatingFrequencyPolicy

### UsageAggregationPolicyId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The usage aggregation policy associated with the usage resource.

This field is a relationship field.

- **Relationship Name**: UsageAggregationPolicy
- **Refers To**: UsageResourceBillingPolicy

### UsageCommitmentPolicyId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The usage commitment policy associated with the usage resource.

This field is a relationship field.

- **Relationship Name**: UsageCommitmentPolicy
- **Refers To**: UsageCommitmentPolicy

### UsageOveragePolicyId

- **Type**: reference
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The usage overage policy associated with the usage resource.

This field is a relationship field.

- **Relationship Name**: UsageOveragePolicy
- **Refers To**: UsageOveragePolicy

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductUsageResourcePolicyFeed](./sforce_api_associated_objects_feed.htm.md):** Feed tracking is available for the object.

**[ProductUsageResourcePolicyHistory](./sforce_api_associated_objects_history.htm.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productusageresourcepolicy.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
