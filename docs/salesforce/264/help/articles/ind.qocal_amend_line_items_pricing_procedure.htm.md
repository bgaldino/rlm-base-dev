---
article_id: ind.qocal_amend_line_items_pricing_procedure.htm
title: Update Quote and Order Actions After Pricing Procedure Changes
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_amend_line_items_pricing_procedure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.pricing_pricing_action_parameters.htm
fetched_at: 2026-11-23
---

# Update Quote and Order Actions After Pricing Procedure Changes

Actions don't update when a pricing procedure changes an amended line item's sales price. Use a post-pricing Apex class to update the actions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To set up and use advanced detail line pricing:	

Salesforce admin

AND

Pricing Design Time User permission set

When you amend an asset, Revenue Cloud determines the action for each quote line item or order item, such as Amend or No Change. The action resolution service sets the action based on changes to the line item, and it runs before the pricing procedure. If the pricing procedure changes the sales price of an amendment line item, for example, by using a calculation matrix, the action doesn't update right away. Revenue Cloud re-evaluates the action only when you run a new transaction.

If you change the sales price manually, the action does update to Amend as expected, because a manual change happens before Revenue Cloud determines the action.

To show the updated action immediately after the pricing procedure changes the sales price, add a custom post-pricing Apex class that explicitly updates the action.

Create a post-pricing Apex class that updates the quote action or order action for each line item whose sales price the pricing procedure changes. See the example section. Model your class on the example in Use Advanced Transaction Detail Line Pricing to Map Custom Fields.

IMPORTANT When the Sales Price Amendments setting is on, changing the sales price on an amendment line item can generate detail lines. If you don't need detail lines, from Setup, find and select Revenue Settings, and then turn off Sales Price Amendments.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_amend_line_items_pricing_procedure.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
