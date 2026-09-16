---
article_id: ind.billing_standard_tax_decision_table_clone.htm
title: Clone the Decision Table
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_decision_table_clone.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_extend_revenue_standard_tax_engine.htm
fetched_at: 2026-09-04
---

# Clone the Decision Table

Clone the Revenue Standard Tax Entries decision table and add the custom columns that you use to match tax rates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To change the decision table:	Rule Engine Designer permission set
From the App Launcher, find and select Lookup Tables.
Open Revenue Standard Tax Entries.
From the Show menu, click Clone, enter a name and API name, and save.
Add custom input or output columns from the Tax Rate object to the cloned decision table.
Configure the required setting and operator for each custom input column. See Create a Decision Table and How Null Values Work in Decision Tables.
Activate and refresh the cloned decision table. See Activate a Decision Table and Refresh a Decision Table.

After you configure the custom metadata type and activate the cloned decision table, associate both with a tax engine. Set Type to Revenue Standard Tax Engine, enter the Custom Metadata Type API Name, and select the Decision Table. See Create a Tax Engine.

NOTE After you add or change a tax rate, refresh the cloned decision table so Billing uses the latest rates. See Refresh a Decision Table.
