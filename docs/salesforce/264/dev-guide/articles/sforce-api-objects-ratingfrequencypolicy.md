---
page_id: sforce-api-objects-ratingfrequencypolicy
title: RatingFrequencyPolicy
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingfrequencypolicy.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_ratingfrequencypolicy.htm
fetched_at: 2026-11-25
---

# RatingFrequencyPolicy

Represents the policy that defines the frequency at which rating is triggered for the ratable summary records. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Name of the rating frequency policy. This is a mandatory field.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: ID of the product for which the rating policy is defined.

This field is a relationship field. This field is deprecated and will be retired in a future version.

- **Relationship Name**: Product

- **Refers To**: Product2

### RatingDelayDuration

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Duration of delay—in hours—post the billing period after which the rating is to be triggered.

### RatingDelayDurationUnit

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Specifies the unit for the specified rating delay duration. Available in API version 65.0 and later.

Valid values are `Days` or `Hours`.

### RatingPeriod

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Period for which the usage of a product and usage resource combination is to be rated.

Valid values are `Daily` or `Monthly`.

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[RatingFrequencyPolicyFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[RatingFrequencyPolicyHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[RatingFrequencyPolicyOwnerSharingRule](./sforce-api-associated-objects-ownersharingrule.md):** Sharing rules are available for the object.

**[RatingFrequencyPolicyShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingfrequencypolicy.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
