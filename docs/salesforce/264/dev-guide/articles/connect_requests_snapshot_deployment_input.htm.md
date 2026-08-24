---
page_id: connect_requests_snapshot_deployment_input.htm
title: Snapshot Deployment Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_snapshot_deployment_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Snapshot Deployment Input

Input representation of the request to deploy a run-time catalog snapshot.

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
