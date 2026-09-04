---
article_id: ind.product_configurator_visual_builder_require_rule.htm
title: Require Rule in the Visual Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_visual_builder_require_rule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_visual_builder_constraint_and_rule_types.htm
fetched_at: 2026-09-04
---

# Require Rule in the Visual Builder

The require rule automatically adds a specified product to a configuration if certain conditions are true. Use the require rule to make sure that certain products are sold together.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

In the require rule window, add one or more expressions to define conditions. Then, select an item that must be included if those conditions are true. Specify the quantity and default attribute values for the included item as needed. For example, use the require rule to specify that a laptop must always include a blue laptop bag.

NOTE If a require rule auto-adds a product that has one or more Product Selling Model Options (PSMOs), set one PSMO on the product to Default. The system uses the default PSMO to determine which pricebook entry to use for the auto-added product. For more information on Product Selling Model Options, see Manage Product Selling Model in Revenue Management.
