---
article_id: ind.billing_preview_invoice.htm
title: Generate Invoice Previews and Preview PDF Documents
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_preview_invoice.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_previews.htm
fetched_at: 2026-09-04
---

# Generate Invoice Previews and Preview PDF Documents

Generate invoice previews without generating an actual invoice and then generate PDF documents for the invoice previews. Share the PDF documents with your customers to reduce billing disputes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Prerequisites

Before you generate invoice previews, make sure that your Billing admin completes the prerequisite steps.

Set up document generation for Billing.
To generate invoice previews for Quote records, create a procedure plan, and then use either the Preview Invoices button or the Invoice Preview API.
Limits

Before you generate invoice previews, consider these limits.

You can generate invoice previews for a maximum of 200 billing schedules of accounts, orders, or billing schedule groups.
Before generating PDF documents for invoice previews, review the default limits for document generation requests and the process for increasing the maximum number of content versions that are published per day.
Generate Invoice Previews for Orders and Accounts
Preview invoices for the next two billing periods of orders and accounts. Generate and download PDF documents of the invoice previews.
Generate Invoice Previews for Billing Schedule Groups
Preview invoices for the next two billing periods of billing schedule groups.
