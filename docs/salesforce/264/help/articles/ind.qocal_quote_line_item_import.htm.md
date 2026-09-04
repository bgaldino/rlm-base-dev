---
article_id: ind.qocal_quote_line_item_import.htm
title: Quote Line Item Imports
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_quote_line_item_import.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_features.htm
fetched_at: 2026-09-04
---

# Quote Line Item Imports

Importing quote line items from a CSV file accelerates the quoting process by eliminating manual data entry for large volumes of products. Revenue Management uses Transaction Management components to process these imports, ensuring data consistency across multiple product types and currency models.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

The import process relies on specific templates and automated flows to handle data.

The CSV template provides standardized headers for common fields, such as ProductCode, ProductName, and ProductSellingModelName.
The import flow manages the user experience and facilitates CSV template downloads and file uploads for processing.
Data Processing Engine definition templates provide the necessary backend support for both multicurrency and single-currency organizations.

The import functionality supports standard quote line items and accommodates custom requirements. Salesforce admins extend the default behavior to include custom fields, ensuring the import meets unique business needs.

Set Up Quote Line Items Import
Turn on the Import Quote Line Items setting and create a Data Processing Engine definition to perform bulk quote creation from CSV files.
Quote Line Item Import Extension
The default import setup supports data entry for standard, commonly used fields. Customize the import process to meet unique business requirements by adding custom fields, modifying the import flow, or changing the processing logic.
Import Quote Line Items from a CSV File
Create quotes faster by importing quote line items from CSV files. After the import completes, configure the products and view the prices.
