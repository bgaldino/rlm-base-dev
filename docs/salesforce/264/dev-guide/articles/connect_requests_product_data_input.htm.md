---
page_id: connect_requests_product_data_input.htm
title: Product Data Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_data_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Data Input

Input representation of the product details such as the product ID and product selling
    model ID.

**JSON example**

: 

```
  "productData": [
    {
      "productId": "01txx0000006ivJAAQ",
      "productSellingModelId": "0jPxx000000009hEAA"
    },
    {
      "productId": "01txx0000006ivLAAQ",
      "productSellingModelId": "0jPxx000000009iEAABB"
    }
  ]
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `productId` | String | ID of the product. | Required | 61.0 |
| `product​Selling​ModelId` | String | ID of the product selling model. | Optional | 61.0 |
