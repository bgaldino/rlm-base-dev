---
article_id: ind.billing_tax_engine_create.htm
title: Create a Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_engine_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_standard_tax_rate.htm
fetched_at: 2026-11-23
---

# Create a Tax Engine

Create a tax engine record that Billing uses to calculate tax. Set the type to Revenue Standard Tax Engine. When you extend the Revenue Standard Tax Engine, associate a custom metadata type and a decision table.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create tax engines:	Tax Admin permission set
NOTE The Standard User profile includes the View Developer Name system permission. Users need this permission to use the Revenue Standard Tax Engine. When you clone the Standard User profile, keep View Developer Name on the cloned profile, or add it to a permission set assigned to the user.
From the App Launcher, find and select Tax Engines.
Click New.
Enter a name for the tax engine.
Select the type as Revenue Standard Tax Engine.
If the Type field is empty, Revenue Cloud Tax Extension is considered as the value.
When you extend the Revenue Standard Tax Engine, complete these fields.
Enter the API name of the custom metadata type in Custom Metadata Type API Name. See Configure Custom Metadata Types.
Custom Metadata Type API Name is the API name of the custom metadata type that maps billing transaction fields to Revenue Standard Tax Entries decision table inputs and outputs. The tax engine references this custom metadata type to identify which field mappings to apply when it evaluates the decision table.
Select the cloned decision table in Decision Table. See Clone the Decision Table.
The Revenue Standard Tax Engine matches tax rates with this decision table. If this field is blank, the engine uses the Revenue Standard Tax Entries decision table. To match custom tax rate fields, select your cloned table and make sure that table is active. The decision table must be active.
Select the status as Active.
You can use only active tax engines to calculate taxes.
To capture taxes at the header level, select Capture Taxes At Header.
The Capture Taxes At Header checkbox appears only when Credit, Payment, and Refund Application Level is Header Level. See Capture Taxes at Header Level.
Save your changes. Here’s how the tax engine appears after you associate the custom metadata type and decision table.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_tax_engine_create.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
