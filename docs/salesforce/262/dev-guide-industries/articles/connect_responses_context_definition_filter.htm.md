---
page_id: connect_responses_context_definition_filter.htm
title: Context Definition Filter
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_filter.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Definition Filter

Output representation details of a context definition filter.

JSON example
:   This example shows a sample response for the Context Definition Filter by ID (GET)
    request.

    ```
    {
      "contextDefinitionFilterId": "1Tlxx0000004DUuCAM",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE",
      "filterName": "FilterAccount2",
      "filterApiName": "FilterAccount2",
      "filtersPerNode": "{&quot;Account&quot;:{&quot;filterCondition&quot;:{&quot;attribute&quot;:&quot;City&quot;,&quot;operator&quot;:&quot;EQUALS&quot;,&quot;operands&quot;:[{&quot;value&quot;:&quot;Bengaluru&quot;,&quot;type&quot;:&quot;STRING&quot;}],&quot;composite&quot;:false},&quot;orderByConditions&quot;:[{&quot;orderByAttribute&quot;:&quot;Name&quot;,&quot;ascending&quot;:false,&quot;nullsFirst&quot;:false}],&quot;limit&quot;:5}}"
      "isSuccess": true
    }
    ```
:   This example shows a sample response for the Context Definition Filter By ID (PATCH)
    request.

    ```
    {
      "contextDefinitionFilterId": "1Tlxx0000004DUuCAM",
      "contextDefinitionVersionId": "11pxx0000004VmmAAE",
      "description": "Updated",
      "filterName": "FilterAccount2",
      "filterApiName": "FilterAccount2",
      "filtersPerNode": "{&quot;Account&quot;:{&quot;filterCondition&quot;:{&quot;attribute&quot;:&quot;City&quot;,&quot;operator&quot;:&quot;EQUALS&quot;,&quot;operands&quot;:[{&quot;value&quot;:&quot;Bengaluru&quot;,&quot;type&quot;:&quot;STRING&quot;}],&quot;composite&quot;:false},&quot;orderByConditions&quot;:[{&quot;orderByAttribute&quot;:&quot;Name&quot;,&quot;ascending&quot;:false,&quot;nullsFirst&quot;:false}],&quot;limit&quot;:5}}",
      "isSuccess": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionFilterId` | String | ID of the context definition filter. | Small, 65.0 | 65.0 |
| `contextDefinitionVersionId` | String | Unique identifier of the specific context definition version to which this filter belongs. | Small, 65.0 | 65.0 |
| `description` | String | Details of the context definition filter such as the purpose of the filter. Use this field to document the filter's business logic, intended use case, or any important implementation details for future reference. | Small, 65.0 | 65.0 |
| `filterApiName` | String | Unique API name identifier for the context definition filter. | Small, 65.0 | 65.0 |
| `filterName` | String | Display name for the context definition filter. | Small, 65.0 | 65.0 |
| `filtersPerNode` | String | A JSON string representation of the filter condition logic that defines the filter criteria. This field contains the structured query conditions that's evaluated to determine which records match the filter. The JSON structure typically includes field names, operators, and values that form the filter expression. | Small, 65.0 | 65.0 |
| `inheritedFrom` | String | Source context definition if filter is inherited in the GET request. This field is not applicable for POST request. | Small, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 65.0 | 65.0 |
