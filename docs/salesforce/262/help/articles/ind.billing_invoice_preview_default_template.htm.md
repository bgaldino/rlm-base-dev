---
article_id: ind.billing_invoice_preview_default_template.htm
title: Default Document Template to Generate Invoice Preview PDF Documents
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_default_template.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Default Document Template to Generate Invoice Preview PDF Documents

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Default Document Template to Generate Invoice Preview PDF Documents

After your Billing admin turns on Document Generation for Billing, immediately generate PDF documents for invoice previews by using the default document template that's preselected.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
NOTE When creating a custom document template, use only the data tokens from the default invoice preview template to prevent missing data.

The field values of the Default Invoice Preview Template document template are derived from:

The Invoice Date, Bill To Contact, Due Date, Total Amount, Total Tax, and Total with Tax fields of the Invoice object.
The Billing Address and Shipping Address fields of the Account object.
The Product, Quantity field, Unit Price, Tax Amount, and Line Amount fields of the Invoice Line object.
The start and end dates of the invoice line, which determine the billing period.
SEE ALSO
Turn On Invoice PDF Document Generation
