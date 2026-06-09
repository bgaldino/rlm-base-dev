---
page_id: connect_resources_rating_waterfall_fetch.htm
title: Rating Waterfall (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_rating_waterfall_fetch.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Rating Waterfall (GET)

Get the persisted rating waterfall that stores the process logs.
Rating waterfall provides insights into the internal rating process.

Resource
:   ```
    /connect/core-pricing/waterfall/lineItemId/executionId
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/core-pricing/waterfall/Gold/2yHdNNEFOZr9jAe4gHS7?tagsToFilter=UnitPrice&usageType=Rating
    ```

Available version
:   62.0

HTTP methods
:   GET

Query parameters
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `tagsTo​Filter` | String | Comma-separated tags to filter. | Optional | 62.0 |
    | `usage​Type` | String | Usage type of the waterfall log record. Valid values are:   - `Rating` - `Pricing`—Specifies that the   record type is `Pricing`. If this value   is specified, the API creates a log of pricing waterfall. See [Pricing   Waterfall](https://developer.salesforce.com/docs/./connect_resources_pricing_waterfall_post.htm.md "HTML (New Window)").   The default value is `Pricing`. | Optional | 62.0 |

Response body for GET
:   [Line Item Waterfall
    Response](./connect_responses_rating_line_item_waterfall_response.htm.md "Output representation of the line item waterfall response.")
