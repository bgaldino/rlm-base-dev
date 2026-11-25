---
page_id: meta-industriespricingsettings
title: IndustriesPricingSettings
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-industriespricingsettings.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-metadata-api-parent
legacy_page_id: meta_industriespricingsettings.htm
fetched_at: 2026-11-25
---

# IndustriesPricingSettings

Represents the settings for Salesforce Pricing.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

In the package manifest, all the settings metadata types for the org are accessed using the “Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_settings.htm) for more details.

## File Suffix and Directory Location

`IndustriesPricingSettings` values are stored in the `IndustriesPricingSettings.settings` file in the `settings` folder. The `.settings` files are different from other named components, because there’s only one settings file for each settings component.

## Version

IndustriesPricingSettings components are available in API version 60.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| `enableDebugPriceLogs` | boolean | Indicates whether to use price logs to diagnose and resolve pricing issues (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later. |
| `enableHighAvailability` | boolean | Reserved for internal use. |
| `enableHighestPriceCompliance` | boolean | Indicates whether to track the maximum price of a product over a period of 30 days (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| `enableLowestPriceCompliance` | boolean | Indicates whether to track the minimum price of a product over a period of 30 days (`true`) or not (`false`). The default value is `false`. Available in API version 62.0 and later. |
| `enablePricingProcParallelization` | boolean | Indicates whether to run pricing elements in parallel within a pricing procedure to optimize the performance of the pricing execution process (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| `enablePricingWaterfall` | boolean | Indicates whether to enable Price Waterfall (`true`) or not (`false`). The default value is `false`. Price Waterfall provides insights that include price breakups and reasons for every step of the pricing process. |
| `enablePricingWaterfallPersistence` | boolean | Indicates whether to enable Price Waterfall Persistence (`true`) or not (`false`). The default value is `false`. Price Waterfall Persistence stores the process logs that provide insights into the internal pricing processes. |
| `enableSalesforcePricing` | boolean | Indicates whether to enable Salesforce Pricing (`true`) or not (`false`). The default value is `false`. |

## Declarative Metadata Sample Definition

This example shows a sample IndustriesPricingSettings component.

```
<IndustriesPricingSettings xmlns="http://soap.sforce.com/2006/04/metadata">
     <enableDebugPriceLogs>true</enableDebugPriceLogs>
     <enableHighAvailability>true</enableHighAvailability>
     <enableHighestPriceCompliance>true</enableHighestPriceCompliance>
     <enableLowestPriceCompliance>true</enableLowestPriceCompliance>
     <enablePricingProcParallelization>true</enablePricingProcParallelization>
     <enablePricingWaterfall>true</enablePricingWaterfall>
     <enablePricingWaterfallPersistence>true</enablePricingWaterfallPersistence>
     <enableSalesforcePricing>true</enableSalesforcePricing>
</IndustriesPricingSettings>
```

This example shows a sample `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>IndustriesPricing</members>
        <name>Settings</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the `package.xml` manifest file doesn’t apply to metadata types for feature settings. The wildcard applies only when retrieving all settings, not for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_settings.htm). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-industriespricingsettings.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
