---
article_id: ind.billing_standard_tax_custom_metadata_types_configure.htm
title: Configure Custom Metadata Types
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_standard_tax_custom_metadata_types_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_extend_revenue_standard_tax_engine.htm
fetched_at: 2026-09-04
---

# Configure Custom Metadata Types

Create a custom metadata type that maps billing transaction fields to decision table columns for the Revenue Standard Tax Engine.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create a custom metadata type and custom fields:	Tax Admin permission set

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
