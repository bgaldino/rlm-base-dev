---
page_id: connect_responses_pricing_valid_elements_output.htm
title: Pricing Recipe Valid Elements
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_valid_elements_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-09-29
---

# Pricing Recipe Valid Elements

Output representation containing the list of valid pricing element type API names for a given Pricing Usage Sub Type.

              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorMessage` | String | Error message when the `isSuccess` property is false. This property value is blank when the `isSuccess` property is true. | Big, 68.0 | 68.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |
| `validPricingElements` | String | List of valid pricing element type API names for the given sub usage type. This property value includes an empty list when the `isSuccess` property is false. | Big, 68.0 | 68.0 |
