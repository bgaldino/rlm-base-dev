---
article_id: ind.billing_standard_tax_decision_table_clone.htm
title: Extend Your Revenue Standard Tax Engine
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_decision_table_clone.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_extend_revenue_standard_tax_engine.htm
fetched_at: 2026-11-23
---

# Extend Your Revenue Standard Tax Engine

Apply tax rates based on custom attributes, such as product category, customer attributes, or exemption criteria, without writing Apex code. Use a custom metadata type to map billing transaction fields to a cloned Revenue Standard Tax Entries decision table, and persist matched values on invoice and credit memo tax lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create a custom metadata type and custom fields:	Tax Admin permission set
To change the decision table:	Rule Engine Designer permission set
NOTE The Standard User profile includes the View Developer Name system permission. Users need this permission to use the Revenue Standard Tax Engine. When you clone the Standard User profile, keep View Developer Name on the cloned profile, or add it to a permission set assigned to the user.
Configure Custom Metadata Types

Create a custom metadata type that maps billing transaction fields to decision table columns for the Revenue Standard Tax Engine.

Before you begin, create the custom fields on the Tax Rate object that you want to use as matching criteria or as outputs on tax lines. Also create any custom fields you need on invoice line tax and credit memo line tax. See Create a Custom Field.

Create a custom metadata type.
Click New in the Custom Fields section of the created custom metadata and create these fields exactly as shown here.
FIELD LABEL	API NAME	FIELD TYPE	DESCRIPTION
Entity Field Name	Entity_Field_Name__c	Metadata Relationship (Field Definition)	The field on that object whose value is used when calculating tax.
Entity Name	Entity_Name__c	Metadata Relationship (Entity Definition)	The billing object that this mapping applies to. This field controls Entity Field Name.
Request/Response	Request_Response__c	Picklist. Add these values: Request, Response.	The Request value used as a decision table input. The Response value used to store the matched value on the tax line.
Tax Field Name	Tax_Field_Name__c	Text	The name that links the billing field to the decision table column.
Tax Rate Entity Name	Tax_Rate_Entity_Name__c	Metadata Relationship (Entity Definition)	The Tax Rate entity used in the mapping. This field controls Tax Rate Input Field Name and Tax Rate Output Field Name.
Tax Rate Input Field Name	Tax_Rate_Input_Field_Name__c	Metadata Relationship (Field Definition)	The Tax Rate field used as a decision table input when matching a tax rate.
Tax Rate Output Field Name	Tax_Rate_Output_Field_Name__c	Metadata Relationship (Field Definition)	The Tax Rate field used as a decision table output. Fill this field when Request/Response is Response.
Save the changes. Here’s how a configured custom metadata type appears.
To define records, click Manage [Your Custom Metadata Type Label].
To add your custom field mappings, click New.
For each field mapping, provide the entity name, entity field name, tax field name, request/response, tax rate entity name, and tax rate input or output field values.
Save the changes. Here’s how a configured tax mapping appears.
Clone the Decision Table

Clone the Revenue Standard Tax Entries decision table and add the custom columns that you use to match tax rates.

From the App Launcher, find and select Lookup Tables.
Open Revenue Standard Tax Entries.
From the Show menu, click Clone, enter a name and API name, and save.
Add custom input or output columns from the Tax Rate object to the cloned decision table.
Configure the required setting and operator for each custom input column. See Create a Decision Table and How Null Values Work in Decision Tables.
Activate and refresh the cloned decision table. See Activate a Decision Table and Refresh a Decision Table.

After you configure the custom metadata type and activate the cloned decision table, associate both with a tax engine. Set Type to Revenue Standard Tax Engine, enter the Custom Metadata Type API Name, and select the Decision Table. See Create a Tax Engine.

NOTE After you add or change a tax rate, refresh the cloned decision table so Billing uses the latest rates. See Refresh a Decision Table.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_decision_table_clone.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
