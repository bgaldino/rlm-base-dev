---
page_id: connect_responses_api_execution_log.htm
title: API Execution Log Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_api_execution_log.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-06-09
---

# API Execution Log Response

Output representation of the execution log of a pricing waterfall request.

JSON example
:   ```
    {
      "message": {The Pricing API execution was successful.},
      "pricingElement": {
        "adjustments": [
          {
            "adjustmentType": null,
            "adjustmentValue": null
          }
        ],
        "name": "List Price",
        "elementType": "ListPrice"
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String [] | Message of the API execution. | Small, 63.0 | 63.0 |
| `pricingElement` | [Adjustment Details](./connect_responses_adjustment_detail.htm.md "Output representation of a pricing adjustment request.") | Details of the price adjustment of a pricing element. | Small, 63.0 | 63.0 |
