---
article_id: ind.billing_document_generation_default_invoice_template.htm
title: Default Document Template to Generate Invoice PDF Documents
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_document_generation_default_invoice_template.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Default Document Template to Generate Invoice PDF Documents

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Default Document Template to Generate Invoice PDF Documents

After your Billing admin turns on Document Generation for Billing, immediately generate bulk PDF documents for invoices by using the default document template that's preselected.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
NOTE For on-demand, account–specific invoice documents, see Assign an Invoice Document Template to a Billing Profile and Generate a Single Invoice PDF Document.

The field values of the Default Invoice Template document template are derived from:

The Invoice Date, Invoice Number, Due Date, Description, Total Amount, Total Tax, Balance, and Net Credits Applied fields of the Invoice record.
The Billing Address and Shipping Address fields of the Account record.
The Product, Quantity, Unit Price, Tax Amount, and Line Amount fields of the Invoice Line record.
The start and end dates of the invoice line, which determine the billing period.
SEE ALSO
Turn On Invoice PDF Document Generation
