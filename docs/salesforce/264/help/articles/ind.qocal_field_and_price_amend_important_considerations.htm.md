---
article_id: ind.qocal_field_and_price_amend_important_considerations.htm
title: Field and Price Amendment Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_price_amend_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-09-04
---

# Field and Price Amendment Considerations

Familiarize yourself with the specific requirements for using Field Amendments and Price Amendments to update asset details and adjust pricing effectively. Understanding these technical mappings and supported fields helps you accurately reflect amendments in asset state periods (ASPs) and audit trails.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Implementation Considerations

The Field Amendments feature supports bundles, derived pricing products (DPPs), and usage-based products. Note these technical requirements for field mapping and behavior.

Identification of Changes: The feature identifies field amendment differences by comparing field values on the quote line item (QLI) or order item (OI) against the ASP.
ASP Versioning: ASPs created before Winter ’26 show field value differences between the Asset Action Source (AAS) and the ASP. This discrepancy results in the creation of field amendment actions for line items even without manual changes.
Value Sourcing: During amend, renew, or cancel (ARC) actions, the transaction pulls field values from the ASP record. However, the QLI Legal Entity field maps to and retrieves its value from the AAS field for ARC actions. The system references non-custom field values, including the start date, from the most recent AAS.
Supported Fields

These fields are supported for Field Amendments and Price Amendments.

FEATURE	SUPPORTED FIELDS
Field Amendments	Billing Frequency, Legal Entity, Uplift Percent, Uplift Policy
Price Amendments	Custom Fields, Discount Amount, Discount Percent, Sales Price, Unit Price
Price Amendment Behaviors
Product Support: Price Amendments work on bundles and usage-based products. However, you can't set a new Sales Price or Unit Price for usage-based products.
Derived Pricing: You can use Price Amendments for a derived pricing product (DPP) when a contributing product's price changes. Existing DPP pricing behavior remains unchanged.
