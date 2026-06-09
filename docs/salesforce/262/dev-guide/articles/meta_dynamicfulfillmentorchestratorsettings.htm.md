---
page_id: meta_dynamicfulfillmentorchestratorsettings.htm
title: DynamicFulfillmentOrchestratorSettings
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_dynamicfulfillmentorchestratorsettings.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# DynamicFulfillmentOrchestratorSettings

Represents the settings for Dynamic
Revenue Orchestrator.

## Parent Type and Manifest Access

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

In the package manifest, all the settings metadata types for the org are accessed using the
“Settings” name. See [Settings](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/meta_settings.htm "HTML (New Window)") for more details.

## File Suffix and Directory Location

DynamicFulfillmentOrchestratorSettings values are stored in the
DynamicFulfillmentOrchestratorSettings.settings file in the
settings folder. The .settings files
are different from other named components, because there is only one settings file
for each settings component.

## Version

DynamicFulfillmentOrchestratorSettings components are available in API version 61.0 and
later.

## Fields

| Field Name | Description |
| --- | --- |
| enableDFOFallout | Field Type  boolean  Description  Indicates whether to enable fallout management to handle fallouts and retry policies (`true`) or not (`false`). The default value is `false`. See [Turn On Feature to Manage Fallout](https://help.salesforce.com/s/articleView?id=ind.dro_turn_on_features_to_manage_fallout_and_service_level_agreements.htm&language=en_US "HTML (New Window)"). |
| enableDFOJeopardy | Field Type  boolean  Description  Indicates whether to enable management of Service Level Agreements (`true`) or not (`false`). The default value is `false`. See [Turn On Feature to Manage Service Level Agreements](https://help.salesforce.com/s/articleView?id=ind.dro_turn_on_features_to_manage_fallout_and_service_level_agreements.htm&language=en_US "HTML (New Window)"). |
| enableDFOPref | Field Type  boolean  Description  Indicates whether to enable features of Dynamic Revenue Orchestrator (`true`) or not (`false`). The default value is `false`. See [Turn On Dynamic Revenue Orchestrator](https://help.salesforce.com/s/articleView?id=ind.dro_turn_on_dynamic_revenue_orchestrator.htm&language=en_US "HTML (New Window)"). |
| enableDROFutureDatedTasks | Field Type  boolean  Description  Indicates whether to enable the Future Dated Steps feature (`true`) or not (`false`). The default value is `false`. See [Enable Future Dated Steps](https://help.salesforce.com/s/articleView?id=ind.enable_future_dated_steps.htm&language=en_US). Available in API version 63.0 and later. |
| enableDROInflightRequest | Field Type  boolean  Description  Indicates whether to allow changes to fulfillment requests that are in progress (`true`) or not (`false`). The default value is `false`. Available in API version 64.0 and later. |
| enableDROTaskSource | Field Type  boolean  Description  Indicates whether to link a Salesforce manual task to a fulfillment step source (`true`) or not (`false`). The default value is `false`. See [Enable the Linking of Task to Step Source](https://help.salesforce.com/s/articleView?id=ind.dro_turn_on_feature_to_link_task_to_step_source.htm&language=en_US "HTML (New Window)"). Available in API version 63.0 and later. |

## Declarative Metadata Sample Definition

The following is an example of a DynamicFulfillmentOrchestratorSettings component.

```
<DynamicFulfillmentOrchestratorSettings xmlns="http://soap.sforce.com/2006/04/metadata">
     <enableDFOPref>true</enableDFOPref>
     <enableDFOFallout>true</enableDFOFallout>
     <enableDFOJeopardy>true</enableDFOJeopardy>
     <enableDROFutureDatedTasks>true</enableDROFutureDatedTasks>
     <enableDROInflightRequest>true</enableDROInflightRequest>
     <enableDROTaskSource>true</enableDROTaskSource>
</DynamicFulfillmentOrchestratorSettings>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>DynamicFulfillmentOrchestrator</members>
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
