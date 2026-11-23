---
article_id: ind.qocal_field_and_price_amend_important_considerations.htm
title: Field and Price Amendment Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_price_amend_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-11-23
---

# Field and Price Amendment Considerations

Familiarize yourself with the specific requirements for using Field Amendments and Price Amendments to update asset details and adjust pricing effectively. Understanding these technical mappings and supported fields helps you accurately reflect amendments in asset state periods (ASPs) and audit trails.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Implementation Considerations

The Field Amendments feature supports bundles, derived pricing products (DPPs), and usage-based products. Note these technical requirements for field mapping and behavior.

Identification of changes: The feature identifies field amendment differences by comparing field values on the quote line item (QLI) or order item (OI) against the ASP.
ASP versioning: ASPs created before Winter ’26 have field value differences between the Asset Action Source (AAS) and the ASP. This discrepancy results in creation of field amendment actions for line items, even without manual changes.
Value sourcing: During amend, renew, or cancel (ARC) actions, the transaction pulls field values from the ASP record. However, the QLI Legal Entity field maps to and gets its value from the AAS field for ARC actions. The system references non-custom field values, including the start date, from the most recent AAS.
Discount and DiscountAmount ASP fields: These fields contain the line item discount percentages and discount amounts. Changes to these field's values are processed as additive discounts and the line becomes a field amendment.
Supported Fields

These fields are supported for Field Amendments and Price Amendments.

FEATURE	SUPPORTED FIELDS
Field Amendments	Billing Frequency, Legal Entity, Uplift Percent, Uplift Policy
Price Amendments	Custom Fields, Discount Amount, Discount Percent, Sales Price, Unit Price
Price Amendment Behaviors
Product Support: Price Amendments work on bundles and usage-based products. However, you can't set a new Sales Price or Unit Price for usage-based products.
Derived Pricing: You can use Price Amendments for a derived pricing product (DPP) when a contributing product's price changes. Existing DPP pricing behavior remains unchanged.
Quote Line Detail: When you perform a price amendment, the system creates Quote Line Detail records and clears the Input Unit Price or Sales Price, and Net Unit Price fields on the Quote Line Items.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_price_amend_important_considerations.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
