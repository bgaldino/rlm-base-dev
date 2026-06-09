---
page_id: meta_industriespricingsettings.htm
title: IndustriesPricingSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_industriespricingsettings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# IndustriesPricingSettings

Represents the settings for Salesforce
Pricing.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed using the
“Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

IndustriesPricingSettings values are stored in the
IndustriesPricingSettings.settings file in the
settings folder. The .settings files
are different from other named components, because there’s only one settings file
for each settings component.

## Version

IndustriesPricingSettings components are available in API version 60.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Description |
| --- | --- |
| enableDebugPriceLogs | Field Type  boolean  Description  Indicates whether to use price logs to diagnose and resolve pricing issues (`true`) or not (`false`). The default value is `false`. Available in API version 63.0 and later. |
| enableHighAvailability | Field Type  boolean  Description  Reserved for internal use. |
| enableHighestPriceCompliance | Field Type  boolean  Description  Indicates whether to track the maximum price of a product over a period of 30 days (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| enableLowestPriceCompliance | Field Type  boolean  Description  Indicates whether to track the minimum price of a product over a period of 30 days (`true`) or not (`false`). The default value is `false`. Available in API version 62.0 and later. |
| enablePricingProcParallelization | Field Type  boolean  Description  Indicates whether to run pricing elements in parallel within a pricing procedure to optimize the performance of the pricing execution process (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| enablePricingWaterfall | Field Type  boolean  Description  Indicates whether to enable Price Waterfall (`true`) or not (`false`). The default value is `false`. Price Waterfall provides insights that include price breakups and reasons for every step of the pricing process. |
| enablePricingWaterfallPersistence | Field Type  boolean  Description  Indicates whether to enable Price Waterfall Persistence (`true`) or not (`false`). The default value is `false`. Price Waterfall Persistence stores the process logs that provide insights into the internal pricing processes. |
| enableSalesforcePricing | Field Type  boolean  Description  Indicates whether to enable Salesforce Pricing (`true`) or not (`false`). The default value is `false`. |

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

This example shows a sample `package.xml` that references
the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>IndustriesPricing</members>
        <name>Settings</name>
    </types>
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the
package.xml manifest file doesn’t apply to metadata types
for feature settings. The wildcard applies only when retrieving all settings, not
for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)"). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
