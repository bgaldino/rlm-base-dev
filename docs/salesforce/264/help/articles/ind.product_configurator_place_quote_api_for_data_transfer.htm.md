---
article_id: ind.product_configurator_place_quote_api_for_data_transfer.htm
title: Use Place Sales Transaction API for Data Transfer
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_place_quote_api_for_data_transfer.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_third_party_configurator.htm
fetched_at: 2026-09-04
---

# Use Place Sales Transaction API for Data Transfer

Transfer data from a custom configurator to a quote or order in Revenue Management by using the Place Sales Transaction API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

The Place Sales Transaction API offers flexibility to either include or exclude the first-party configurator logic. Further, third-party users can use the first-party configurator API tasks such as validating the bundle structure, applying Salesforce Pricing rules, or implementing qualification rules.

EXAMPLE

"configurationInput": ["skip" / "runAndAllowErrors" / "runAndBlockErrors"], // Default runAndBlockErrors
"configurationOptions": {
"validateProductCatalog": true,
"validateAmendRenewCancel": true,
"executeConfigurationRules": true,
"addDefaultConfiguration": true
}
// rest of Place Sales Transaction API payload
}
