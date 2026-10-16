---
article_id: ind.sf_contracts_datatrueup_lineitems.htm
title: How to Keep Contract Line Items in Sync with Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_lineitems.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# How to Keep Contract Line Items in Sync with Data True-Up

Data True-Up syncs line item details between a generated document and a Sales Contract Line Item record and its related records. Context Service document templates support Data True-Up line-item tokens.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

When a template includes a line-item table, such as a product or service list per contract, map each line-item record to a row in the document by using repeating section tokens with the DT_ prefix.

After generating the document or modifying the line-item content in Salesforce or the document, use Data True-Up to fetch the current values or write changes back. Data True-Up keeps product or service fields such as quantity, total price, aligned between the document and the Salesforce record.

Make sure that the line-item repeating section and the field tokens use the correct API names. Data True-Up reconciles only the fields that it supports for sync. See Supported Data Type Fields for Data True-Up.

Format for Line-Item Tokens

The DT_ prefix identifies which line items participate in the Data True-Up reconciliation process.

{{#DT_LineItems}}
  {{DT_ProductName}}    {{DT_Quantity}}    {{DT_UnitPrice}}  {{DT_TotalPrice}}
{{/DT_LineItems}}

Define the start and end of the repeating line-item section by using the {{#DT_LineItems}} and {{/DT_LineItems}} tokens.
Use tokens with the DT_ prefix within a section, such as {{DT_Product Name}}. Match them to the API field names defined for the line-item object so they participate in Data True-Up reconciliation.
Replace DT_LineItems with your organization’s line-item object API name while preserving the DT_ prefix for Data True-Up compatibility.
Before you reconcile the referenced fields, confirm that Data True-Up supports them. See Tokens in Microsoft Word or Microsoft PowerPoint Documents.
Using Data True-Up and Standard Tokens Together

You can include standard tokens inside a Data True-Up line-item section. This approach helps reduce the number of Data True-Up tokens and stay within the supported limit.

{{#DT_LineItems}}
  {{DT_ProductName}}    {{Quantity}}
{{/DT_LineItems}}


In this example, only tokens with the DT_ prefix count toward the Data True-Up token limit. This pattern is useful when you don’t need reconciliation for every field.

{{DT_ProductName}} participates in Data True-Up reconciliation.
{{Quantity}} is a standard token and resolves as a normal replacement value.
