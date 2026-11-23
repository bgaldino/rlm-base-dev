---
article_id: ind.billing_account_specific_invoice_template_configure.htm
title: Generate Individual Invoice PDF Documents
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_specific_invoice_template_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_document_generation_batch_and_single.htm
fetched_at: 2026-11-23
---

# Generate Individual Invoice PDF Documents

Generate a PDF document for an invoice directly from the invoice record. Provide billing profile-specific individual invoice documents without waiting for invoice batch runs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create and generate invoice PDF documents:	

Billing Admin permission set OR Billing Operations User permission set

AND

DocGen User permission set

AND

DocGen Designer permission set

NOTE

Before generating invoice PDF documents, review the default limits for document generation requests and the process for increasing the maximum number of content versions that are published per day.

NOTE

To access DocGen records, add yourself to the DocGen Document Template Library and have one of the required permissions.

From the App Launcher, find and select Invoices.
Open a draft or posted invoice for which you want to generate a document.
Click Generate Invoice Document.
Preview the invoice document in the Generate Invoice Document window. If necessary, download a local copy of the invoice document. Regenerate the invoice document as needed.

Billing selects the appropriate invoice template based on this resolution order:

If the invoice has a billing profile with an invoice document template, Billing uses that template.
If the invoice’s billing profile lacks an invoice document template, Billing uses the default template from the billing account’s billing profile.
If neither is available, Billing uses the default invoice document template defined for the Salesforce org.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_account_specific_invoice_template_configure.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
