---
page_id: meta_pricingactionparameters.htm
title: PricingActionParameters
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_pricingactionparameters.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# PricingActionParameters

Represents the pricing action that's associated with a
context definition and pricing procedure.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality.
We maintained certain terms to avoid any effect on customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

## File Suffix and Directory Location

PricingActionParameters components have the suffix
.pricingActionParameters and are stored in the
pricingActionParameters folder.

## Version

PricingActionParameters components are available in API version 60.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Description |
| --- | --- |
| contextDefinition | Field Type  string  Description  Required.  Context definition record that's associated with the pricing action. |
| contextMapping | Field Type  string  Description  Required.  Context mapping record that's associated with the pricing action. |
| developerName | Field Type  string  Description  Required.  Unique name of the pricing action parameter record.  The name must begin with a letter and use only alphanumeric characters and underscores. The name must not include spaces, end with an underscore, or have two consecutive underscores. |
| effectiveFrom | Field Type  dateTime  Description  Required.  Date and time from when the pricing action becomes effective. |
| effectiveTo | Field Type  dateTime  Description  Date and time till when the pricing action is in effect. |
| masterLabel | Field Type  string  Description  Required.  Master label of the pricing action parameter. |
| objectName | Field Type  string  Description  Name of the object that's associated with the pricing action. Valid values are:  - `Case` - `Contract` - `Opportunity` - `Order` - `Quote` - `SalesAgreement` - `WorkOrder` |
| pricingProcedure | Field Type  string  Description  Pricing procedure record that's associated with this pricing action. |

## Declarative Metadata Sample Definition

The following is an example of a PricingActionParameters component.

```
<PricingActionParameters xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>CMEDefaultActionParameters</developerName>
    <objectName>ORDER</objectName>
    <pricingProcedure>PP</pricingProcedure>
    <effectiveFrom>2024-04-08T07:32:00.000Z</effectiveFrom>
    <effectiveTo>2024-04-11T07:32:00.000Z</effectiveTo>
    <contextDefinition>SalesTransactionContext__stdctx</contextDefinition>
    <contextMapping>SalesAgreementEntitiesMapping</contextMapping>
    <masterLabel>PAP_test</masterLabel>
</PricingActionParameters>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>PricingActionParameters</name>
    </types>
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
