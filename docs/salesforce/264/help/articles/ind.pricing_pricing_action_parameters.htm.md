---
article_id: ind.pricing_pricing_action_parameters.htm
title: Pricing Action Parameters
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_action_parameters.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_unique_pricing_scenarios.htm
fetched_at: 2026-11-23
---

# Pricing Action Parameters

To calculate the price of products directly from any object’s record page, use the Calculate Price button. All pricing actions are associated with a context definition and a pricing procedure so that the pricing data that is processed during the pricing process is stored directly in the Salesforce object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

There are two types of pricing action buttons.

Standard Pricing Action button: Configure objects such as Quote, Order, Contract, Case, and Opportunity to show the pricing action button on their record page by editing their page layout.
Custom Pricing Action button: Add the pricing action button as a Lightning component by editing the page directly from the object’s record page.
Get Ready to Create Pricing Actions
Before you create pricing actions, complete these prerequisites.
Standard Pricing Actions
To view the pricing action button on the object’s record page, edit the page layout of the object.
Update Quote and Order Actions After Pricing Procedure Changes
Actions don't update when a pricing procedure changes an amended line item's sales price. Use a post-pricing Apex class to update the actions.
Customize the Pricing Action Button by Using Lightning Components
Add the Pricing Calculation standard Lightning component to object record pages to make custom pricing actions available across your org and calculate the price of a product directly from the record page.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_action_parameters.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
