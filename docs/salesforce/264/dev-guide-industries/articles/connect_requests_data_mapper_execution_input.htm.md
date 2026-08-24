---
page_id: connect_requests_data_mapper_execution_input.htm
title: Data Mapper Execution Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execution_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Data Mapper Execution Input

Input representation of the execution details of a data mapper.

**JSON example**

: 
            

```
{
  "dataMapperInput": {
    "inputs": [
      {
        "Name": "Get Account Details"
      }
    ]
  },
  "inputType": "JSON",
  "options": {
    "ignoreCache": false
  }
}
```

          

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `dataMapperInput` | [Data Mapper Execute Input Data](./connect_requests_data_mapper_execute_input_data.htm.md) | Details for executing the data mapper. | Required | 64.0 |
| `inputType` | String | Type of data mapper input. For example, JSON, XML, or custom class. | Required | 64.0 |
| `options` | [Data Mapper Execution Options](./connect_requests_data_mapper_execution_options.htm.md) | Optional parameters to refine the data mapper execution. | Optional | 64.0 |
