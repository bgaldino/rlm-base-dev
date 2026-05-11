---
article_id: ind.billing_invoice_creation.htm
title: Create Standalone Invoices or Import External Invoices
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_creation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Create Standalone Invoices or Import External Invoices

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Create Standalone Invoices or Import External Invoices

Use the Invoice Ingestion API to create standalone invoices by providing the required details to import invoices from an external system. You can also use the API to generate invoices from debit memos.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

To create or import invoices by using the Invoice Ingestion API, provide invoice details from any standard or custom Salesforce object record, or an external system. If the ingested invoice lines have the Tax Processing Status value as either Pending or Estimated, the Invoice Estimated Tax Calculation API is used to calculate estimated taxes for these invoice lines.

The API creates Invoice, Invoice Line, Invoice Line Tax, and Invoice Address Group records based on the specified details.

If you specify an order ID as the referenceEntityId property value in the Invoice Ingestion API, the generated invoices appear on the All Invoices related list of the Order record.

To generate invoices from debit memos, specify the debit memo ID as the referenceEntityId property value in the request body of this API. Make sure that the debit memo is in Posted status and is ready for invoice generation. The invoice is generated in Draft status.
