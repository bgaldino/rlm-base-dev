---
article_id: ind.billing_invoice_pdf_document_delivery_through_email.htm
title: Send Invoices Through Email
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_pdf_document_delivery_through_email.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-11-23
---

# Send Invoices Through Email

Ensure regional compliance by sending invoices through emails to your customers after the invoices are posted and before the payment due date. Customize your preferences at various levels in your Salesforce org to choose the way emails are delivered to your customers.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Sequence of Invoice Email Preferences

When you send invoice emails, the system looks for email preferences in this sequence:

Billing Account record
Legal Entity record
Billing Settings page

If emails are sent based on the preferences on the Billing Settings page and the invoice PDF documents are already generated, the PDF documents are attached to the emails by default.

Turn On Email Delivery of Invoices
Send emails with invoice information along with invoice PDF documents to your customers.
Define Invoice Email Delivery Configuration and Preferences
Before you send invoices to your customers through email, your Billing admin and Billing Operations user must complete certain tasks.
Send Invoice Emails from Invoice Records
After invoice PDF documents are generated, send them to your customers through an email.
Send Invoice Emails in Bulk from Invoice Batch Runs
After an invoice batch run completes and the invoice PDF documents are generated for the posted invoices of the invoice batch run, send invoice emails in bulk to your customers who opted for invoice delivery through email. Attach invoice PDF documents to the emails based on the selected preferences.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_pdf_document_delivery_through_email.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
