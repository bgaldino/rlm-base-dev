---
page_id: meta_industriesratingsettings.htm
title: IndustriesRatingSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_industriesratingsettings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# IndustriesRatingSettings

Represents the settings for Rate
Management.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed using the
“Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

The IndustriesRatingSettings values are stored in the
IndustriesRating.settings file in the
settings folder. The .settings files
are different from other named components, because there’s only one settings file
for each settings component.

## Version

IndustriesRatingSettings components are available in API version 62.0 and later.

## Special Access Rules

This metadata type is available with Rate Management.

## Fields

| Field Name | Description |
| --- | --- |
| enableRating | Field Type  boolean  Description  Indicates whether to enable Rate Management (`true`) or not (`false`). The default value is `false`. |
| enableRatingWaterfall | Field Type  boolean  Description  Indicates whether to enable Rating Waterfall (`true`) or not (`false`). The default value is `false`. Rating Waterfall provides insights into the rating data, which you can synchronize with your rating lookup tables. |
| enableRatingWaterfallPersistence | Field Type  boolean  Description  Indicates whether to enable Rating Waterfall Persistence (`true`) or not (`false`). The default value is `false`. Rating Waterfall Persistence stores rating data, which you can use to enhance the internal processes and increase efficiency. |

## Declarative Metadata Sample Definition

The following is an example of an IndustriesRatingSettings component.

```
<IndustriesRatingSettings xmlns="http://soap.sforce.com/2006/04/metadata">
     <enableRating>true</enableRating>
     <enableRatingWaterfall>true</enableRatingWaterfall> 
     <enableRatingWaterfallPersistence>true</enableRatingWaterfallPersistence>
</IndustriesRatingSettings>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>IndustriesRating</members>
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
