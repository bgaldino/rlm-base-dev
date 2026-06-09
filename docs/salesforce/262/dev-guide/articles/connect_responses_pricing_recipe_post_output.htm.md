---
page_id: connect_responses_pricing_recipe_post_output.htm
title: Pricing Recipe Post
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_post_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Recipe Post

Output representation of the pricing recipe after the API request.

JSON example
:   ```
    {
    isSuccess : true 
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Details from the pricing error response. | Small, 60.0 | 60.0 |
| `isSuccess` | Boolean | Indicates whether the response was calculated successfully (`true`) or not (`false`). | Small, 60.0 | 60.0 |
