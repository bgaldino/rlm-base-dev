---
page_id: sforce-api-objects-attributebasedadjrule
title: AttributeBasedAdjRule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributebasedadjrule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_attributebasedadjrule.htm
fetched_at: 2026-11-25
---

# AttributeBasedAdjRule

Represents the attribute conditions in a rule associated with the attribute based adjustment made for a product or service being sold. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AttributeCount

- **Type**: int

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The number of attributes.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the attribute based adjustment rule was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Name of the attribute based adjustment rule.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: ID of the owner of the attribute based adjustment rule.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### UsageType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of record where the attribute-based adjustment rule is used.

Possible values are:

- `Pricing`

- `Rating`

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AttributeBasedAdjRuleFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[AttributeBasedAdjRuleHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[AttributeBasedAdjRuleShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-attributebasedadjrule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
