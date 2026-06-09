---
page_id: connect_resources_catalog_details.htm
title: Catalog Details (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_catalog_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_resources.htm
fetched_at: 2026-06-09
---

# Catalog Details (POST)

Get catalog details for a specified catalog ID. This API is a
composite API for Product Discovery.

Resource
:   ```
    /connect/cpq/catalogs/catalogId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/cpq/catalogs/0ZSxx000000009hGAA
    ```

Available version
:   60.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "userContext": {
             "accountId": "001xx0000000001AAA",
             "contactId": "003xx00000000D7AAI"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
        | `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |

Response body for POST
:   [CPQ Base
    Details](./connect_responses_cpq_base_details_output.htm.md "Output representation of the catalog, category, or product details based on the request.")
