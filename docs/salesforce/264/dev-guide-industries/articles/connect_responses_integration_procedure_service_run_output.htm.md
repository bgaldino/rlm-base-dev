---
page_id: connect_responses_integration_procedure_service_run_output.htm
title: Integration Procedure Execution Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_service_run_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Execution Details

Output representation of the execution details of the integration procedure.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "error": "Specify a valid IP name.",
  "response": [
    {
      "status": false
    }
  ],
  "status": "Error"
}
```

          

        
      

    

- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the execution of the integration procedure fails. | Small, 64.0 | 64.0 |
| `response` | String[] | List of responses for the execution of the integration procedures. | Small, 64.0 | 64.0 |
| `status` | String | Execution status of the integration procedure. Valid values are: `Error`—Execution has failed due to an error. `Success`—Execution is successful. | Small, 64.0 | 64.0 |
