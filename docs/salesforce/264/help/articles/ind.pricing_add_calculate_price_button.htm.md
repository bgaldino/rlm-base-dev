---
article_id: ind.pricing_add_calculate_price_button.htm
title: Add the Calculate Price Button
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_add_calculate_price_button.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_standard_pricing_actions.htm
fetched_at: 2026-09-07
---

# Add the Calculate Price Button

To make the standard button for pricing action visible on your object’s record page, configure the object’s page layout from Object Manager.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To edit page layouts:	Customize Application

Before you begin, define the pricing parameters that connect the pricing action button to your context definition, mapping, and pricing procedure. See Configure Pricing Action Parameters for Standard Objects

IMPORTANT

Salesforce Pricing doesn't work directly with the SalesTransactionContext__stdctx base context definition. To configure Standard Pricing Actions, always extend the base context. An extended context definition inherits the structure, nodes, and attributes from the base context definition while allowing you to add custom nodes, attributes, and tags for your pricing logic.

The standard Calculate Price button is only for pricing Salesforce objects and doesn't support custom data hydration.

The more complex Quotes and Orders logic, which uses custom hydration for bundles and derived products, requires a custom-built pricing button that can act on persisted (saved) data. Therefore, the standard button should not be considered a replacement for Transaction Management's pricing logic.

From Setup, in Object Manager, select any one of these objects: Quote, Order, Contract, Case, and Opportunity. For example, let’s select Opportunity.
Select Page Layouts, and then click Opportunity Layout.
In the palette, click Buttons.
Drag Calculate Price to the Opportunity Detail section under Salesforce Mobile and Lightning Experience Actions in the layout.
Save your changes.
