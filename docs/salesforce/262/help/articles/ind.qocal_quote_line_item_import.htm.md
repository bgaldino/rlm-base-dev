---
article_id: ind.qocal_quote_line_item_import.htm
title: Quote Line Item Imports
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_quote_line_item_import.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Quote Line Item Imports

Importing quote line items from a CSV file accelerates the quoting process by eliminating manual data entry for large volumes of products. Agentforce Revenue Management uses Transaction Management components to process these imports, ensuring data consistency across multiple product types and currency models.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

The import process relies on specific templates and automated flows to handle data.

The CSV template provides standardized headers for common fields, such as ProductCode, ProductName, and ProductSellingModelName.
The import flow manages the user experience and facilitates CSV template downloads and file uploads for processing.
Data Processing Engine definition templates provide the necessary backend support for both multicurrency and single-currency organizations.

The import functionality supports standard quote line items and accommodates custom requirements. Salesforce admins extend the default behavior to include custom fields, ensuring the import meets unique business needs.

/apex/HTViewHelpDoc?id=ind.Chunk1113763236.htm#qocal_set_up_quote_line_item_import

Quote Line Item Import Extension
The default import setup supports data entry for standard, commonly used fields. Customize the import process to meet unique business requirements by adding custom fields, modifying the import flow, or changing the processing logic.
/apex/HTViewHelpDoc?id=ind.Chunk507849811.htm#qocal_qli_import_user_import_lines_csv
