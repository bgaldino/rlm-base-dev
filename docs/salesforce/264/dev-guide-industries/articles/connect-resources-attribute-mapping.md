---
page_id: connect-resources-attribute-mapping
title: Context Attribute Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-attribute-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-attribute-management
legacy_page_id: connect_resources_attribute_mapping.htm
fetched_at: 2026-11-25
---

# Context Attribute Mapping (POST, PATCH)

Create context attribute mapping. Update context attribute mapping.

## Resource

```
/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings
```

The {contextNodeMappingId} parameter is the ID of the context node mapping.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-node-mappings/{contextNodeMappingId}/context-attribute-mappings
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

POST, PATCH

## Request Body for POST

### JSON Example

```
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

This example shows a JSON sample when context-to-context mappings exist.

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the context attribute record. | Required | 59.0 |
| `contextAttributeMappingId` | String | ID of the context attribute mapping record. | Required | 59.0 |
| `contextInputAttributeName` | String | Context input attribute name. | Optional | 59.0 |
| `hydrationDetails` | [Context Attribute Hydration Details Input](./connect-requests-context-attr-hydration-details-input.md)[] | List of context attribute hydration detail. | Optional | 59.0 |

## Response Body for POST

[Context Attribute Mapping List Output](./connect-responses-context-attribute-mapping-list.md)

## Request Body for PATCH

### JSON Example

```
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

This example shows a JSON sample when context-to-context mappings exist.

```
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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextAttributeId` | String | ID of the context attribute record. | Required | 59.0 |
| `contextAttributeMappingId` | String | ID of the context attribute mapping record. | Required | 59.0 |
| `contextInputAttributeName` | String | Context input attribute name. | Optional | 59.0 |
| `hydrationDetails` | [Context Attribute Hydration Details Input](./connect-requests-context-attr-hydration-details-input.md)[] | List of context attribute hydration detail. | Optional | 59.0 |

## Response Body for PATCH

[Context Attribute Mapping List](./connect-responses-context-attribute-mapping-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-attribute-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
