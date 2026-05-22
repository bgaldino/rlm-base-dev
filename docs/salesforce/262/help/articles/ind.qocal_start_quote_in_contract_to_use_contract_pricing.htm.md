---
article_id: ind.qocal_start_quote_in_contract_to_use_contract_pricing.htm
title: Generate a Quote or Order from a Contract
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_start_quote_in_contract_to_use_contract_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Generate a Quote or Order from a Contract

Create quotes or orders from an active contract with contract-based pricing to include negotiated contract prices in your new transaction. Sales reps use existing contract-based pricing to ensure financial accuracy for specific customers.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To use contract pricing:	Salesforce Pricing Design Time User
To create quotes:	Create on Quotes
IMPORTANT
Refresh the decision table for contract pricing after activating a contract that contains contract item prices or price adjustment schedules.
Avoid removing or changing a contract ID assigned to a quote or order, as this action impacts pricing during recalculation.

Generate a new transaction record that inherits negotiated pricing directly from an active contract.

From the App Launcher, search for and select Contracts.
From the Contracts list view, select All Activated Contracts.
Select an activated contract that contains contract-based pricing.
On the Related tab, go to the quotes or orders related list and click New.
Enter a name for the quote or order and save your changes.
Add products to the quote or order.
The system applies existing contract prices, discounts, or adjustments to the added products.
Hover over the Net Unit Price to view the pricing waterfall and verify the pricing calculations.
Save your changes.
