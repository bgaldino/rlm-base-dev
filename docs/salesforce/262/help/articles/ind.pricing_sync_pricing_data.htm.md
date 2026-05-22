---
article_id: ind.pricing_sync_pricing_data.htm
title: Sync Pricing Data in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_sync_pricing_data.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Sync Pricing Data in Agentforce Revenue Management

Regularly sync your pricing data in Salesforce Agentforce Revenue Management to ensure the latest information is available in decision tables that are mapped to a pricing recipe and have their usage type set to Pricing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To enable data sync:	Salesforce Pricing Design Time
To ensure complete sync of decision tables:	Assetize Order

You should sync pricing data whenever there are updates to your product prices, discounts, or any other pricing-related data that decision tables consume. Syncing pricing data is crucial for accurate pricing calculations. This ensures consistency across your sales processes and supports features like derived pricing. Without it, inconsistencies could impact final net price calculations.

IMPORTANT For an accurate sync, set the Usage Type to Pricing for any decision table containing source objects. If a complete sync fails, we recommend using the System Admin permission set.

The sync operation is a manual process.

From Setup, in the Quick Find box, enter Salesforce Pricing, and then select Salesforce Pricing Setup.
In the Sync Pricing Data section, click Sync.
