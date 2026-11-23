---
article_id: ind.qocal_quote_to_contract_flow.htm
title: Map a Flow to Capture Quote Line Pricing on Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_quote_to_contract_flow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_contract_features.htm
fetched_at: 2026-11-23
---

# Map a Flow to Capture Quote Line Pricing on Contracts

Configure a flow to generate contracts from quotes automatically, helping sales reps to capture negotiated prices and discounts as contract item prices. This automation simplifies the contract lifecycle by giving users the choice to include quote line details or create a contract without specific pricing records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To open, edit, or create a flow in Flow Builder:	Manage Flow
To use Contract Pricing:	Salesforce Pricing Design Time User

Contracts created from quotes include contract item price records generated from quote line items. Conversely, the system doesn’t create contract item price records from order products when you generate a contract from an order.

From Setup, search for and select Revenue Settings.
In Set Up Flow for Creating Contracts from Quotes section, enter rev_contracts__CreateCntrFromQuote and save your changes.
Admins can customize this automation by entering a different flow API name and saving.
When users click the New Contract button, select one of the options.
Capture net unit prices or discounts of quote line items as contract item prices.
Create a contract without capturing any contract-based prices or discounts.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_quote_to_contract_flow.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
