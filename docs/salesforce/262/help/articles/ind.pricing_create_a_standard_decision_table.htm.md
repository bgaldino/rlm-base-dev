---
article_id: ind.pricing_create_a_standard_decision_table.htm
title: Create a Decision Table
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_a_standard_decision_table.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create a Decision Table

To evaluate pricing rules and return specific pricing data such as list prices, discounts, or volume tiers, configure a standard decision table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create and manage decision tables:	

Salesforce Pricing Design Time

When you configure decision tables for pricing, each combination of input values must resolve to a single, unique row. Salesforce Pricing doesn't support retrieving multiple outputs for the exact same input criteria. Set up your decision table to map each specific input value to only one output entry.

1. From the App Launcher, search for and select Lookup Tables.
Select Decision Table, and then click New
Enter a name for your decision table, and then press Tab to autopopulate the API Name.
Select Pricing as the application usage.
Select Advanced as the decision table type.
Click Save & Next.
In the Source Object field, select the standard or custom object that contains your pricing data.
Define your input conditions:
Select the appropriate source object fields and set their operators.
Verify that the Condition Type (for example, All conditions are met (AND)) aligns with your required pricing logic.
Specify the result details by selecting the source object fields that you want to return as outputs, and define a column name for each.
Click Save & Next.
Review your configuration, and click Save & Next again.
Click Finish.
On the decision table record page, click Activate.
