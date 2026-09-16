---
page_id: connect_requests_context_definition_filter_list_input.htm
title: Context Definition Filter List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_filter_list_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Filter List Input

Input representation for a list of Context Definition Filters

**JSON example**

: 

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

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filters` | [Context Definition Filter Input](./connect_requests_context_definition_filter_input.htm.md)[] | List of context definition filter inputs. | Required | 65.0 |
