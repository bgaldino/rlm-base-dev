---
page_id: connect_resources_usage_product_validation.htm
title: Usage Product Validation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_usage_product_validation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Usage Product Validation (POST)

Validate cross-object relationships and business rules for usage-based products.

This API returns validation results with errors and warnings.

Resource
:   ```
    /revenue/usage-management/usage-products/actions/validate
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/usage-management/usage-products/actions/validate
    ```

Available version
:   66.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "productIds": [
            "01txx0000006i2gAAA",
            "01txx0000006j2gAAA"
          ],
          "startDate": "2024-01-01T00:00:00Z",
          "endDate": "2024-12-31T23:59:59Z"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `productIds` | String[] | List of product IDs to be validated. The maximum limit is `10` valid product IDs. | Required | 66.0 |
        | `startDate` | String | Start date of the date range in which all active records are validated. | Optional | 66.0 |
        | `endDate` | String | End date of the date range in which all active records are validated. | Optional | 66.0 |

Response body for POST
:   [Usage Product Validation](./connect_responses_usage_product_validation_output.htm.md "Output representation of all the performed validations.")
