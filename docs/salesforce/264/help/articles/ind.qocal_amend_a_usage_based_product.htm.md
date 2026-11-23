---
article_id: ind.qocal_amend_a_usage_based_product.htm
title: Amend a Usage-Based Product
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_amend_a_usage_based_product.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amending_rates_and_grants_on_usage_based_products.htm
fetched_at: 2026-11-23
---

# Amend a Usage-Based Product

Change the rates, grants, or quantities of an existing asset to reflect new customer agreements.

REQUIRED EDITIONS
NOTE Grant negotiations are not supported on existing quotes and orders.
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To amend assets:	Amend Assets and Sales Rep permission group
NOTE Before you being to amend a usage-based product, remember the following.
Existing quotes and orders don’t support grant negotiations.
Ensure that the amendment date is within the asset's lifecycle.
From the App Launcher, find and select Orders.
Select the order number.
Click Account Name, and then click Assets.
Select the asset, and then click Amend.
Enter the amendment date.
If needed, select Use the amendment start date for the subscription start date, and click Submit.
Submitting the amendment creates the quote line item usage resource grants.
From the Quick Actions menu, select Manage Usage Resources.
Specify the grant quantity and applicable rate.
Save your changes.
The system creates an amendment for the quote line item.
EXAMPLE

To update an existing subscription for ACME, a cloud storage company, define a grant quantity of 70,000 Revenue Cloud Credits and an applicable rate of $18 USD. After you save, use the amended quote line item to create an order.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_amend_a_usage_based_product.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
