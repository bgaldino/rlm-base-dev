---
page_id: connect_responses_configurator_product_selling_model_option_output.htm
title: Configurator Product Selling Model Option
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_selling_model_option_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Configurator Product Selling Model Option

Output representation of the product selling model option in a product configuration.

## JSON Example

```
         "productSellingModelOptions": [
           {
             "id": "0iOxx000000009hEAA",
             "productId": "01txx0000006jmWAAQ",
             "productSellingModel": {
               "id": "0jPxx000000004rEAA",
            "name": "Termed Annually",
               "pricingTerm": 1,
               "pricingTermUnit": "Annual",
               "sellingModelType": "TermDefined",
               "status": "Active"
             },
             "productSellingModelId": "0jPxx000000004rEAA"
           },
           {
             "id": "0iOxx00000000PpEAI",
             "productId": "01txx0000006jmWAAQ",
             "productSellingModel": {
               "id": "0jPxx0000000085EAA",
               "name": "Evergreen Annually",
               "pricingTerm": 1,
               "pricingTermUnit": "Annual",
               "sellingModelType": "Evergreen",
               "status": "Active"
             },
             "productSellingModelId": "0jPxx0000000085EAA"
           }
         ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the product selling model option. | Small, 60.0 | 60.0 |
| `product​Id` | String | ID of the product that’s associated with the product selling model option. | Small, 60.0 | 60.0 |
| `product​Selling​Model` | [Configurator Product Selling Model](./connect_responses_configurator_product_selling_model_output.htm.md "Output representation of the product selling model in a product configuration.")[] | Product selling model that’s associated with the product selling model option. | Small, 60.0 | 60.0 |
| `product​Selling​ModelId` | String | ID of the product selling model that’s associated with the product selling model option. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_selling_model_option_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
