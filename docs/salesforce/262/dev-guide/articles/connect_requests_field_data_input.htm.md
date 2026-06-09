---
page_id: connect_requests_field_data_input.htm
title: Field Data Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_field_data_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-06-09
---

# Field Data Input

Input representation of the details of the field data input.

JSON example
:   ```
          "fieldDataInputs": [
            {
              "fieldApiName": "MaxQuantity",
              "originalValue": 0.437584,
              "unitOfMeasureId": "uomId2"
            },
            {
              "fieldApiName": "MinQuantity",
              "originalValue": 7364.58923,
              "unitOfMeasureId": "uomId2"
            }
          ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `fieldApi​Name` | String | Unique API name of the field. | Required | 63.0 |
    | `original​Value` | String | Original value of the fields. | Required | 63.0 |
    | `unitOf​MeasureId` | String | ID of the unit of measure record that’s associated to the field. | Required | 63.0 |
