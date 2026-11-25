---
page_id: meta-productspecificationtype
title: ProductSpecificationType
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-productspecificationtype.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-metadata-api-parent
legacy_page_id: meta_productspecificationtype.htm
fetched_at: 2026-11-25
---

# ProductSpecificationType

Represents the specification types in your org that define products with unique terminology specific to the industry.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

ProductSpecificationType components have the suffix `.productSpecificationType` and are stored in the `productSpecificationTypes` folder.

## Version

ProductSpecificationType components are available in API version 60.0 and later.

## Special Access Rules

Ensure Product Catalog Management is enabled to access this metadata type.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| `description` | string | Required. Description of the product specification type. |
| `masterLabel` | string | Required. A user-friendly name for the product specification record type, which is defined when the metadata component is created. |

## Declarative Metadata Sample Definition

The following is an example of a ProductSpecificationType component.

```
<ProductSpecificationType xmlns="http://soap.sforce.com/2006/04/metadata">
    <masterLabel>sample</masterLabel>
    <description>Sample Description</description>
</ProductSpecificationType>
```

The following is an example `package.xml` that references the previous definition.

```
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ProductSpecificationType</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-productspecificationtype.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
