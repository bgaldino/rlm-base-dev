---
page_id: sforce_api_objects_productusageresource.htm
title: ProductUsageResource
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productusageresource.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductUsageResource

Represents the mapping of a product and its usage resources.
This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

## Fields

| Field | Details |
| --- | --- |
| EffectiveEndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the relationship between the product and the usage resource stops being active, and any usage tracking or billing related to this relationship ends. |
| EffectiveStartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the relationship between the product and the usage resource becomes active or effective, and any usage tracking or billing related to this relationship begins. |
| IsOptional | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the product usage resource is optional when the associated product is one of the commitment usage model types (`true`) or not (`false`). The default value is `false`. This field is available in API version 65.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the product usage grant.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The sellable product that grants the usage resource.  This field is a relationship field.  Relationship Name  ProductOffer  Refers To  Product2 |
| ProductUsageResourceNum | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The number of each resource grant map that starts with one and is consecutive. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the product usage resource record.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| TokenResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource of category `Token` that’s associated with the selected usage resource. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  TokenResource  Refers To  UsageResource |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource associated with the product usage grant.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ProductUsageResourceChangeEvent](https://developer.salesforce.com/docs/./sforce_api_associated_objects_change_event.htm.md)
:   Change events are available for the object.

[ProductUsageResourceFeed](https://developer.salesforce.com/docs/./sforce_api_associated_objects_feed.htm.md)
:   Feed tracking is available for the object.

[ProductUsageResourceHistory](https://developer.salesforce.com/docs/./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.

[ProductUsageResourceOwnerSharingRule](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing rules are available for the object.

[ProductUsageResourceShare](https://developer.salesforce.com/docs/./sforce_api_associated_objects_share.htm.md)
:   Sharing is available for the object.
