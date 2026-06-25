---
page_id: connect_resources_attribute_mapping.htm
title: Context Attribute Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_attribute_mapping.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_attribute_management.htm
fetched_at: 2026-06-25
---

# Context Attribute Mapping (POST, PATCH)

Create context attribute mapping. Update context attribute mapping.

Resource
:   ```
    /connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings
    ```

Example for PATCH
:   ```
    https://yourInstance.salesforce.com/services/data/v59.0/connect/context-node-mappings/${contextNodeMappingId}/context-attribute-mappings
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
            "contextAttributeMappings": [
                {
                    "contextAttributeId": "11nxx000001hIgLAAU",
                    "hydrationDetails": {
                        "contextAttrHydrationDetails": [
                            {
                                "sObjectDomain": "Order",
                                "queryAttribute": "Status"
                            }
                        ]
                    }
                },
                {
                    "contextAttributeId": "11nxx000001hKiFAAU",
                    "hydrationDetails": {
                        "contextAttrHydrationDetails": [
                            {
                                "sObjectDomain": "Order",
                                "queryAttribute": "Name"
                            }
                        ]
                    }
                }
            ]
        }
        ```
    :   This example shows a JSON sample when context-to-context mappings
        exist.
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
                            "contextAttrContextHydrationDetails": [
                              {
                                "queryAttribute": "11nxx000001hGTFAA2",
                                "parentAttributeMappingId": "11Rxx00000058LcEAI"
                              }
                            ]
                          },
                          "contextAttributeId": "11nxx000001ihzFAAQ",
                          "contextInputAttributeName": "Node1A1"
                        }
                      ]
                    },
                    "contextNodeId": "11oxx000001HS0iAAG",
                    "mappedContextNodeId": "11oxx000001G0mSAAS",
                    "sObjectName": "Node1"
                  }
                ]
              },
              "intents": [
                "ASSOCIATION",
                "HYDRATION",
                "PERSISTENCE",
                "TRANSLATION"
              ],
              "mappedContextDefinitionName": "11Oxx0000006PZ8EAM",
              "isDefault": false
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextAttributeId` | String | ID of the context attribute record. | Required | 59.0 |
        | `contextAttributeMappingId` | String | ID of the context attribute mapping record. | Required | 59.0 |
        | `contextInputAttributeName` | String | Context input attribute name. | Optional | 59.0 |
        | `hydrationDetails` | [Context Attribute Hydration Details Input](./connect_requests_context_attr_hydration_details_input.htm.md "Input representation of context attribute hydration detail.")[] | List of context attribute hydration detail. | Optional | 59.0 |

Response body for POST
:   [Context Attribute Mapping List Output](./connect_responses_context_attribute_mapping_list.htm.md "Output representation of list of context attribute mappings.")

Request body for PATCH
:   JSON example
    :   ```
        {
            "contextAttributeMappings": [
                {
                    "contextAttributeId": "11nxx000001hIgLAAU",
                    "hydrationDetails": {
                        "contextAttrHydrationDetails": [
                            {
                                "sObjectDomain": "Order",
                                "queryAttribute": "Status"
                            }
                        ]
                    }
                },
                {
                    "contextAttributeId": "11nxx000001hKiFAAU",
                    "hydrationDetails": {
                        "contextAttrHydrationDetails": [
                            {
                                "sObjectDomain": "Order",
                                "queryAttribute": "Name"
                            }
                        ]
                    }
                }
            ]
        }
        ```
    :   This example shows a JSON sample when context-to-context mappings
        exist.
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
                            "contextAttrContextHydrationDetails": [
                              {
                                "queryAttribute": "11nxx000001hGTFAA2",
                                "parentAttributeMappingId": "11Rxx00000058LcEAI"
                              }
                            ]
                          },
                          "contextAttributeId": "11nxx000001ihzFAAQ",
                          "contextInputAttributeName": "Node1A1"
                        }
                      ]
                    },
                    "contextNodeId": "11oxx000001HS0iAAG",
                    "mappedContextNodeId": "11oxx000001G0mSAAS",
                    "sObjectName": "Node1"
                  }
                ]
              },
              "intents": [
                "ASSOCIATION",
                "HYDRATION",
                "PERSISTENCE",
                "TRANSLATION"
              ],
              "mappedContextDefinitionName": "11Oxx0000006PZ8EAM",
              "isDefault": false
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `contextAttributeId` | String | ID of the context attribute record. | Required | 59.0 |
        | `contextAttributeMappingId` | String | ID of the context attribute mapping record. | Required | 59.0 |
        | `contextInputAttributeName` | String | Context input attribute name. | Optional | 59.0 |
        | `hydrationDetails` | [Context Attribute Hydration Details Input](./connect_requests_context_attr_hydration_details_input.htm.md "Input representation of context attribute hydration detail.")[] | List of context attribute hydration detail. | Optional | 59.0 |

Response body for PATCH
:   [Context Attribute Mapping List](./connect_responses_context_attribute_mapping_list.htm.md "Output representation of list of context attribute mappings.")
