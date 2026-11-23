---
page_id: connect_requests_context_definition_filter_list_input.htm
title: Context Definition Filter List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_list_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Context Definition Filter List Input

Input representation for a list of Context Definition Filters

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filters` | [Context Definition Filter Input](./connect_requests_context_definition_filter_input.htm.md "Input representation details of context definition filter.")[] | List of context definition filter inputs. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_list_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
