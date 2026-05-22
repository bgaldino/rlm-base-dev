---
article_id: ind.pricing_get_ready_to_build_pricing_procedures.htm
title: Prerequisites to Build Pricing Procedures
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_get_ready_to_build_pricing_procedures.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Prerequisites to Build Pricing Procedures

Before you begin creating pricing procedures and adding elements to them, ensure you have completed these prerequisites. Understanding the fundamentals is crucial for successful implementation and operation of your pricing strategies.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create context definitions:	

Salesforce Pricing Design Time


To create, edit, and activate a decision table in Salesforce Pricing:	Salesforce Pricing Design Time
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time
Decision Tables
Decision tables are essential as they match your input values with the input rows in a decision table, returning the matching row’s output pricing element that uses it in a pricing procedure.
Context Definitions
Context definitions contain the necessary information to run the pricing process. This includes the relationship between nodes and their structure, attributes, context tags, and mapping. Mapping defines the nodes and attributes with the correct input data from Salesforce objects. The pricing procedure runs with its associated tags and writes the results back to the context definition that the tags belong to. A crucial point to remember is that a context tag can’t have the same name as the decision table's label or API name.
Add Products as Price Book Entries
Record each product or service you sell as a product in Agentforce Revenue Management. These products, also referred to as line items, have a specific selling price and are added as entries to a price book.
Configure a Product Selling Model for Your Products
Product selling models define how products are sold—be it one-time, term-defined, or evergreen subscriptions. They provide flexibility in managing diverse product offerings and streamline how those products are quoted, ordered, and renewed within a revenue management system. These models are crucial for accurately representing different sales approaches for your products.
Create Constant Resources
If your variables lack context tags, create a constant resource to serve as a placeholder for fixed values in your pricing procedures. Constants are used for inputs, outputs, and other values passed from a pricing element.
