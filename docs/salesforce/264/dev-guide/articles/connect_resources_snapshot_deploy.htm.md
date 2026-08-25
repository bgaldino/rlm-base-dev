---
page_id: connect_resources_snapshot_deploy.htm
title: Snapshot Deployment (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_snapshot_deploy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Snapshot Deployment (POST)

Create indexes for a snapshot. Indexes improve search results and make
      it easier to find products at run time through search terms.

    
      
        
          

**Resource**

          
: 
            

```
/connect/pcm/index/deploy
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/pcm/index/deploy
```

          

        
        
          

**Available version**

          
: 62.0

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

          
: This example shows a sample request to build a new snapshot with immediate
            activation.

: 

```
{
  "snapshot": {
    "activationType": "IMMEDIATE"
  },
  "buildType": "FULL"
}
```

          
: This example shows a sample request to rebuild a snapshot in the `active` status.

          
: 
            

```
{
  "snapshot": {
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000005DFe1AM"
  },
  "buildType": "FULL"
}
```

          

**Properties**

: 

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `buildType` | String | Build type of the snapshot index. Valid value is: `FULL`—Specifies a full index build. `INCREMENTAL`—Specifies an incremental index build. Available from API version 63.0 and later. | Required | 62.0 |
| `snapshot` | [Run-time Catalog Snapshot Input](./connect_requests_runtime_catalog_snapshot_input.htm.md)[] | Snapshot to deploy. | Required | 62.0 |

          

        
        
          

**Response body for POST**

          
: [Snapshot
              Deployment](./connect_responses_snapshot_deployment_output.htm.md)
