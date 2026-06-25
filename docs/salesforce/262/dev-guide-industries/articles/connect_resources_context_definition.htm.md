---
page_id: connect_resources_context_definition.htm
title: Context Definition (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_definition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_context_definition_management.htm
fetched_at: 2026-06-25
---

# Context Definition (GET, POST)

Create a context definition, clone an existing context definition, extend a standard
definition (file based definition) or to persist entire context definition.

Resource
:   ```
    /connect/context-definitions
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   GET, POST

Response body for GET
:   [Context Definition List](./connect_responses_context_definition_list.htm.md "Output representation of list of context definitions.")

Request body for POST
:   JSON example
    :   ```
        {
           "name":"Example Definition",
           "description":"Example Description",
           "developerName":"John Doe",
           "startDate":"2023-06-02T00:00:00.000Z",
           "endDate":"2025-06-20T00:00:00.000Z",
           "isActive":false,
           "payload":"{\"contextDefinition\":{\"name\":\"ExampleDefinition\",\"description\":\"Example Description\",\"developerName\":\"ExampleDefinition\",\"contextDefinitionVersionList\":[{\"contextDefinitionVersion\":{\"isActive\":\"TRUE\",\"startDate\":\"2023-06-02T00:00:00.000Z\",\"endDate\":\"2025-06-20T00:00:00.000Z\",\"contextNodes\":[{\"name\":\"Claim\",\"isTransposable\":\"TRUE\",\"contextNodeId\":\"$param_claimId\",\"attributes\":[{\"dataType\":\"STRING\",\"type\":\"INPUT\",\"isFinal\":\"TRUE\",\"isKey\":\"false\",\"isValue\":\"true\",\"contextAttributeId\":\"$param_claimaccountId\",\"name\":\"Account\",\"contextTagList\":[{\"name\":\"ClaimAccount\"}]}],\"nodeChildren\":[{\"name\":\"ClaimItem\",\"isTransposable\":\"TRUE\",\"contextNodeId\":\"$param_claimItemId\",\"attributes\":[{\"dataType\":\"STRING\",\"type\":\"INPUT\",\"isFinal\":\"TRUE\",\"isKey\":\"FALSE\",\"isValue\":\"FALSE\",\"contextAttributeId\":\"$param_assetId\",\"name\":\"Asset\",\"contextTagList\":[{\"name\":\"ClaimItemAsset\"}]}],\"contextTagList\":[{\"contextNodeId\":\"$param_claimItemId\",\"name\":\"ClaimItem\"}]}],\"contextTagList\":[{\"contextNodeId\":\"$param_claimId\",\"name\":\"Claim\"}]}],\"contextMapping\":[{\"name\":\"Claim Order Mapping\",\"isDefault\":\"TRUE\",\"contextNodeMappings\":[{\"contextNodeId\":\"$param_claimId\",\"sObjectName\":\"Claim\",\"contextAttributeMappings\":[{\"contextAttributeId\":\"$param_claimaccountId\",\"hydrationSource\":\"SObject\",\"contextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Claim\",\"queryAttribute\":\"Account\",\"parentContextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Account\",\"queryAttribute\":\"Name\"}]}]}]},{\"contextNodeId\":\"$param_claimItemId\",\"sObjectName\":\"ClaimItem\",\"contextAttributeMappings\":[{\"contextAttributeId\":\"$param_assetId\",\"hydrationSource\":\"SObject\",\"contextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"ClaimItem\",\"queryAttribute\":\"Asset\",\"parentContextSObjectHydrationInfoList\":[{\"sObjectDomain\":\"Asset\",\"queryAttribute\":\"Name\"}]}]}]}]}]}}]}}",
           "sourceDefinitionId":"11Oxx0000007MnhEAE",
           "contextTtl":30
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextTtl` | Integer | Time to live (TTL) of context. | Optional | 59.0 |
        | `description` | String | Short description of context definition. | Optional | 59.0 |
        | `developerName` | String | Developer name. | Required | 59.0 |
        | `endDate` | String | End date till context definition is valid. | Optional | 59.0 |
        | `isActive` | Boolean | Specifies whether context is active (`true`) or not (`false`). | Optional | 59.0 |
        | `name` | String | Name of the context definition. | Required | 59.0 |
        | `payload` | String | JSON payload containing all the definitions and mappings. | Optional | 59.0 |
        | `sourceDefinitionId` | String | Source context definition ID. | Optional | 59.0 |
        | `startDate` | String | Start date from when context definition is valid. | Required | 59.0 |

Response body for POST
:   [Context Definition Information](./connect_responses_context_definition_info.htm.md "Output representation of context definition information.")
