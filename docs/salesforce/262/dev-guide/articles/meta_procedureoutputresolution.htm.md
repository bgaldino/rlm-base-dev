---
page_id: meta_procedureoutputresolution.htm
title: ProcedureOutputResolution
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_procedureoutputresolution.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# ProcedureOutputResolution

Represents the pricing resolution for a pricing
element determined by using strategy name and formula.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

## File Suffix and Directory Location

ProcedureOutputResolution components have the suffix
.procedureOutputResolution and are stored in the
procedureOutputResolution folder.

## Version

ProcedureOutputResolution components are available in API version 63.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Description |
| --- | --- |
| developerName | Field Type  string  Description  Required. API name of the procedure output resolution. |
| formula | Field Type  string  Description  Required.  Stores the encoded formula as text. |
| isActive | Field Type  boolean  Description  Required.  Indicates whether the strategy is active (`true`) or not (`false`). |
| isInternal | Field Type  boolean  Description  Reserved for internal use. |
| masterLabel | Field Type  string  Description  Required.  A user-friendly name for the procedure output resolution, which is defined when the ProcedureOutputResolution record is created. |
| pricingElement | Field Type  string  Description  Required.  Pricing element on which the procedure output resolution is defined. |

## Declarative Metadata Sample Definition

Here's an example of a ProcedureOutputResolution component.

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

Here's an example `package.xml` that references the
previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ProcedureOutputResolution</name>
    </types>
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
