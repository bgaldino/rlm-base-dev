---
page_id: connect_requests_product_classification_details_input.htm
title: Product Classification Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_classification_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-11-23
---

# Product Classification Details Input

Input representation of the request to fetch details of product classification records, including their attributes and attribute categories.

**JSON Example**

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

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `catalogSystems` | String[] | Name of the catalog system. Valid value is `epc`—Enterprise Product Catalog. | Optional | 66.0 |
| `product​ClassificationIds` | String[] | List of product classification IDs for which you want to retrieve product details. In the `epc` catalog system, these values are the `Product2` record IDs. | Required | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_product_classification_details_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
