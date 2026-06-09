---
page_id: sforce_api_objects_assettag.htm
title: AssetTag
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assettag.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_standard_objects.htm
fetched_at: 2026-06-09
---

# AssetTag

Associates a word or short phrase with an Asset.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`,
`query()`, `retrieve()`

## Fields

| Field Name | Details |
| --- | --- |
| ItemId | Type  reference  Properties  Create, Filter  Description  ID of the tagged item. |
| Name | Type  string  Properties  Create, Filter  Description  Name of the tag. If this value does not already exist, a new TagDefinition is created and becomes the parent of this Tag object. Otherwise, a TagDefinition with the same name becomes the parent of this Tag object. Parent relationships are created automatically. |
| TagDefinitionId | Type  reference  Properties  Filter  Description  ID of the parent TagDefinition object that owns the tag. |
| Type | Type  picklist  Properties  Create, Filter, Restricted picklist  Description  Defines the visibility of a tag.  Valid values:  - `Public`—The tag can be viewed and   manipulated by all users in an organization. - `Personal`—The tag can be viewed or   manipulated only by a user with a matching   OwnerId. |

## Usage

AssetTag stores the relationship between its parent TagDefinition and the Asset being
tagged. Tag objects act as metadata, allowing users to describe and organize their
data.

When a tag is deleted, its parent TagDefinition will also be deleted if the name is
not being used; otherwise, the parent remains. Deleting a TagDefinition sends it to
the Recycle Bin, along with any associated tag entries.
