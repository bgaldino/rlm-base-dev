---
page_id: connect-requests-context-mappings-input
title: Context Mappings Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-mappings-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-requests
legacy_page_id: connect_requests_context_mappings_input.htm
fetched_at: 2026-11-25
---

# Context Mappings Input

Input representation of context mapping.

## JSON Example

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

## Properties

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-context-mappings-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
