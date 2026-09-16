---
page_id: connect_responses_integration_procedure_cache_output.htm
title: Integration Procedure Cache Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_integration_procedure_cache_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Integration Procedure Cache Details

Output representation of the cache that are cleared for the specified integration
    procedures.

      
        
          

**JSON example**

          
: 
            

```
{
  "error": "Specify a valid cache key.",
  "response": [
    {
      "status": false
    }
  ],
  "status": "Error"
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the operation fails. | Small, 64.0 | 64.0 |
| `responseList` | [Integration Procedure Cache Response](./connect_responses_integration_procedure_cache_response.htm.md)[] | List of responses that are generated during the cache clearing process where each response corresponds to a specific cache key. | Small, 64.0 | 64.0 |
| `status` | Boolean | Indicates whether the cache is cleared successfully (`true`) or not (`false`) | Small, 64.0 | 64.0 |
