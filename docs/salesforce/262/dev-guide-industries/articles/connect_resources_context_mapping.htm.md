---
page_id: connect_resources_context_mapping.htm
title: Context Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_context_mapping.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_mapping_management.htm
fetched_at: 2026-06-25
---

# Context Mapping (POST, PATCH)

Create and update context mappings.

Resource
:   ```
    /connect/context-definitions/${contextDefinitionId}/context-mappings
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-mappings
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-definitions/${contextDefinitionId}/context-mappings
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST, PATCH

Request body for POST
:   JSON example
    :   ```
        {
          "contextMappings": [
            {
              "name": "ExampleMapping",
              "description": "Example Mapping Description",
              "isDefault": true,
              "intents": [
                "ASSOCIATION",
                "HYDRATION",
                "PERSISTENCE",
                "TRANSLATION"
              ]
            }
          ],
          "generateInputMappings": false,
          "generateSObjectMappings": false
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextMappingId` | String | ID of this context mapping. Required for update. | Required | 59.0 |
        | `contextNodeMappings` | Context Node Mappings Input[] | List of context node mappings. | Optional | 59.0 |
        | `description` | String | Description of context mapping. | Optional | 59.0 |
        | `isDefault` | Boolean | Indicates whether to make a default mapping for the context definition (`true`) or not (`false`). | Optional | 59.0 |
        | `intents` | List<String> | Purpose that's used to identify the type of required context mapping. Valid values are:   - `HYDRATION`—To load cache from a   data source. - `PERSISTENCE`—To load the sink   objects from cache. Sink objects are the final   destinations for the processed data. - `ASSOCIATION`—To create a mapping   without validating database relationships,   attaching context structure nodes and their   attributes with data source nodes and their   attributes. - `TRANSLATION`—To transform the data   loaded in the cache to another representation   defined by the mapping. | Optional | 61.0 |
        | `name` | String | Name of the context mapping. | Required | 59.0 |

Response body for POST
:   [Context Mapping List Output](./connect_responses_context_mapping_list.htm.md "Output representation of a list of context mappings.")

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextMappings": [
              {
                "contextMappingId": "11jxx0000005UXnAAM",
                "contextNodeMappings": {
                  "contextNodeMappings": [
                    {
                      "attributeMappings": {
                        "contextAttributeMappings": [
                          {
                            "hydrationDetails": {
                              "contextAttrHydrationDetails": []
                            },
                            "contextAttributeId": "11nxx000001ihzFAAQ",
                            "contextInputAttributeName": "Node1A1"
                          }
                        ]
                      },
                      "contextNodeId": "11oxx000001HS0iAAG",
                      "sObjectName": "Node1"
                    }
                  ]
                }
              }
            ]
          }
        ```

Response body for PATCH
:   [Context Mapping List Output](./connect_responses_context_mapping_list.htm.md "Output representation of a list of context mappings.")
