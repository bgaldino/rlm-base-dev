---
article_id: ind.billing_invoice_previews.htm
title: Preview Invoices
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_previews.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Preview Invoices

Preview invoices for the next two billing periods of orders, quotes, accounts, or billing schedule groups to verify order products, discounts, amendments, cancellations, and tax calculations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Default Document Template to Generate Invoice Preview PDF Documents
After your Billing admin turns on Document Generation for Billing, immediately generate PDF documents for invoice previews by using the default document template that's preselected.
Generate Invoice Previews and Preview PDF Documents
Generate invoice previews without generating an actual invoice and then generate PDF documents for the invoice previews. Share the PDF documents with your customers to reduce billing disputes.
Generate Invoice Previews with the Invoice Preview API
To generate preview invoices by using the Invoice Preview API, create and activate a custom procedure plan definition for the object that you want to preview invoices for. The Invoice Preview API uses the procedure plan to generate invoice previews. A custom procedure plan creation isn't required to use the Invoice Preview API for orders, accounts, and billing schedule groups.
Example: Preview Invoices for an Order
This example shows how Billing generates preview invoices when an order includes products with different billing frequencies.
