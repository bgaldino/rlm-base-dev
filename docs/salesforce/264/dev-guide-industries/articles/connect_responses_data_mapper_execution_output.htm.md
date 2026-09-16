---
page_id: connect_responses_data_mapper_execution_output.htm
title: Data Mapper Execution Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_data_mapper_execution_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Data Mapper Execution Details

Output representation of the execution details of a data mapper.

        
          

**JSON example**

          
: 
            

```
{
  "response": [
    {
      "error": "Specify a Data Mapper name",
      "response": [
        {
          "status": false
        }
      ],
      "responseType": "JSON"
    }
  ],
  "status": "Success"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              
- 
- 

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution fails. | Small, 64.0 | 64.0 |
| `response` | [Data Mapper Execution Response](./connect_responses_data_mapper_execution_response_output.htm.md) [] | List of responses corresponding to the custom inputs that are provided during the data mapper execution. | Small, 64.0 | 64.0 |
| `status` | String | Execution status of the data mapper. Valid values are: `Error`—Data mapper execution has failed due to an error. `Success`—Data mapper execution is successful. | Small, 64.0 | 64.0 |
