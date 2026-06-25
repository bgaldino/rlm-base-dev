---
page_id: connect_resources_context_definition_upgrades.htm
title: Context Definition Upgrade (PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition_upgrades.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-06-25
---

# Context Definition Upgrade (PATCH)

Upgrade a context definition. Once an extended definition is created from a base
standard definition, use this API to reflect any updates made to the base standard
definition in the extended definition.

Resource
:   ```
    /connect/context-definitions/upgrades
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v64.0/connect/context-definitions/upgrades
    ```

Available version
:   64.0

HTTP methods
:   PATCH

Request body for PATCH
:   JSON example
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

Response body for PATCH
:   [Context Definition Information](./connect_responses_context_definition_info.htm.md "Output representation of context definition information.")
