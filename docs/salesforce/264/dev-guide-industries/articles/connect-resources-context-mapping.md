---
page_id: connect-resources-context-mapping
title: Context Mapping (POST, PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-mapping.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-mapping-management
legacy_page_id: connect_resources_context_mapping.htm
fetched_at: 2026-11-25
---

# Context Mapping (POST, PATCH)

Create and update context mappings.

## Resource

```
/connect/context-definitions/{contextDefinitionId}/context-mappings
```

The {contextDefinitionId} parameter is the ID of the context definition.

## Example for POST

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-mappings
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}/context-mappings
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

### Properties

- 
- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextMappingId` | String | ID of this context mapping. Required for update. | Required | 59.0 |
| `contextNodeMappings` | Context Node Mappings Input[] | List of context node mappings. | Optional | 59.0 |
| `description` | String | Description of context mapping. | Optional | 59.0 |
| `isDefault` | Boolean | Indicates whether to make a default mapping for the context definition (`true`) or not (`false`). | Optional | 59.0 |
| `intents` | List<String> | Purpose that’s used to identify the type of required context mapping. Valid values are: `HYDRATION`—To load cache from a data source.`PERSISTENCE`—To load the sink objects from cache. Sink objects are the final destinations for the processed data.`ASSOCIATION`—To create a mapping without validating database relationships, attaching context structure nodes and their attributes with data source nodes and their attributes.`TRANSLATION`—To transform the data loaded in the cache to another representation defined by the mapping. | Optional | 61.0 |
| `name` | String | Name of the context mapping. | Required | 59.0 |

## Response Body for POST

[Context Mapping List Output](./connect-responses-context-mapping-list.md)

## Request Body for PATCH

### JSON Example

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

## Response Body for PATCH

[Context Mapping List Output](./connect-responses-context-mapping-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-mapping.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
