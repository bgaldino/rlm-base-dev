---
page_id: connect_responses_deep_clone_record_response.htm
title: Deep Clone Record Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_deep_clone_record_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Deep Clone Record Response

Output representation of the details of the cloned related records.

JSON example
:   ```
      "createdRecordList": [
        {
          "createdRecordId": "01tSG0000030Yb3YAE",
          "entityApiName": "Product2",
          "entityLabel": "Product"
        },
        {
          "createdRecordId": "0iOSG0000002rMn2AI",
          "entityApiName": "ProductSellingModelOption",
          "entityLabel": "Product Selling Model Option"
        },
        {
          "createdRecordId": "0v7SG0000001ktdYAA",
          "entityApiName": "ProductAttributeDefinition",
          "entityLabel": "Product Attribute Definition"
        }
      ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `created​RecordId` | String | ID of the created related record. | Small, 63.0 | 63.0 |
| `entity​ApiName` | String | API name of the created object. | Small, 63.0 | 63.0 |
| `entity​Label` | String | Label of the created object. | Small, 63.0 | 63.0 |
