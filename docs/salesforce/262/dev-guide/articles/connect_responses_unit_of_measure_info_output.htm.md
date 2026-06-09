---
page_id: connect_responses_unit_of_measure_info_output.htm
title: Unit of Measure Info
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_unit_of_measure_info_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Unit of Measure Info

Output representation of the details of a unit of measure record.

JSON example
:   ```
      "uomIdToUnitOfMeasureInfo": {
        "0hEU200000003M5MAI": {
          "id": "0hEU200000003M5MAI",
          "name": "Pounds",
          "roundingMethod": "Nearest",
          "scale": 1,
          "unitCode": "Pounds"
        },
        "0hEU200000003KTMAY": {
          "id": "0hEU200000003KTMAY",
          "name": "Grams",
          "roundingMethod": "Down",
          "scale": 5,
          "unitCode": "Grams"
        }
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the unit of measure record. | Small, 63.0 | 63.0 |
| `name` | String | Name of the unit of measure record. | Small, 63.0 | 63.0 |
| `roundingMethod` | String | Data rounding method of the unit of measure record. | Small, 63.0 | 63.0 |
| `scale` | Integer | Scale of the unit of measure record. | Small, 63.0 | 63.0 |
| `unitCode` | String | Code of the unit of measure record. | Small, 63.0 | 63.0 |
