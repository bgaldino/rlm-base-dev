---
article_id: ind.product_configurator_place_quote_api_for_data_transfer.htm
title: Use Place Sales Transaction API for Data Transfer
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_place_quote_api_for_data_transfer.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Use Place Sales Transaction API for Data Transfer

Transfer data from a custom configurator to a quote or order in Agentforce Revenue Management by using the Place Sales Transaction API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

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
