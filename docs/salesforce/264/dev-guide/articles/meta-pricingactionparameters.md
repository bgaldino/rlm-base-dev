---
page_id: meta-pricingactionparameters
title: PricingActionParameters
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-pricingactionparameters.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-metadata-api-parent
legacy_page_id: meta_pricingactionparameters.htm
fetched_at: 2026-11-25
---

# PricingActionParameters

Represents the pricing action that’s associated with a context definition and pricing procedure.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

PricingActionParameters components have the suffix `.pricingActionParameters` and are stored in the `pricingActionParameters` folder.

## Version

PricingActionParameters components are available in API version 60.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| `contextDefinition` | string | Required. Context definition record that’s associated with the pricing action. |
| `contextMapping` | string | Required. Context mapping record that’s associated with the pricing action. |
| `developerName` | string | Required. Unique name of the pricing action parameter record. The name must begin with a letter and use only alphanumeric characters and underscores. The name must not include spaces, end with an underscore, or have two consecutive underscores. |
| `effectiveFrom` | dateTime | Required. Date and time from when the pricing action becomes effective. |
| `effectiveTo` | dateTime | Date and time till when the pricing action is in effect. |
| `masterLabel` | string | Required. Master label of the pricing action parameter. |
| `objectName` | string | Name of the object that’s associated with the pricing action. Valid values are `Case`, `Contract`, `Opportunity`, `Order`, `Quote`, `SalesAgreement`, or `WorkOrder`. |
| `pricingProcedure` | string | Pricing procedure record that’s associated with this pricing action. |

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

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>PricingActionParameters</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-pricingactionparameters.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
