---
page_id: connect_responses_deep_clone_response.htm
title: Deep Clone Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_deep_clone_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Deep Clone Response

Output representation of the details of the cloned record.

JSON example
:   ```
    {
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
      ],
      "createdRootRecordId": "01tSG0000030Yb3YAE",
      "errorList": [],
      "isSuccessful": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `created​RecordList` | [Deep Clone Record Response](./connect_responses_deep_clone_record_response.htm.md "Output representation of the details of the cloned related records.")[] | List of cloned related records of the main record. | Small, 63.0 | 63.0 |
| `createdRoot​RecordId` | String | ID of the created root record. | Small, 63.0 | 63.0 |
| `error​List` | [Deep Clone Error](./connect_responses_deep_clone_error.htm.md "Output representation of the error details related to the deep clone request.")[] | Details of errors, if any. | Small, 63.0 | 63.0 |
| `error​Message` | String | Error message if the API request fails. | Small, 63.0 | 63.0 |
| `is​Successful` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 63.0 | 63.0 |
