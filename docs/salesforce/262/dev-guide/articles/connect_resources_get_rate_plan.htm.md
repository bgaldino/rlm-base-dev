---
page_id: connect_resources_get_rate_plan.htm
title: Rate Plan (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_get_rate_plan.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Rate Plan (GET)

Get a rate plan for a specified set of context input. Use this API to retrieve rate
cards, rate card entries, and related adjustments based on the filter criteria for the context
input.

Keep these considerations in mind when you use this API.

- This API request supports one pricebook and one sellable product.
- The ID of the product is required to invoke this API.
- Invoke this API even if a hydrated context is available to fetch the rate card, rate
  card entry, and adjustment details.

Special Access Rules
:   The org must have the Rate Management: Run Time User permission set to use this API.
    Additionally, the org must also have a default usage rating discovery procedure defined
    in the Revenue Settings from Setup.

Resource
:   ```
    /connect/core-rating/rate-plan
    ```

Resource example
:   ```
    https://your​Instance.salesforce.com​/services​/data/v67.0/connect/​core-rating/rate-plan​?contextId=858a3ad3e5a0e​5c319652a6ab92f6​fdb2b4fa8be72b390506​d014596c6da62c9&procedure​ApiName=Sample​Procedure
    ```

Available version
:   62.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextId` | String | ID of the context to specify as an input to the procedure. | Required | 62.0 |
    | `procedure​ApiName` | String | API name of the procedure to be executed. | Required | 62.0 |

Response body for GET
:   [Rate Plan Response](./connect_responses_rate_plan_response.htm.md "Output representation of the details of a rate plan.")
