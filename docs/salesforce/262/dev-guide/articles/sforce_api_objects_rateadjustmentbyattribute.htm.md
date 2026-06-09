---
page_id: sforce_api_objects_rateadjustmentbyattribute.htm
title: RateAdjustmentByAttribute
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_rateadjustmentbyattribute.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_std_objects_parent.htm
fetched_at: 2026-06-09
---

# RateAdjustmentByAttribute

Represents the adjustments that determine the rate of a resource based on its
rate-impacting attributes. These attributes are linked to the usage product record. Rates
are then influenced by conditions specified in the Attribute Based Adjustment Condition
object. Finally, the charge rate is determined by using the Attribute Based Adjustment Rule
object. This object is available in API version 62.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AdjustmentType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Type of rate adjustment.  Valid values are:  - `Amount` - `Override` - `Percentage` |
| AdjustmentValue | Type  double  Properties  Create, Filter, Sort, Update  Description  Value of the rate adjustment based on the selected adjustment type. |
| AttributeBasedAdjRuleId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  ID of the attribute based adjustment rule associated with this rate adjustment by attribute record.  This field is a relationship field.  Relationship Name  AttributeBasedAdjRule  Refers To  AttributeBasedAdjRule |
| EffectiveFrom | Type  dateTime  Properties  Filter, Sort  Description  Date and time when the associated rate card entry comes into effect. |
| EffectiveTo | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Date and time until when the associated rate card entry remains effective. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last referred to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Timestamp for when the current user last viewed a record related to this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Auto-generated identifier for the rate adjustment by attribute record. |
| ProductId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the product whose resource is being used as the associated rate card entry.  This field is a relationship field.  Relationship Name  Product  Refers To  Product2 |
| ProductSellingModelId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  ID of the product selling model for the associated rate card entry.  This field is a relationship field.  Relationship Name  ProductSellingModel  Refers To  ProductSellingModel |
| RateCardEntryId | Type  reference  Properties  Create, Filter, Group, Sort  Description  ID of the rate card entry associated with this rate adjustment by attribute record.  This field is a relationship field.  Relationship Name  RateCardEntry  Relationship Type  Master-detail  Refers To  RateCardEntry (the master object) |
| RateCardEntryStatus | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Status of the rate card entry associated with this rate adjustment by attribute.  Valid values are:  - `Active` - `Draft` - `Inactive`  The default value is `Draft`. Available in API version 63.0 and later. |
| RateCardId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the rate card of the associated rate card entry.  This field is a relationship field.  Relationship Name  RateCard  Refers To  RateCard |
| RateUnitOfMeasureId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the standard unit of measure record of the associated rate card entry.  This field is a relationship field.  Relationship Name  RateUnitOfMeasure  Refers To  UnitOfMeasure |
| RateUnitOfMeasureName | Type  string  Properties  Filter, Group, Sort  Description  Name of the standard unit of measure record of the associated rate card entry. |
| UsageResourceId | Type  reference  Properties  Filter, Group, Sort  Description  ID of the resource selected for the associated rate card entry.  This field is a relationship field.  Relationship Name  UsageResource  Refers To  UsageResource |

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re
available in the same API versions as this object. Otherwise, they’re available in the
specified API version and later.

[RateAdjustmentByAttributeFeed](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[RateAdjustmentByAttributeHistory](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
