---
article_id: ind.product_configurator_visual_builder_preference_rule.htm
title: Preference Rule
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_visual_builder_preference_rule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_visual_builder_constraint_and_rule_types.htm
fetched_at: 2026-09-04
---

# Preference Rule

The preference rule applies a constraint when certain conditions are true, but allows the constrainte engine to override the constraint if the user input violates the constraint conditions. For example, use the preference rule to specify that, when laptop display is 2K, the display size should be 15 inch or larger, but allow the configuration to continue without failing if the user selects a smaller display size, and deliver an error message indicating that display size should be 15 inch or larger.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

Enter one or more expressions to define the conditions to be met, then enter one or more expressions to defined the preferred outcome. This outcome is overridden if the user enters input that violates the conditions to be met. Include an optional run-time message to show to the user when their input violates the rule conditions.

NOTE If a preference rule auto-adds a product that has one or more Product Selling Model Options (PSMOs), set one PSMO on the product to Default. The system uses the default PSMO to determine which pricebook entry to use for the auto-added product. For more information on Product Selling Model Options, see Manage Product Selling Model in Revenue Management.
