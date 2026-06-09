---
page_id: sforce_api_objects_ratingfrequencypolicy.htm
title: RatingFrequencyPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_ratingfrequencypolicy.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RatingFrequencyPolicy

Represents the policy that defines the frequency at which rating is
triggered for the ratable summary records. This object is available in API version
62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Name of the rating frequency policy. This is a mandatory field. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  ID of the product for which the rating policy is defined.  This field is a relationship field. This field is deprecated and will be retired in a future version.  Relationship Name  Product  Refers To  Product2 |
| RatingDelayDuration | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Duration of delay—in hours—post the billing period after which the rating is to be triggered. |
| RatingDelayDurationUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the unit for the specified rating delay duration. Available in API version 65.0 and later.  Valid values are:  - `Days` - `Hours` |
| RatingPeriod | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Period for which the usage of a product and usage resource combination is to be rated.  Valid values are:  - `Daily` - `Monthly` |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  ID of the usage resource for which the rating policy is defined.  This field is a relationship field. This field is deprecated and will be retired in a future version.  Relationship Name  UsageResource  Refers To  UsageResource |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[RatingFrequencyPolicyFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[RatingFrequencyPolicyHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.

[RatingFrequencyPolicyOwnerSharingRule](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing rules are available for the object.

[RatingFrequencyPolicyShare](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
