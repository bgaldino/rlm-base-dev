---
page_id: connect_requests_deep_clone_input.htm
title: Deep Clone Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_deep_clone_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Deep Clone Input

Input representation of the details of the object and associated record to be
cloned.

JSON example
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
