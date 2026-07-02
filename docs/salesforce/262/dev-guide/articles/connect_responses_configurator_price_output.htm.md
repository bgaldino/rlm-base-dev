---
page_id: connect_responses_configurator_price_output.htm
title: Configurator Price
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_price_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Price

Output representation of the pricing details in a product configuration.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `currency​IsoCode` | String | Currency ISO code of the price book entry. | Small, 60.0 | 60.0 |
| `effective​From` | String | Date from when the price book entry is effective. | Small, 60.0 | 60.0 |
| `effective​To` | String | Date until when the price book entry is effective. | Small, 60.0 | 60.0 |
| `isDefault` | Boolean | Indicates if this price book entry is the default pricing model (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Selected` | Boolean | Indicates if this price book entry is selected (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `pricebook​EntryId` | String | ID of the price book entry. | Small, 60.0 | 60.0 |
| `pricebookId` | String | Pricebook2 ID of the price book entry. | Small, 60.0 | 60.0 |
| `pricing​Model` | [Configurator Pricing Model](./connect_responses_configurator_pricing_model_output.htm.md "Output representation of the details of a pricing model in a product configuration.")[] | Pricing model details of the price book entry. | Small, 60.0 | 60.0 |
| `unitPrice` | Double | Unit price of the price book entry. | Small, 60.0 | 60.0 |
