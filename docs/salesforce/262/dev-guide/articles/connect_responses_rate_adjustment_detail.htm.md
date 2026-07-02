---
page_id: connect_responses_rate_adjustment_detail.htm
title: Adjustment Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_rate_adjustment_detail.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Adjustment Details

Output representation of a rate adjustment request.

JSON example
:   ```
     "pricingElement": {
          "adjustments": [{
          "adjustmentType": null,
          "adjustmentValue": null
        }],
          "name": "List Price",
          "elementType": "ListPrice"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `adjustments` | Map<String, Object>[] | Details of the rate element. | Small, 60.0 | 60.0 |
| `description` | String | Description of the rate element. | Small, 60.0 | 60.0 |
| `element​Type` | String | Type of the rate element. | Small, 60.0 | 60.0 |
| `name` | String | Name of the rate element. | Small, 60.0 | 60.0 |
