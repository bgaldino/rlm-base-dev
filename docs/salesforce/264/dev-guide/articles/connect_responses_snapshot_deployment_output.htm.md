---
page_id: connect_responses_snapshot_deployment_output.htm
title: Snapshot Deployment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_snapshot_deployment_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Snapshot Deployment

Output representation of the snapshot deployment.

        
          

**JSON example**

          
: This example shows a sample response to the request to build a new snapshot with
            immediate activation.

          
: 
            

```
{
  "errors": [],
  "snapshot": {
    "activationStatus": "NONE",
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000004CFU",
    "snapshotIndexes": [
      {
        "createdDate": "2024-07-24T21:10:48.000Z",
        "id": "1D6xx0000004CFU",
        "indexBuildType": "FULL",
        "indexType": "PRODUCT",
        "lastBuildStatus": "IN_PROGRESS"
      }
    ]
  },
  "statusCode": "200"
}
```

          

          
: This example shows a sample response of the request to rebuild a snapshot in the
              `active` status.

          
: 
            

```
{
  "errors": [],
  "snapshot": {
    "activationStatus": "NONE",
    "activationType": "IMMEDIATE",
    "id": "1Avxx0000004CH6",
    "snapshotIndexes": [
      {
        "createdDate": "2024-07-24T21:13:05.000Z",
        "id": "1D6xx0000004CH6",
        "indexBuildType": "FULL",
        "indexType": "PRODUCT",
        "lastBuildStatus": "IN_PROGRESS"
      }
    ]
  },
  "statusCode": "200"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Output](./connect_responses_epc_error_output.htm.md)[] | List of errors, if any. | Small, 62.0 | 62.0 |
| `snapshot` | [Snapshot](./connect_responses_snapshot_output.htm.md)[] | Run-time catalog snapshot associated with the created index. | Small, 62.0 | 62.0 |
| `statusCode` | String | Code indicating the status of the request. | Small, 62.0 | 62.0 |
