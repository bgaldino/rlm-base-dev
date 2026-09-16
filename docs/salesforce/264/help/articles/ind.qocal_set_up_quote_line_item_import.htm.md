---
article_id: ind.qocal_set_up_quote_line_item_import.htm
title: Set Up Quote Line Items Import
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_quote_line_item_import.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_quote_line_item_import.htm
fetched_at: 2026-09-04
---

# Set Up Quote Line Items Import

Turn on the Import Quote Line Items setting and create a Data Processing Engine definition to perform bulk quote creation from CSV files.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Turn On Import Quote Line Items

Before you begin, perform these actions.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To turn on the Import Quote Line Items setting:	Advanced CSV Data Import permission set
On the Revenue Settings page:
Turn on Enable Groups in quotes and orders.
Turn off Hide Price Refresh Notification.
Add product codes to all products intended for import.
In Setup, find and select Revenue Settings.
Turn on Import Quote Line Items.
The Import Lines button now appears on quote pages.
In the Flow for Importing Quote Line Items field, enter the API name of the flow that processes the imported quote line items.
To use the predefined flow, keep the default value, transactionManagement__ImpQuotLineItm.
To use a custom flow, enter your specific flow API name.
The flow opens when a user clicks Import Lines.
Create and Set Up a Data Processing Engine Definition

Create a Data Processing Engine definition to process CSV data and create quote line items. Revenue Management provides templates based on organization type.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create a Data Processing Engine definition:	

Customize Application

AND

Modify All Data

Revenue Management provides these Data Processing Engine definition templates.

ORG TYPE	NAME	API NAME
Single-currency	Create Quote Line Items from a CSV File	CreateQuoteLineItemsFromCSV
Multicurrency	Create Quote Line Items from a CSV File in Multi-Currency Orgs	CreateQuoteLineItemsWithCurrencyFromCSV
NOTE These definitions use the Core execution platform type and don’t open in the Data Processing Engine builder. To learn how to edit these definitions, see Customize Data Processing Engine Definitions for Quote Line Item Imports .
In Setup, find and select Data Processing Engine.
Next to the preferred template, click  and select Save As.
Enter a name, API name, and description, and save your changes.
Next to your new definition, click  and select Activate.
In Setup, find and select Revenue Settings.
Select your activated definition from the Data Processing Engine Definition for Importing Quote Line Items dropdown.
Test the definition by performing a quote line item import.

After you complete the setup:

Monitor import status by using Monitor Workflow Services.
Extend the import functionality to support more requirements, such as custom fields.
