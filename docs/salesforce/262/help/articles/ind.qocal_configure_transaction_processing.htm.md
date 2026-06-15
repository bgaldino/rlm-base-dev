---
article_id: ind.qocal_configure_transaction_processing.htm
title: Set Up the Transaction Processing Type for Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_configure_transaction_processing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up the Transaction Processing Type for Quotes and Orders

Define how Agentforce Revenue Management processes transactions by selecting a default Transaction Processing Type (TPT).

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create transaction processing type records and to select a default transaction processing type:	

Customize Application

AND

View Setup and Configuration

Set a default processing type for all transactions and define exceptions via the Tooling API. Use these configurations to turn on the Advanced Configurator or skip tax calculations. Help your sales representatives override the default, add the Transaction Type field to quote, and order page layouts.

IMPORTANT Select the default transaction type carefully. This action is irreversible after enablement.
Create a Transaction Processing Type record and specify preferences that use the TransactionProcessingType Tooling API a
From Setup, in the Quick Find box, search for and select Revenue Settings.
Turn on Transaction processing for quotes and orders.
Add the Transaction Type field to quote and order page layouts to provide override capabilities. See Customize Page Layouts with the Enhanced Page Layout Editor and Modify Field Access Settings.
