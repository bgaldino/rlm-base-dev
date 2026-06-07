---
article_id: ind.product_catalog_set_up_enhanced_product_discovery_features.htm
title: Set Up Enhanced Product Discovery Features
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_set_up_enhanced_product_discovery_features.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Set Up Enhanced Product Discovery Features

Turn on enhanced Product Discovery features so that Product Discovery can show transaction previews, configuration rule outcomes, and rule-based recommendations, and automatically save product changes while users browse the catalog.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To manage enhanced product discovery:	Product Catalog Management Designer

Before you begin:

Product Discovery is enabled in your org.
Product Catalog Management is configured for the catalog you use for quoting.
Turn On Enhanced Product Discovery Features
From Setup, in the Quick Find box, enter Product Discovery, and then select Product Discovery Settings.
Turn on Transaction Preview, Configuration Rules, Product Recommendations, and Auto Save.
Configure Constraint Rules for Product Discovery

In Product Configurator, you can define rules in a constraint model to control how products behave during Product Discovery, including which products are disabled, which products are recommended, and which messages users see. After you activate the model, Product Discovery evaluates these rules in real time as users add products to the transaction.

NOTE

Set the virtual type annotation to true for the transaction type so Product Discovery can evaluate rules against the transaction header, such as a Quote or Order, during catalog browsing.

Set up Constraint Rules Engine for Product Configurator. See Set Up Constraint Rules Engine for Product Configurator
Create a Constraint Model
In the constraint model, add or update rules that evaluate transaction line items.

Use disable rules to make products unavailable when the current transaction meets specific conditions. Use message rules to show info, warning, or error messages when the current transaction meets specific conditions. Use recommendation rules to show related or add-on products based on the current transaction, without blocking selection.

Save your changes to the constraint model.
Activate the updated model so Product Discovery evaluates the rules at run time.

For detailed rule authoring, see the Constraint Modeling Language
