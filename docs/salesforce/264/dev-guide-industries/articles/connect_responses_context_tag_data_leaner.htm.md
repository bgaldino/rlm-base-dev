---
page_id: connect_responses_context_tag_data_leaner.htm
title: Context Tag Data Leaner
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_tag_data_leaner.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Tag Data Leaner

Output representation of the leaner context tag data. It stores only the metadata
    required to reconstruct tag values and the index references instead of full path
    strings.

        
          

**JSON example**

          
: 
            

```
{
  "nodeLevelTag": false,
  "recordIdIndexesForPath": [
    0,
    2
  ],
  "tagValue": "Blue"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `nodeLevel​Tag` | Boolean | Indicates whether the tag is at node level (`true`) or not. (`false`) | Small, 66.0 | 66.0 |
| `recordId​IndexesForPath` | Integer[] | List of integer indexes referencing the recordIds array to reconstruct the data path.For example, if `recordIds` is ["r4", "r2", "r10", "r1"] and `recordIdIndexesForPath` is [3, 1], the reconstructed path would be contextId/r1/r2 (where r1 is at index 3 and r2 is at index 1). | Small, 66.0 | 66.0 |
| `tagValue` | Object | Value of the tag. For attribute-level tags, this is a primitive value. For node-level tags, this is a map containing nested tag data. | Small, 66.0 | 66.0 |
