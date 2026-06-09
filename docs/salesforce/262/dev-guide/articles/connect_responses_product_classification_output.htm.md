---
page_id: connect_responses_product_classification_output.htm
title: Product Classification
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Product Classification

Output representation of the product classification details.

JSON example
:   ```
    {
      "productClassification": {
        "id": "11BT10000004C9SMAU",
        "name": "class",
        "code": "code",
        "parentProductClassificationId": "11BDU0000004JXq2AM",
        "status": "Active"
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the product classification record. | Small, 61.0 | 61.0 |
| `id` | String | ID of the product classification record. | Small, 60.0 | 60.0 |
| `name` | String | Name of the product classification record. If data translation is set up and specified in the org, the translated description is available. | Small, 61.0 | 61.0 |
| `parentProduct​Classification​Id` | String | ID of the parent product classification. | Small, 65.0 | 65.0 |
| `status` | String | Status of the product classification record. | Small, 61.0 | 61.0 |
