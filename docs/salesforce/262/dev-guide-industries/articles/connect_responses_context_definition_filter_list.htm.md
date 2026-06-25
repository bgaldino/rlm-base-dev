---
page_id: connect_responses_context_definition_filter_list.htm
title: Context Definition Filter List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_filter_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Definition Filter List

Output representation details of context definition filter list.

JSON example
:   ```
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

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionFilterList` | [Context Definition Filter](./connect_responses_context_definition_filter.htm.md "Output representation details of a context definition filter.")[] | List of context definition filters. | Small, 65.0 | 65.0 |
| `contextDefinitionFilterListId` | String | ID of the context definition filter list. | Small, 65.0 | 65.0 |
| `contextDefinitionId` | String | ID of the context definition. | Small, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 65.0 | 65.0 |
