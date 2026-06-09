---
page_id: sforce_api_objects_productusagegrant.htm
title: ProductUsageGrant
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productusagegrant.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductUsageGrant

Represents the details of a grant associated with a resource, product, or
service, such as the purchased quantity, renewal and rollover policy, and validity of the
grant. This object is available in API version 62.0 and later.

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

## Special Access Rules

To create, update, and delete product usage
grant records, you must have the Usage Management Design Time permission set
license.

## Fields

| Field | Details |
| --- | --- |
| DrawdownOrder | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The order that's used to debit entitlement consumption from the usage entitlement bucket.  Valid values are:  - `ExpiringFirst` - `GrantedFirst` - `GrantedLast`  This field is deprecated and will be retired in a future version. |
| EffectiveEndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time until when the grant remains effective. |
| EffectiveStartDate | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time when the grant becomes effective. |
| Label | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The identifying label for the product usage grant. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when this record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| OverageChargeable | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies whether to charge for overages.  Valid values are:  - `No` - `Yes`  This field is deprecated and will be retired in a future version. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the owner of the product usage grant.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ProductOfferId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The sellable product that grants the usage resource.  This field is a relationship field. This field is deprecated and will be retired in a future version.  Relationship Name  ProductOffer  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The product selling model associated with the product usage grant. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  ProductSellingModel  Refers To  ProductSellingModel |
| ProductUsageGrantNum | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The number of each resource grant map that starts with one and is consecutive. |
| ProductUsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The product usage resource associated with the product usage grant. Available in API version 64.0 and later.  This field is a relationship field.  Relationship Name  ProductUsageResource  Refers To  ProductUsageResource |
| Quantity | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The quantity of the granted resource. |
| RenewalPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The grant renewal policy associated with the product usage grant.  This field is a relationship field.  Relationship Name  RenewalPolicy  Refers To  UsageGrantRenewalPolicy |
| RolloverPolicyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The grant rollover policy associated with the product usage grant.  This field is a relationship field.  Relationship Name  RolloverPolicy  Refers To  UsageGrantRolloverPolicy |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The status of the product usage grant.  Valid values are:  - `Active` - `Draft` - `Inactive` |
| Type | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of model that defines how the usage resource is consumed.  Valid values are:  - `Commit` - `Grant`  The default value is `Grant`. Available in API version 64.0 and later. |
| UnitOfMeasureClassId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The unit of measure class associated with the product usage grant.  This field is a relationship field.  Relationship Name  UnitOfMeasureClass  Refers To  UnitOfMeasureClass |
| UnitOfMeasureId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unit for measure associated with the product usage grant. This value when specified, overrides the default unit of measure defined in the associated unit of measure class.  This field is a relationship field.  Relationship Name  UnitOfMeasure  Refers To  UnitOfMeasure |
| UsageDefinitionProductId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The sellable product associated with the usage resource that's used to retrieve tax policy, calculate rating during overages, and other invoicing actions.  This field is a relationship field.  Relationship Name  UsageDefinitionProduct  Refers To  Product2 |
| UsageModelType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The ID of the unit of measure associated with the product. The type of usage model for a product or service. `Anchor` is the main subscription product or service. `Pack` is the add-on product or service that grants additional usage resources for consumption. `Commit` is the product or service with a specific committed quantity of consumption.  Valid values are:  - `Anchor` - `Pack` - `Token Commitment` - `Quantity   Commitment` - `Monetary   Commitment`  This field is available in API version 65.0 and later. |
| UsageResourceId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The usage resource associated with the product usage grant.  This field is a relationship field. This field is deprecated and will be retired in a future version.  Relationship Name  UsageResource  Refers To  UsageResource |
| ValidityPeriodTerm | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The period until when the resource grant is valid. |
| ValidityPeriodUnit | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The length of a validity period for the resource grant, when used with the ValidityPeriodTerm field.  Valid values are:  - `Month` - `None` - `Year` |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[ProductUsageGrantHistory](./sforce_api_associated_objects_history.htm.md)
:   History is available for tracked fields of the object.

[ProductUsageGrantOwnerSharingRule](./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing rules are available for the object.

[ProductUsageGrantShare](./sforce_api_associated_objects_ownersharingrule.htm.md)
:   Sharing is available for the object.
