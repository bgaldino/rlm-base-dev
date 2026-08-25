---
page_id: connect_responses_datamapper_clear_cache_output.htm
title: Data Mapper Cache Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_datamapper_clear_cache_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Data Mapper Cache Details

Output representation of the cache details that are cleared for the specified data
    mappers.

      
        
          

**JSON example**

          
: 
            

```
{
  "error": "Specify a Data Mapper name",
  "responseList": [
    {
      "error": "Specify a Data Mapper name",
      "status": false
    }
  ],
  "status": false
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Error message if the operation fails. | Small, 64.0 | 64.0 |
| `responseList` | [Data Mapper Clear Cache Response](./connect_responses_datamapper_clear_cache_response.htm.md)[] | List of responses that are generated during the clear cache process. | Small, 64.0 | 64.0 |
| `status` | Boolean | Indicates whether the cache is cleared successfully (`true`) or not (`false`). | Small, 64.0 | 64.0 |
