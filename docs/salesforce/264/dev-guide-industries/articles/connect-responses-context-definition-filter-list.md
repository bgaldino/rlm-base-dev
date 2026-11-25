---
page_id: connect-responses-context-definition-filter-list
title: Context Definition Filter List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-filter-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_context_definition_filter_list.htm
fetched_at: 2026-11-25
---

# Context Definition Filter List

Output representation details of context definition filter list.

## JSON Example

```
{
  "contextDefinitionFilterList": [
    {
      "contextDefinitionFilterId": "1Tlxx0000004DRgCAM",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE",
      "filterApiName": "FilterAccount"
      "filterName": "FilterAccount",
      "filtersPerNode": "{\n    &quot;Account&quot;: {\n      &quot;filterCondition&quot;: {\n        &quot;attribute&quot;: &quot;Name&quot;,\n        &quot;operator&quot;: &quot;EQUALS&quot;,\n        &quot;operands&quot;: [\n          {\n            &quot;value&quot;: &quot;Acme&quot;,&quot;type&quot;: &quot;STRING&quot;\n          }\n        ]\n      },\n      &quot;orderByConditions&quot;: [\n        {\n          &quot;orderByAttribute&quot;: &quot;Name&quot;,\n          &quot;ascending&quot;: false,\n          &quot;nullsFirst&quot;: false\n        }\n      ],\n      &quot;limit&quot;: 10\n    }\n  }"
    },
    {
      "contextDefinitionFilterId": "1Tlxx0000004DTICA2",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE",
      "filterName": "FilterContact",
      "filterApiName": "FilterContact",
      "filtersPerNode": "{\n    &quot;Contact&quot;: {\n      &quot;filterCondition&quot;: {\n        &quot;attribute&quot;: &quot;FirstName&quot;,\n        &quot;operator&quot;: &quot;EQUALS&quot;,\n        &quot;operands&quot;: [\n          {\n            &quot;value&quot;: &quot;Howard&quot;,&quot;type&quot;: &quot;STRING&quot;\n          }\n        ]\n      }\n  }\n  }"
    }
  ],
  "contextDefinitionFilterListId": "4dd6fda2-3fa0-4075-8f03-33a1288ef009",
  "contextDefinitionId": "SimpleDef",
  "isSuccess": true
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionFilterList` | [Context Definition Filter](./connect-responses-context-definition-filter.md)[] | List of context definition filters. | Small, 65.0 | 65.0 |
| `contextDefinitionFilterListId` | String | ID of the context definition filter list. | Small, 65.0 | 65.0 |
| `contextDefinitionId` | String | ID of the context definition. | Small, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-context-definition-filter-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
