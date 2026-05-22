---
article_id: ind.qocal_asset_transfer_important_considerations.htm
title: Asset Transfer Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_transfer_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Asset Transfer Considerations

Familiarize yourself with the requirements and limitations for moving assets between accounts to ensure data consistency and compliance. Reviewing these constraints helps you manage quantities, price books, and product types correctly during the transfer process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Asset Transfer Requirements and Constraints

Review these critical rules before initiating an asset transfer.

Quantity Synchronization: If you adjust the transfer quantity on one quote or order, manually update the destination quantity to keep them in sync. You change the line item quantity in the source order and then apply changes to the destination order.
Configuration Limits: You can’t reconfigure bundles or change product attributes on the source quote or order during a transfer.
Transaction Volume: Asset Transfer supports a maximum of 50 line items per transaction.
Product Compatibility: The initial release of Asset Transfer doesn’t support transferring ramped assets or usage-based products.
Asset Status: You can’t transfer an expired asset.
Pricing Restrictions: You can’t use different price books for a transfer.
API Behavior: The Transfer API is synchronous. Any issue during processing reverts the entire transaction.
