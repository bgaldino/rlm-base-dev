---
page_id: connect_responses_snapshot_index_info_output.htm
title: Snapshot Index Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_index_info_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Snapshot Index Info

Output representation of the details of a snapshot index.

      
        
          

**JSON example**

          
: 
            

```
 "indexInfos": [
            {
              "buildType": "FULL",
              "id": "0axxx00000000T3AAI",
              "isIncrementable": true,
              "usageType": "LIVE"
            }
          ]
```

          

        
      

- 
- 

- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `buildType` | String | Build type of the index. Valid values are: `FULL`—Specifies a full index build. `INCREMENTAL`—Specifies an incremental index build. Available in API version 63.0 and later. | Small, 63.0 | 63.0 |
| `id` | String | ID of the index information record. | Small, 63.0 | 63.0 |
| `isIncrementable` | Boolean | Indicates whether a partial build is enabled (`true`) or disabled (`false`). | Small, 63.0 | 63.0 |
| `usageType` | String | Usage type of the index. Valid values are: `LIVE`—Index usage type is live. `OUT_OF_USE`—Index usage type is out of use. | Small, 63.0 | 63.0 |
