---
article_id: ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines.htm
title: Automatic Conversion of Negative Invoice Lines into Credit Memo Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Automatic Conversion of Negative Invoice Lines into Credit Memo Lines

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Automatic Conversion of Negative Invoice Lines into Credit Memo Lines

In certain billing scenarios, an invoice line can be generated with a negative charge amount. This typically occurs when you amend an order to decrease the quantity of a product and generate an invoice for the amended product, or generate an invoice for an order product that has a negative price. Automate conversion of large volumes of such negative invoice lines to credit memo lines, and the application of these credit memo lines to invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Process Overview

When your Billing admin enables the Convert Negative Invoice Lines to Credit Memo Lines feature, the system automatically converts negative invoice lines into credit memo lines. The converted credit memos are then applied to the posted invoice which had the negative lines.

Conditions for Conversion

Negative invoice lines are automatically converted to credit memo lines when these conditions are met:

The negative invoice lines are for posted invoices.
The negative invoice lines haven't been previously converted to credit memos.
Converted Amount Details

The converted amount for each invoice line is stored in its Converted Negative Amount field, and the total converted amount for the invoice is stored in its Total Converted Negative Amount field.

Application of Converted Credit Memos to Invoices

After negative lines of an invoice are converted, if a balance remains on that invoice, the converted credit memos are applied to it. The credit amount applied will be the smaller of the invoice's balance or the credit memo's balance.

If the credit memo's balance is larger than the invoice's balance, the credit memo will fully settle the invoice. Any remaining balance on the credit memo must then be manually applied to other invoices.

Business Use Case: Converting Negative Invoice Lines when a Product's Quantity is Reduced

You amend a customer's order to reduce the quantity of their SaaS subscriptions from 4 to 3. This reduction creates an amended order product with a price of -$100.

The next time you generate an invoice for this order, an invoice line is created with an amount of -$100.
If Convert Negative Invoice Lines to Credit Memo Lines is turned on, this negative invoice line is automatically converted into a credit memo line within a new, posted credit memo.
The new credit memo line has a line amount of $100.
This credit memo's balance of $100 is applied to the original invoice, reducing its balance from $400 to $300.
