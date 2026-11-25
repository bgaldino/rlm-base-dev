---
page_id: meta-procedureoutputresolution
title: ProcedureOutputResolution
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-procedureoutputresolution.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-metadata-api-parent
legacy_page_id: meta_procedureoutputresolution.htm
fetched_at: 2026-11-25
---

# ProcedureOutputResolution

Represents the pricing resolution for a pricing element determined by using strategy name and formula.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

ProcedureOutputResolution components have the suffix `.procedureOutputResolution` and are stored in the `procedureOutputResolution` folder.

## Version

ProcedureOutputResolution components are available in API version 63.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| `developerName` | string | Required. API name of the procedure output resolution. |
| `formula` | string | Required. Stores the encoded formula as text. |
| `isActive` | boolean | Required. Indicates whether the strategy is active (`true`) or not (`false`). |
| `isInternal` | boolean | Reserved for internal use. |
| `masterLabel` | string | Required. A user-friendly name for the procedure output resolution, which is defined when the ProcedureOutputResolution record is created. |
| `pricingElement` | string | Required. Pricing element on which the procedure output resolution is defined. |

## Declarative Metadata Sample Definition

Here’s an example of a ProcedureOutputResolution component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ProcedureOutputResolution xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>ProcedureOutputResolution</developerName>
    <isActive>false</isActive>
    <isInternal>false</isInternal>
    <masterLabel>Procedure Output Resolution</masterLabel>
    <pricingElement>ListPrice</pricingElement>
    <formula>MAX(ListPrice)</formula>
</ProcedureOutputResolution>
```

Here’s an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ProcedureOutputResolution</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-procedureoutputresolution.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
