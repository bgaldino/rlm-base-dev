---
page_id: sforce-api-objects-productsellingmodeldatatranslation
title: ProductSellingModelDataTranslation
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productsellingmodeldatatranslation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_productsellingmodeldatatranslation.htm
fetched_at: 2026-11-25
---

# ProductSellingModelDataTranslation

Represents the translated values of the data stored within the ProductSellingModel record’s fields. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

- Your organization must be using Enterprise, Unlimited, or Developer edition.

- Translation Workbench and data translation must be enabled in your org.

- To view this object, you must have the “View Setup and Configuration” permission.

## Fields

### IsOutOfDate

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the translation is out-of-date (`true`) or current (`false`). A translation is out-of-date if the parent Product2 record is updated after the last translation was filed.

### Language

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort

- **Description**: The language for these translated values.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The translated value for the ProductSellingModel record name. This field is required to translate the text in other fields.

### ParentId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the ProductSellingModel record associated with the data that’s being translated.

This field is a relationship field.

- **Relationship Name**: Parent

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

## Usage

Use this object to translate the data stored in a ProductSellingModel record into the different languages supported by Salesforce. If data translation is enabled for custom fields on the ProductSellingModel object, additional ProductSellingModelDataTranslation fields exist for translating the data contained within those fields.

You can’t use a custom external id field in an upsert call for a ProductSellingModelDataTranslation object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productsellingmodeldatatranslation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
