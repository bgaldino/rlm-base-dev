---
article_id: ind.qocal_qli_import_user_import_lines_csv.htm
title: Import Quote Line Items from a CSV File
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_user_import_lines_csv.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_quote_line_item_import.htm
fetched_at: 2026-09-04
---

# Import Quote Line Items from a CSV File

Create quotes faster by importing quote line items from CSV files. After the import completes, configure the products and view the prices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To download the CSV template file and import quote line items:	Advanced CSV Data Import permission set

To import quote line items, download the CSV template, add your data, and upload the file to your quote record.

Open a quote record page.
Click Import Lines.
Click Download CSV Template to receive a template containing headers.
Add quote line items to the downloaded template.
Click Upload Files.
Browse and select your file, and then click Open.
Click Import.
If the process completes or fails, receive a notification.
If the import fails, access Revenue Transaction Error Log records from the related list on the quote to identify and fix issues.
Configure quote line items and make any other necessary changes to the quote after a successful import.
If the file upload doesn't complete and the Done button remains disabled, see Understanding "Query Non Vetoed Files" Permission and File Access.
WARNING Transaction Management suspends all actions on the quote while the import is in progress.
Considerations for Creating a CSV File
Familiarize yourself with recommendations, supported products, required fields, and limits before creating your file.
