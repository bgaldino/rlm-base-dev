---
page_id: connect_resources_usage_product_activation.htm
title: Usage Product Activation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_usage_product_activation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Usage Product Activation (POST)

Activate a usage product and its related records, such as usage resources, grants,
policies, and rate card entries, in a single request.

Keep these considerations in mind when you use this API.

- In version 67.0, each request activates one
  product.
  If a request includes more than one product, the API returns the `MAX_LIMIT_EXCEEDED` error.
- Each record in the request stays in Draft status until activation runs. If any record
  for the product fails to activate, the API rolls back all activations for that
  product.
- The records activate in the order required by their dependencies, so a child record
  never activates before its parent.
- Each request activates a maximum of 200 records, including the product and all of its
  associated child records. If the request exceeds 200 records, the API returns the `MAX_LIMIT_EXCEEDED` error.

Resource
:   ```
    /revenue/usage-management/usage-products/actions/activate
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/usage-management/usage-products/actions/activate
    ```

Available version
:   67.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "shouldValidateProductSetup": false,
          "activationRequests": [
            {
              "productId": "01txx0000006i2gAAA",
              "usageResourceIds": [
                "0hUxx000000001",
                "0hUxx000000002"
              ]
            }
          ]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `activation​Requests` | [Usage Activation Request Input](./connect_requests_usage_activation_request_input.htm.md "Input representation for a single product entry in a usage product activation request. Each entry identifies one product and the usage resources to activate for that product.")[] | List of activation requests. Each entry identifies a product and the usage resources to activate for that product. This list accepts only one entry. If you include more, the API returns the `MAX_LIMIT_EXCEEDED` error. | Required | 67.0 |
        | `shouldValidate​ProductSetup` | Boolean | Indicates whether to run product setup validation before activation (`true`) or not (`false`). The default value is `true`. | Optional | 67.0 |

Response body for POST
:   [Usage Product Activation](./connect_responses_usage_activation_output.htm.md "Output representation of a usage product activation response.")
