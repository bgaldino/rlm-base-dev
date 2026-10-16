---
article_id: ind.pricing_pricing_recipes.htm
title: Pricing Recipes Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_recipes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_set_up_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Pricing Recipes Setup

Pricing Recipes in Salesforce Pricing enable you to create and manage detailed pricing strategies. These recipes associate data from selected objects with decision tables to develop comprehensive pricing procedures. Understanding pricing recipes is crucial for successfully leveraging Salesforce Pricing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
How Pricing Recipes Work

A pricing recipe groups decision tables that serve as a data source for your pricing infrastructure. Pricing recipes also provide a one-point configuration for how decision tables are used within procedures.

Salesforce Pricing offers you flexible, data-model independent pricing, retrieving values from any field. You can map a pricing recipe to a decision table, then use Dynamic Output Mapping to define custom outputs for your elements. This provides precise control over pricing calculations. We simplify setup with a predefined recipe and standard decision tables, accelerating your procedure creation.

Select a Pricing Recipe for Your Salesforce Org
Every Salesforce org requires a pricing recipe to define its pricing strategy. When Salesforce Pricing is activated, your org is automatically set up with a predefined recipe, though you can only have one active pricing recipe at a time. This recipe is essential for managing detailed pricing procedures.
Create a Pricing Recipe
Learn how to create a custom pricing recipe to group and associate your custom decision tables, enabling precise control over pricing calculations in your Salesforce org. This task is essential when the predefined recipe doesn't meet your specific business needs. Use the Subtype field to set up the default pricing recipe and decision tables for each cloud, such as Revenue Cloud or Life Sciences Cloud. While building or editing a pricing procedure, element lookups display only the decision tables linked to the default recipe of that procedure's subtype.
Modify Price Adjustment Matrices
Customize your pricing recipes by associating them with decision tables, allowing you to offer customers discounts based on specific conditions.
Sync Decision Tables in a Pricing Recipe
To sync decision tables for a specific pricing recipe:
