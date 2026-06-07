---
article_id: ind.qocal_qli_import_extend_functionality.htm
title: Quote Line Item Import Extension
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_extend_functionality.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Quote Line Item Import Extension

The default import setup supports data entry for standard, commonly used fields. Customize the import process to meet unique business requirements by adding custom fields, modifying the import flow, or changing the processing logic.

/apex/HTViewHelpDoc?id=ind.Chunk1966530487.htm#qocal_qli_import_custom_csv_template

Considerations for Customizing the Quote Line Item Import Flow
When users select import lines, Transaction Management uses a flow to provide options for downloading a CSV template and uploading a CSV file for processing. Review these requirements and limits to customize the import flow effectively.
Customize Data Processing Engine Definitions for Quote Line Item Imports
Modify the Data Processing Engine definition if you want users to import custom fields. Transaction Management uses this definition to process quote line items after a user uploads a CSV file.
