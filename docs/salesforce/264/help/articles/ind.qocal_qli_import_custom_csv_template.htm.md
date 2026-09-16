---
article_id: ind.qocal_qli_import_custom_csv_template.htm
title: Custom CSV Templates for Quote Line Item Imports
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_custom_csv_template.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_qli_import_extend_functionality.htm
fetched_at: 2026-09-04
---

# Custom CSV Templates for Quote Line Item Imports

Customize the import process to meet specific business needs by creating a custom CSV template. Custom templates support the addition of unique fields while maintaining the structure required for data processing.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

Update the downloadable CSV template that your sales reps use to import quote line items.

Create a CSV file template containing the required headers.
Define a static resource in Setup and upload the template file.

After creating the static resource, complete these setup tasks.

Customize the Import Quote Line Items flow and specify the new static resource to make sure that users download the correct file. See Import Quote Line Items.
Customize the Data Processing Engine definition to update the processing logic for the new headers. .
Considerations for Custom CSV Template
Download and review the default CSV template headers to determine if a custom version is necessary. If you use custom templates, adhere to these requirements.
