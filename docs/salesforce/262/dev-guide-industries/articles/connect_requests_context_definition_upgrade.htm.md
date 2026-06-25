---
page_id: connect_requests_context_definition_upgrade.htm
title: Context Definition Upgrade Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_upgrade.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Definition Upgrade Input

Input representation of context definition upgrade.

JSON example
:   ```
    {
      "contextDefinitions": [
        {
          "contextDefinitionId": "11Oxx0000006PfZEAU",
          "upgradeMode": "Sync"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextDefinitionId` | String | ID of this context definition to be upgraded. | Required | 64.0 |
    | `upgradeMode` | String | The upgrade mode enum. Possible values are:  - Sync - Preview - OverrideThe default value   is Sync. | Optional | 64.0 |
