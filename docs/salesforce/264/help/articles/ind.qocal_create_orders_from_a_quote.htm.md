---
article_id: ind.qocal_create_orders_from_a_quote.htm
title: Create an Order from a Quote
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_orders_from_a_quote.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_order_features.htm
fetched_at: 2026-11-23
---

# Create an Order from a Quote

Convert an accepted quote into an order with one click to synchronize product, quantity, pricing, and tax data. By using this process, the order record automatically inherits these details directly from the quote record.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To create orders from quotes:	Create Orders from Quotes

The order record copies product, quantity, pricing, and tax information directly from the quote record. If you make any tax-impacting changes to the order record, Salesforce recalculates the tax for the order.

IMPORTANT Revenue Cloud doesn't support creating orders from future-dated contracts. The system defaults the Order Start Date to the current date. If the contract has a future start date, this date mismatch causes an error during order creation.
Open the quote record.
Click Create Order.
Monitor your notifications to confirm the status of the order creation.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_orders_from_a_quote.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
