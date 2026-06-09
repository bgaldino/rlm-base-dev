---
page_id: connect_resources_deep_clone.htm
title: Deep Clone (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_deep_clone.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_resources.htm
fetched_at: 2026-06-09
---

# Deep Clone (POST)

Copy related records of an object along with the main product
record.

Resource
:   ```
    /connect/pcm/deep-clone
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/pcm/deep-clone
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "mainRecordId": "01tSG0000028kcSYAQ",
          "mainObjectApiName": "Product2",
          "mainRecordFieldValues": {
            "Name": "New Cloud Storage"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `mainObject​ApiName` | String | API name of the object. The supported object is Product2. | Required | 63.0 |
        | `mainRecord​Field​Values` | Map<String, String> | Mapping of the API name of the field to its value. The values passed through this map are set for the created record. You can pass the Name field only through this map. | Optional | 63.0 |
        | `mainRecord​Id` | String | ID of the record. | Required | 63.0 |

Response body for POST
:   [Deep Clone
    Response](./connect_responses_deep_clone_response.htm.md "Output representation of the details of the cloned record.")
