---
page_id: connect_requests_product_classification_details_input.htm
title: Product Classification Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_classification_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Classification Details Input

Input representation of the request to fetch details of product classification records,
    including their attributes and attribute categories.

**JSON example**

: 

```
{
  "productClassificationIds": [
    "01txx0000006iFMAAY",
    "01txx0000006iGxAAY"
  ],
  "catalogSystems": [
    "epc"
  ]
}
```

**Properties**

: 

- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `catalogSystems` | String[] | Name of the catalog system. Valid value is: `epc`—Enterprise Product Catalog | Optional | 66.0 |
| `product​ClassificationIds` | String[] | List of product classification IDs for which you want to retrieve product details. In the `epc` catalog system, these values are the `Product2` record IDs. | Required | 66.0 |
