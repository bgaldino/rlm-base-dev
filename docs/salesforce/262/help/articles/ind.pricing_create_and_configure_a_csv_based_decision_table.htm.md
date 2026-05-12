---
article_id: ind.pricing_create_and_configure_a_csv_based_decision_table.htm
title: Create and Configure a CSV-Based Decision Table
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_and_configure_a_csv_based_decision_table.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create and Configure a CSV-Based Decision Table

You can use CSV-based decision tables to manage medium-scale pricing logic. After you create them, map these decision tables to a pricing recipe and use them in your pricing procedures.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create and manage decision tables:	

Salesforce Pricing Design Time

NOTE All CSV-based decision tables created after the Usage 262 upgrade are automatically versioned.
CSV-Based Decision Table Limitations
Before configuring a CSV-Based Decision Table, keep these points in mind.
Create the Decision Table
From the App Launcher, find and select Lookup Tables.
Select Decision Table, and click New.
Specify the basic details, and select Pricing as the application usage.
Select Advanced as the Decision Table Type. 
For the Source Object, select CSV.
Define your input columns, such as Product and Price Book, and then define your output columns, such as Unit Price and Discount.
Click Save.
Upload Data to the Decision Table 
When you save the decision table, Salesforce Pricing creates a single, inactive version by default. For steps to upload CSV data for the decision table, see Add CSV Data to Decision Tables.
Activate and Map the Decision Table
After the data uploads successfully, activate the decision table version.
Go to Pricing Recipes, and select the recipe that you want to modify (for example, Price Adjustment Matrix).
Map your new CSV-based decision table to the recipe by specifying the relevant input, output, and discount type columns.
Save your changes. You can now select this decision table within the elements of your pricing procedure.
