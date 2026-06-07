---
article_id: ind.pricing_pricing_procedures.htm
title: Build Your Pricing Procedures Using Salesforce Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_pricing_procedures.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Build Your Pricing Procedures Using Salesforce Pricing

Pricing procedures are fundamental to all pricing strategies in Agentforce Revenue Management, enabling businesses to implement dynamic pricing rules and efficiently calculate a product's final net price. They act as the core engine for pricing calculations in Salesforce Pricing, providing a flexible and powerful way to manage both simple and complex pricing scenarios.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

Pricing procedures calculate prices using your data. They pull information from wherever the relevant data is, for example, from decision tables, formulas, and custom objects. These procedures are made up of rules, conditions, and formulas, and you can easily configure them to create smart, flexible pricing strategies that change as your business does. Furthermore, they provide a visual representation of calculations using Price Waterfall, simplifying the understanding and management of complex pricing scenarios.

While you technically can create custom pricing procedures, we strongly recommend leveraging the predefined pricing procedures. They are designed to ensure consistency across all your pricing, and deliver accurate pricing calculations every time.

Understand Pricing Elements
Pricing elements are the primary components that make up a pricing procedure in Salesforce Pricing within Agentforce Revenue Management. They are the building blocks, where each element represents a step in the calculation of a product's final price. Understanding pricing elements is essential for successfully defining and calculating product prices and creating customized pricing strategies.
Prerequisites to Build Pricing Procedures
Before you begin creating pricing procedures and adding elements to them, ensure you have completed these prerequisites. Understanding the fundamentals is crucial for successful implementation and operation of your pricing strategies.
Configure Your Pricing Procedure
Assemble a pricing procedure using pricing elements and ensure accurate pricing for your products.
Simulate and Activate Your Pricing Procedure
Test and validate that your pricing rules and values added to your pricing procedure return accurate results. If your procedure doesn’t work as expected, edit your values or variables, and try again. When you’re satisfied, activate your pricing procedure.
Simple Pricing Procedure Example
Let’s configure and simulate a simple pricing procedure using some common pricing elements to calculate discounts for a laptop.
Use the Default Revenue Management Pricing Procedure
While you can create custom pricing procedures, we strongly recommend using the predefined versions. These predefined procedures bring consistency to your org and deliver accurate calculations.
Automate Context Tag Mapping with Einstein Generative AI

Set Up Parallel Pricing Element Execution
Run multiple pricing procedures concurrently or use parallel processing within a single pricing procedure to ensure faster and more efficient pricing, especially in complex scenarios.
Decision Explainer for Salesforce Pricing
Use Decision Explainer to customize the Salesforce Pricing waterfall structure and generate dynamic explanations for the resulting pricing outcomes.
