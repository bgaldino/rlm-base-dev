---
article_id: ind.qocal_qli_import_considerations_custom_csv_template.htm
title: Considerations for Custom CSV Template
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_considerations_custom_csv_template.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_qli_import_custom_csv_template.htm
fetched_at: 2026-09-04
---

# Considerations for Custom CSV Template

Download and review the default CSV template headers to determine if a custom version is necessary. If you use custom templates, adhere to these requirements.

Include a unique row identifier, such as RowNumber.
Include a unique product identifier, such as ProductCode.
Include the product quantity, such as Quantity.
Include the product selling model, such as ProductSellingModelName.
Include the billing frequency when you turn on Billing.
Exclude headers for read-only or calculated fields, such as List Price and Net Unit Price.
Limit the template to 18 columns.
The Data Processing Engine definition supports 20 columns, but the Transaction Management flow adds the quoteId and quoteLineGroupId columns at run time.
Create attributes in the extended Sales Transaction context definition and map them to any custom fields added to the template.
