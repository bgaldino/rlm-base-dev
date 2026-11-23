---
article_id: ind.product_configurator_place_quote_api_for_data_transfer.htm
title: Use Place Sales Transaction API for Data Transfer
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_place_quote_api_for_data_transfer.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_third_party_configurator.htm
fetched_at: 2026-11-23
---

# Use Place Sales Transaction API for Data Transfer

Transfer data from a custom configurator to a quote or order in Revenue Cloud by using the Place Sales Transaction API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_place_quote_api_for_data_transfer.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
