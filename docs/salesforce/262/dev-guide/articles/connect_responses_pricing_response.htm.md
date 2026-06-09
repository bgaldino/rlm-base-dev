---
page_id: connect_responses_pricing_response.htm
title: Pricing Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Response

Output representation of the pricing request.

JSON example
:   ```
    {
        "success": true,
        "executionId": "zu81o5hBCrFzyd5LWZk"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Errors while processing the request, if any. | Small, 60.0 | 60.0 |
| `execution​Id` | String | Auto-generated alphanumeric string for correlation to extract async waterfall and context persistence status. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates if the request is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |
