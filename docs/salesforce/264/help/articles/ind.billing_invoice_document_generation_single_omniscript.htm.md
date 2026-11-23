---
article_id: ind.billing_invoice_document_generation_single_omniscript.htm
title: Generate a Single Invoice PDF Document with Omniscript
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_document_generation_single_omniscript.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_document_generation_single.htm
fetched_at: 2026-11-23
---

# Generate a Single Invoice PDF Document with Omniscript

Generate a PDF document for an invoice by using Omniscript.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To configure Omniscript on the Invoice record page:	Customize Application
To use Omniscript:	Omnistudio User permission set
To generate a PDF document from the Invoice record page:	

Billing Admin permission set

OR

Billing Operations User permission set


To generate invoice PDF documents:	DocGen User permission set

To generate a PDF document for an invoice, configure Omniscript on your Invoice record page, and then generate a PDF document from the Invoice record page.

Configure Omniscript on Invoice Record Page
Open the invoice record that you want to generate a PDF document for.
From Setup, go to Edit Page.
In the components search bar, enter Omniscript.
Drag the Omniscript component onto one of the tabs of the Invoice record page layout.
You can also create a tab to configure Omniscript on the Invoice record.
Generate a PDF Document from Invoice Record Page
Open the invoice record that you want to generate a PDF document for.
Go to the tab where you added the Omniscript component.
Enter the invoice record ID.
Select a template type, and then click Next.
Select a template, and then click Next.
Select Server Side Document Generation as the document generation type.
Select Microsoft Word or Microsoft PowerPoint & PDF as the output file format.
Select the font source.
Enter a document title, and then click Next.
An invoice document is generated.
Download the generated invoice document.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_document_generation_single_omniscript.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
