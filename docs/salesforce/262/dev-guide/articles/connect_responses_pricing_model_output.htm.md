---
page_id: connect_responses_pricing_model_output.htm
title: Pricing Model
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_model_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Pricing Model

Output representation of the details of the pricing model.

JSON example
:   ```
    {
      "pricingModel": {
        "id": "0jPSG000000Avcv2AC",
        "name": "One Time",
        "pricingModelType": "OneTime"
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `frequency` | String | Details about the frequency of recurrence of the pricing model. | Small, 67.0 | 67.0 |
| `id` | String | ID of the pricing model. | Small, 67.0 | 67.0 |
| `name` | String | Name of the pricing model. | Small, 67.0 | 67.0 |
| `occurrence` | Integer | Details about the number of occurrences of the pricing model. | Small, 67.0 | 67.0 |
| `pricingModelType` | String | Type of the pricing model. | Small, 67.0 | 67.0 |
| `unitOfMeasure` | String | Unit of measure for the pricing model. | Small, 67.0 | 67.0 |
