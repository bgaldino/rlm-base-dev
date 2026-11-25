---
page_id: meta-industriesusagesettings
title: IndustriesUsageSettings
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-industriesusagesettings.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-metadata-api-parent
legacy_page_id: meta_industriesusagesettings.htm
fetched_at: 2026-11-25
---

# IndustriesUsageSettings

Represents the settings for Usage Management.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

In the package manifest, all the settings metadata types for the org are accessed using the “Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_settings.htm) for more details.

## File Suffix and Directory Location

`IndustriesUsageSettings` values are stored in the `IndustriesUsage.settings` file in the `settings` folder. The `.settings` files are different from other named components, because there is only one settings file for each settings component.

## Version

IndustriesUsageSettings components are available in API version 63.0 and later.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| `enableUsage` | boolean | Indicates whether to create and access Usage Management objects to manage product usage and determine rates based on usage (`true`) or not (`false`). The default value is `false`. |

## Declarative Metadata Sample Definition

The following is an example of an IndustriesUsageSettings component.

```
<?xml version="1.0" encoding="UTF-8"?>
<IndustriesUsageSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <enableUsage>true</enableUsage>
</IndustriesUsageSettings>
```

The following is an example `package.xml` that references the previous definition.

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

The wildcard character `*` (asterisk) in the `package.xml` manifest file doesn’t apply to metadata types for feature settings. The wildcard applies only when retrieving all settings, not for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_settings.htm). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/meta-industriesusagesettings.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
