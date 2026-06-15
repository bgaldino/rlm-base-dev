---
page_id: sforce_api_objects_productsellingmodeldatatranslation.htm
title: ProductSellingModelDataTranslation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productsellingmodeldatatranslation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ProductSellingModelDataTranslation

Represents the translated values of the data stored within the
ProductSellingModel record’s fields. This object is available in API version 61.0 and
later.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

- Your organization must be using Enterprise, Unlimited, or Developer edition.
- Translation Workbench and data translation must be enabled in your org.
- To view this object, you must have the “View Setup and Configuration”
  permission.

## Fields

| Field | Details |
| --- | --- |
| IsOutOfDate | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the translation is out-of-date (`true`) or current (`false`). A translation is out-of-date if the parent Product2 record is updated after the last translation was filed. |
| Language | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  The language for these translated values. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The translated value for the ProductSellingModel record name. This field is required to translate the text in other fields. |
| ParentId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the ProductSellingModel record associated with the data that’s being translated.  This field is a relationship field.  Relationship Name  Parent  Relationship Type  Lookup  Refers To  ProductSellingModel |

## Usage

Use this object to translate the data stored in a ProductSellingModel record into the
different languages supported by Salesforce. If data translation is enabled for custom
fields on the ProductSellingModel object, additional ProductSellingModelDataTranslation
fields exist for translating the data contained within those fields.

You can’t use a custom external id field in an upsert call for a
ProductSellingModelDataTranslation object.
