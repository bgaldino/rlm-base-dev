---
article_id: ind.qocal_qli_import_user_considerations.htm
title: Considerations for Creating a CSV File
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_qli_import_user_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_qli_import_user_import_lines_csv.htm
fetched_at: 2026-09-04
---

# Considerations for Creating a CSV File

Familiarize yourself with recommendations, supported products, required fields, and limits before creating your file.

Enter values for all required fields, which include ProductCode, RowNumber, and Quantity in the default template.
Include the Billing Frequency if you turn on Billing.
Provide the ProductSellingModelName for products with product selling models.
Use unique values in the RowNumber column, though they appear in any order.
Match the values in the ProductCode and ProductSellingModelName columns to the values defined in Revenue Management.
Use unique values in the ProductName column to identify rows if they fail to process.
Make sure that all associated products have product codes before attempting an import.
Import only the root product to add a bundle product. Manually configure child products after the import finishes.
Import the source product in the CSV file or ensure it exists in the quote to import a product that uses derived pricing.
Refrain from importing usage-based products as they lack support.
Import static product bundles and products with static attributes only after an admin configures the Data Processing Engine definition to populate related default records.
Add quote line items to initial and amendment quotes.
Avoid importing quote line items to renewal and cancellation quotes.
Limit the CSV file to 1,000 rows, ensuring the total number of lines created doesn’t exceed 1,000.
Import multiple files until you reach the quote line item limit per quote.
Verify that the imported line items add to the first group if your quote contains groups.
Use only comma-delimited CSV files that meet all readiness criteria. For more information, see CSV File Readiness.
IMPORTANT The error logs exclude ProductCode and RowNumber columns. If you import both root and child products of a bundle via CSV, the system adds them as separate products.
