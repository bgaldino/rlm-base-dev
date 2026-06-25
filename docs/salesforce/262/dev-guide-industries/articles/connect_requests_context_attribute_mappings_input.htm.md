---
page_id: connect_requests_context_attribute_mappings_input.htm
title: Context Attribute Mappings Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_attribute_mappings_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Attribute Mappings Input

Input representation of context attribute mapping.

JSON example
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
