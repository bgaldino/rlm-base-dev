---
page_id: connect_requests_context_definition_filter_input.htm
title: Context Definition Filter Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Context Definition Filter Input

Input representation details of context definition filter.

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionVersionId` | String | Unique identifier of the specific context definition version to which this filter belongs. | Required | 65.0 |
| `description` | String | Details of the context definition filter such as the purpose of the filter. Use this field to document the filter's business logic, intended use case, or any important implementation details for future reference. | Optional | 65.0 |
| `filterApiName` | String | Unique API name identifier for the context definition filter. | Required | 65.0 |
| `filterName` | String | Display name for the context definition filter. | Required | 65.0 |
| `filtersPerNode` | String | A JSON string representation of the filter condition logic that defines the filter criteria. This field contains the structured query conditions that's evaluated to determine which records match the filter. The JSON structure typically includes field names, operators, and values that form the filter expression. | Required | 65.0 |
| `inheritedFrom` | String | Source context definition if filter is inherited in the GET request. This field is not applicable for POST request. | Optional | 65.0 |

## JSON Example

This example shows a sample request to
create, get, or update a context definition filter.

```
{
      "description": "Updated",
      "filterApiName": "FilterAccount",
      "filterName":"FilterAccount",
      "filtersPerNode": "{\"Account\":{\"filterCondition\":{\"attribute\":\"City\",\"operator\":\"EQUALS\",\"operands\":[{\"value\":\"Bengaluru\",\"type\":\"STRING\"}],\"composite\":false},\"orderByConditions\":[{\"orderByAttribute\":\"Name\",\"ascending\":false,\"nullsFirst\":false}],\"limit\":5}}",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE"
    }
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
