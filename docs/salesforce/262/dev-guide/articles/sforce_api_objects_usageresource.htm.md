---
page_id: sforce_api_objects_usageresource.htm
title: UsageResource
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usageresource.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# UsageResource

Represents an entitlement granted to a user or party by a provider,
such as data storage, computing power, bandwidth, or any other product or service.
Additionally, this object is used to represent resources consumed over time. This
object is available in API version 62.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| Category | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The category of the usage resource that's used to organize and understand the product grant maps.  Valid values are:  - `Currency`—Available in API version 65.0 and   later. - `Usage` - `Token`—Available   in API version 64.0 and later. |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The unique user-defined string for the usage resource. |
| DefaultUnitOfMeasureId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The default unit of measure for the given resource. The default value can be overridden with an alternate default unit of measure for a given resource.  This field is a relationship field.  Relationship Name  DefaultUnitOfMeasure  Refers To  UnitOfMeasure |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The description of the usage resource. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the usage resource record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the usage resource record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the usage resource.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| TokenResourceId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage resource of Category `Token` that’s used to charge this usage resource. For example, you can select a usage resource Credits (Token category) to rate the usage resource Data (Usage category). This field is available in API version 65.0 and later.  Relationship Name  TokenResource  Refers To  UsageResource |
| UnitOfMeasureClassId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unit of measure class that's used with the resource to define the units in which this resource is measured.  This field is a relationship field.  Relationship Name  UnitOfMeasureClass  Refers To  UnitOfMeasureClass |
| UsageDefinitionProductId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The product associated with the usage resource to retrieve tax policy, calculate rating during overages, and other invoicing actions.  This field is a relationship field.  Relationship Name  UsageDefinitionProduct  Refers To  Product2 |
| UsageResourceBillingPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The usage resource billing policy that defines how the usage resource can be aggregated before it's sent for rating.  This field is a relationship field. This field is deprecated and will be retired in a future version.  Relationship Name  UsageResourceBillingPolicy  Refers To  UsageResourceBillingPolicy |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[UsageResourceFeed](https://developer.salesforce.com/docs/./sforce_api_associated_objects_feed.htm.md)
:   Feed tracking is available for the object.

[UsageResourceHistory](https://developer.salesforce.com/docs/./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.

[UsageResourceOwnerSharingRule](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing rules are available for the object.

[UsageResourceShare](https://developer.salesforce.com/docs/./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing is available for the object.
