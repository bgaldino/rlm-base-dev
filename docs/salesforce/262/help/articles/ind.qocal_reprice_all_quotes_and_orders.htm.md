---
article_id: ind.qocal_reprice_all_quotes_and_orders.htm
title: Reprice All for Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_reprice_all_quotes_and_orders.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Reprice All for Quotes and Orders

Refresh and validate prices across an entire transaction by recalculating all quote or order lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

The Reprice All action performs a full repricing of every transaction line, even when no changes exist. This action always runs a full recalculation, regardless of whether you turn on Delta Pricing.

Repricing Scenarios
The Transaction Processing Type (TPT) skipped pricing during the record commitment process.
Validation errors prevented a successful pricing run.
Discounts, adjustments, or bundle configurations require a refresh.
Estimated taxes need calculation (requires the Add Estimated Tax to Quotes and Orders setting in Revenue Settings).
Button Accessibility

Access the Reprice All button within the Transaction Line Editor or the Sales Transaction Line Editor. If the button isn’t visible, use the Lightning App Builder to add it to the interface. See Configure Action Buttons in Transaction Line Editor.

Accuracy in Usage-Based Quotes

Salesforce maintains the connection between quote line items and usage data through system-generated resource grants. System-generated grants ensure accurate resource quantity negotiations and successful record commitments.

Protect quote data integrity by following these guidelines.

Avoid manual deletion of usage resource grants for quote line items.
Acknowledge that manual deletion breaks resource links, which causes record commitment failures and locked resources.
Restore accidentally deleted grants by clicking Reprice All to rebuild the records.
Contact your Salesforce admin or Customer Support if repricing fails to restore data consistency.
