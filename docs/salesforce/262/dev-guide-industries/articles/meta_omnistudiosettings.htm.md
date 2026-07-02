---
page_id: meta_omnistudiosettings.htm
title: OmniStudioSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omnistudiosettings.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniStudioSettings

Represents the settings that help administrators turn on
specific Omnistudio features and capabilities at the organization level.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed
using the “Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

OmniStudioSettings values are stored in the .settings
file in the settings folder. The .settings
files are different from other named components, because there is only one settings
file for each settings component.

## Version

OmniStudioSettings components are available in API version 64.0 and later.

## Special Access Rules

## Fields

| Field Name | Description |
| --- | --- |
| disableRollbackFlagsPref | Field Type  boolean  Description  Indicates whether to turn on rollback flag preferences for Omnistudio settings (`true`) or not (`false`). The default value is`false`. When enabled, rollback flags are disabled to prevent automatic rollback of configuration changes. This setting helps retain designer settings during upgrades and provides control over rollback behavior for Omnistudio configurations. It works in conjunction with the `RetainDesignerSettingOnUpgrade` setting to manage upgrade behavior. |
| enableOaEventInternalWrites | Field Type  boolean  Description  Indicates whether to turn on internal write operations for Omnistudio events (`true`) or not (`false`). The default value is`false`. This setting manages internal event handling, and controls how Omnistudio processes and stores event data. It also enables internal event persistence and processing capabilities for Omnistudio applications. |
| enableOaEventNotifications | Field Type  boolean  Description  Indicates whether to turn on the Omnistudio event notification system (`true`) or not (`false`). The default value is `false`. This setting manages notifications for Omnistudio events, and enables real-time communication and alerts for application activities. It supports platform events, custom notifications, and integration with Salesforce notification systems. |
| enableOaForCore | Field Type  boolean  Description  Indicates whether to turn on Omnistudio core builder functionality and the standard Omnistudio designer experience (`true`) or not (`false`). The default value is `false`. This setting is important for organizations that use managed packages with specific namespace requirements (omnistudio, vlocity\_cmt, vlocity\_ins, vlocity\_ps) and version constraints that are greater than v63.0. |
| enableOmniGlobalAutoNumberPref | Field Type  boolean  Description  Indicates whether to turn on global auto-numbering preferences for Omnistudio (`true`) or not (`false`). The default value is `false`. This setting controls the automatic generation and management of sequential numbers for Omnistudio components and records. It also provides centralized auto-numbering management for consistent record identification across all Omnistudio components. |
| enableOmniStudioContentTest | Field Type  boolean  Description  Indicates whether to turn on Omnistudio content testing capabilities (`true`) or not (`false`). The default value is `false`. When enabled, users can test Omnistudio content and configurations within the platform. This setting supports testing of OmniScripts, Flexcards, DataRaptors, and Integration Procedures in a controlled environment. It’s typically used for development and quality assurance to validate content before deployment. Available in API version 65.0 and later. |
| enableOmniStudioDrVersion | Field Type  boolean  Description  Indicates whether to turn on Omnistudio Data Mapper version functionality within Omnistudio (`true`) or not (`false`). The default value is `false`. Omnistudio Data Mapper version management features are essential for data transformation and integration workflows. This setting also enables version control for Omnistudio Data Mapper transformations, allowing organizations to maintain multiple versions of data mapping configurations. |
| enableOmniStudioMetadata | Field Type  boolean  Description  Indicates whether to turn on metadata functionality in the organization (`true`) or not (`false`). The default value is `false`. When enabled, the organization can access and manage Omnistudio metadata components through the Metadata and Tooling API. This setting can’t be enabled if metadata component unique names contain spaces or special characters. After it’s enabled, the setting can’t be disabled. |
| enableStandardOmniStudioRuntime | Field Type  boolean  Description  Indicates whether to enable the standard Omnistudio runtime environment (`true`) or not (`false`). The default value is `false`. When enabled, the standard runtime engine processes Omnistudio applications and content. This setting supports migration from managed-package Omnistudio runtimes to the standard runtime. This setting requires Omnistudio managed package to be properly configured. Available in API version 65.0 and later. |

## Declarative Metadata Sample Definition

This example shows a sample OmniStudioSettings component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniStudioSettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <enableOmniStudioMetadata>true</enableOmniStudioMetadata>
    <enableOmniStudioContentTest>false</enableOmniStudioContentTest>
    <enableStandardOmniStudioRuntime>false</enableStandardOmniStudioRuntime><enableOmniStudioDrVersion>false</enableOmniStudioDrVersion>
    <enableOaForCore>false</enableOaForCore>
    <enableOaEventNotifications>false</enableOaEventNotifications>
    <enableOaEventInternalWrites>false</enableOaEventInternalWrites>
    <enableOmniGlobalAutoNumberPref>true</enableOmniGlobalAutoNumberPref>
    <disableRollbackFlagsPref>false</disableRollbackFlagsPref>
</OmniStudioSettings>
```

Here's an example `package.xml` that references the
previous definition.

```
<?xml version="1.0" encoding="UTF-8"?><Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>OmniStudio</members>
        <name>Settings</name>
    </types>
    <version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

The wildcard character `*` (asterisk) in the
package.xml manifest file doesn’t apply to metadata types
for feature settings. The wildcard applies only when retrieving all settings, not
for an individual setting. For details, see [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)"). For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
