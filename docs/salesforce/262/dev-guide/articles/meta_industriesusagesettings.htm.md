---
page_id: meta_industriesusagesettings.htm
title: IndustriesUsageSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_industriesusagesettings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# IndustriesUsageSettings

Represents the settings for Usage Management.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed using the
“Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

IndustriesUsageSettings values are stored in the
IndustriesUsage.settings file in the
settings folder. The .settings files
are different from other named components, because there is only one settings file
for each settings component.

## Version

IndustriesUsageSettings components are available in API version 63.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
| enableUsage | Field Type  boolean  Description  Indicates whether to create and access Usage Management objects to manage product usage and determine rates based on usage (`true`) or not (`false`). The default value is `false`. |

## Declarative Metadata Sample Definition

The following is an example of an IndustriesUsageSettings component.

```
<?xml version="1.0" encoding="UTF-8"?>
<IndustriesUsageSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <enableUsage>true</enableUsage>
</IndustriesUsageSettings>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>IndustriesUsage</members>
        <name>Settings</name>
    </types>
    <version>[ftest]</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the
package.xml manifest file doesn’t apply to metadata types
for feature settings. The wildcard applies only when retrieving all settings, not
for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)"). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
