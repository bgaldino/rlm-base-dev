---
article_id: ind.pricing_calculate_margin_by_using_a_standard_cost_book.htm
title: "Example: Calculate Margin by Using a Standard Cost Book"
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_margin_by_using_a_standard_cost_book.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_define_costs_in_cost_books.htm
fetched_at: 2026-11-23
---

# Example: Calculate Margin by Using a Standard Cost Book

Salesforce Pricing doesn't bring cost data into the quote line or calculate margin automatically. This example shows one way to surface cost on the quote line item and calculate margin from it, using standard Salesforce Pricing building blocks and custom fields.

REQUIRED EDITIONS

This article is an illustrative example, not a packaged feature or a supported configuration path. Object names, field names, tag names, and formulas in this topic are examples only. Your context definition, mapping, pricing recipe, and pricing procedure can be structured differently. Treat every name and value here as a placeholder, and adapt each step to match your Salesforce org. Work with a Salesforce administrator or implementation partner if you aren't familiar with context definitions, decision tables, and pricing procedures.

Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To create and manage cost books:	Salesforce Pricing Design Time User

In this example, a sales representative opens a quote, adds a product, and views three line-item values that Salesforce Pricing doesn't display by default: product cost, margin percentage, and margin amount. To achieve this outcome:

Record the product cost in a cost book.
Add custom fields to hold cost and margin on the quote and quote line item.
Extend the context definition so the cost book ID and unit cost flow through pricing calculations.
Build a decision table that looks up the cost for a product from its cost book entry.
Add that decision table to a pricing recipe and pricing procedure so the engine fetches the cost during calculation.
Display the new fields on the quote record layout.
Create a Cost Book and Cost Book Entry

Follow Define Cost Books to create a cost book and add a cost book entry for a product.

Add Custom Fields

The following field names are examples. Use names that fit your org’s naming conventions, and check for existing fields before creating new ones.

On the Quote object, create a custom Text field to hold the related cost book ID (for example, `Example_Cost_Book_Id__c`).
On the Quote Line Item object, create:
A Currency field to hold the unit cost (for example, `Example_Unit_Cost__c`).
A Formula field for total cost (for example, `Example_Total_Cost__c` = `Example_Unit_Cost__c * Quantity`).
A Formula field for margin percentage (for example, `Example_Margin_Percent__c` = `(NetTotalPrice - (Example_Unit_Cost__c * Quantity)) / NetTotalPrice`).
A Formula field for margin amount (for example, `Example_Margin_Amount__c` = `NetTotalPrice - (Example_Unit_Cost__c * Quantity)`).
NOTE In this example, Salesforce Pricing doesn't calculate margin automatically. It only supplies the cost value. The margin calculation occurs in your custom formula field.
Extend the Context Definition
In the extended sales transaction context definition, add two attributes:
An Input/Output String attribute at the transaction level to carry the cost book ID (for example, `ExampleCostBookId`).
An Input/Output Currency attribute at the line-item level to carry the unit cost (for example, `ExampleUnitCost`).
Add each attribute as a tag.
In the context mapping:
Map the cost book ID tag to the custom Quote field (`Example_Cost_Book_Id__c`).
Map the unit cost tag to the custom Quote Line Item field (`Example_Unit_Cost__c`).
NOTE Ensure that your mapping matches the object you're pricing. For example, don't map Quote tags onto an Opportunity mapping.
Build a Decision Table to Look Up Cost
Add the decision table to the pricing recipe, mapping its output to a unit price or cost field.
In the pricing procedure, add a lookup element that uses this decision table:
Map the cost book ID and product for the current line as inputs.
Map the output result to the `ExampleUnitCost` tag created in the context definition.
Save and activate the pricing procedure.
Display Cost and Margin on the Quote

Add the custom Quote Line Item fields (`Example_Unit_Cost__c`, `Example_Total_Cost__c`, `Example_Margin_Percent__c`, and `Example_Margin_Amount__c`) to the line item layout or the Transaction Line Editor so sales representatives can view them.

Test the Configuration

Create a quote, add a product that has a cost book entry, and confirm that the cost, margin percentage, and margin amount gets calculated as expected. If a value doesn't populate, verify that the context mapping matches the target object type and that the decision table is active.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_margin_by_using_a_standard_cost_book.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
