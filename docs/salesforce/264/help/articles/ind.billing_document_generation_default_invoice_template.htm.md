---
article_id: ind.billing_document_generation_default_invoice_template.htm
title: Default Document Template to Generate Invoice PDF Documents
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_document_generation_default_invoice_template.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_document_generation_batch_and_single.htm
fetched_at: 2026-11-23
---

# Default Document Template to Generate Invoice PDF Documents

After your Billing admin turns on Document Generation for Billing, immediately generate bulk PDF documents for invoices by using the default document template that's preselected.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
NOTE For on-demand, account–specific invoice documents, see Assign an Invoice Document Template to a Billing Profile and Generate Individual Invoice PDF Documents.

The field values of the Default Invoice Template document template are derived from:

The Invoice Date, Invoice Number, Due Date, Description, Total Amount, Total Tax, Balance, and Net Credits Applied fields of the Invoice record.
The Billing Address and Shipping Address fields of the Account record.
The Product, Quantity, Unit Price, Tax Amount, and Line Amount fields of the Invoice Line record.
The start and end dates of the invoice line, which determine the billing period.
SEE ALSO
Turn On PDF Document Generation for Billing

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_document_generation_default_invoice_template.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
