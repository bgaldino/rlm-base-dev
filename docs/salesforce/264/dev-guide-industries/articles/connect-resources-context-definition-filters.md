---
page_id: connect-resources-context-definition-filters
title: Context Definition Filters (GET, POST)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-filters.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-context-definition-management
legacy_page_id: connect_resources_context_definition_filters.htm
fetched_at: 2026-11-25
---

# Context Definition Filters (GET, POST)

Create or get context filters associated with a specific context definition. Context filters are criteria or conditions that refine or limit data operations based on specific parameters.

## Resource

```
/connect/context-definitions/${contextDefinitionId}/context-filters
```

The `contextDefinitionId` property value is the unique identifier for the context definition whose filters you want to retrieve.

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/context-definitions/SimpleDef/context-filters
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

65.0

## HTTP Methods

GET, POST

## Response Body for GET

[Context Definition Filter List](./connect-responses-context-definition-filter-list.md)

## Request Body for POST

### JSON Example

```
{
  "filters": [
    {
      "filterApiName": "FilterAccount",
      "filterName":"FilterAccount",
      "filtersPerNode": "{\"Account\":{\"filterCondition\":{\"attribute\":\"City\",\"operator\":\"EQUALS\",\"operands\":[{\"value\":\"Bengaluru\",\"type\":\"STRING\"}],\"composite\":false},\"orderByConditions\":[{\"orderByAttribute\":\"Name\",\"ascending\":false,\"nullsFirst\":false}],\"limit\":5}}",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE"
    }
  ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filters` | [Context Definition Filter Input](./connect-requests-context-definition-filter-input.md)[] | List of context definition filter inputs. | Required | 65.0 |

## Response Body for POST

[Context Definition Filter List](./connect-responses-context-definition-filter-list.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-filters.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
