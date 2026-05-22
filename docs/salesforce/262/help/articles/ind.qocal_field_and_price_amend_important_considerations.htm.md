---
article_id: ind.qocal_field_and_price_amend_important_considerations.htm
title: Field and Price Amendment Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_price_amend_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Field and Price Amendment Considerations

Familiarize yourself with specific requirements for using the field and price amendments feature to update asset details and adjust pricing effectively. Understanding these technical mappings and supported fields makes sure that your amendments accurately reflect in asset state periods (ASPs) and audit trails.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Implementation Considerations

The Field Amendments feature supports bundles, derived pricing products (DPPs), and usage-based products. Note these technical requirements for field mapping and behavior.

Field Mapping Complexity: Mapping custom fields between order line items, assets, and amendment quotes require context definition mappings.
Mapping Execution: The system applies mappings during order assetization to create or update asset-related objects. This process also applies mappings when you create an amendment quote or order.
Identification of Changes: The feature identifies field amendment differences by comparing field values on the quote line item (QLI) or order item (OI) against the ASP.
ASP Versioning: ASPs created before the Winter '26 release show field value differences between the Asset Action Source (AAS) and the ASP. This discrepancy results in the creation of field amendment actions for line items even without manual changes.
Value Sourcing: During amend, renew, or cancel (ARC) actions, the transaction pulls field values from the ASP record. However, the QLI Legal Entity field maps to and retrieves its value from the AAS field for ARC actions. The system references non-custom field values, including the start date, from the most recent AAS.
Pricing Constraints: The system doesn’t support setting a new list price, unit price, or sales price as a field amendment.
Quote Line Distributions: The system doesn’t support amendments that update fields on the Quote Line Item (QLI) distribution.
Supported Fields

The system supports specific fields for field-level and price-only modifications.

FEATURE	SUPPORTED FIELDS
Field Amendments	Billing Frequency, Legal Entity, Uplift Percent, Uplift Policy
Price Amendments	Custom Fields, Discount Amount, Discount Percent
Price Only Amendment Behaviors
Product Support: The Price Only Amendments feature works on bundles and usage-based products.
Derived Pricing: The system supports price amendments for a derived pricing product (DPP) when a contributing product's price changes. This process maintains existing behavior for DPPs.
Transaction Limits: Price amendments don’t apply to renewals or cancellations.
