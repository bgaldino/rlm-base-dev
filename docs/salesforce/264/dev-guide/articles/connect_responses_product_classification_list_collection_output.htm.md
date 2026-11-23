---
page_id: connect_responses_product_classification_list_collection_output.htm
title: Product Classification List Collection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_list_collection_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-11-23
---

# Product Classification List Collection

Output representation that contains a collection of product classification records along with any processing errors.

## JSON Example

```
{
  "success": true,
  "errors": [],
  "productClassifications": [
    {
      "id": "11BT10000004C9SMAU",
      "name": "Mobile Devices",
      "code": "MOB_DEV",
      "parentProductClassificationId": "11BDU0000004JXq2AM",
      "status": "Active"
    },
    {
      "id": "11BT10000004C9TMAU",
      "name": "Mobile Accessories",
      "code": "MOB_ACC",
      "status": "Active"
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Product Catalog Management Error](./connect_responses_p_c_m_error_output.htm.md "Output representation that contains error details, including error codes and messages.")[] | List of errors encountered during the processing of the API request. | Small, 67.0 | 67.0 |
| `productClassifications` | [Product Classification](./connect_responses_product_classification_output.htm.md "Output representation of the product classification details.")[] | List of product classification records that match the request query. | Small, 67.0 | 67.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or has failed (`false`). | Small, 67.0 | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_list_collection_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
