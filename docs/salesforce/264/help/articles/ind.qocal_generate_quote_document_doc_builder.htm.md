---
article_id: ind.qocal_generate_quote_document_doc_builder.htm
title: Generate a Quote Document with Document Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_generate_quote_document_doc_builder.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_features.htm
fetched_at: 2026-11-23
---

# Generate a Quote Document with Document Builder

Preview, generate, and email quote PDFs from the quote page. Share details about completed work with your customers in real time.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To generate a quote PDF document:	Document Builder User permission set
NOTE

Quote documents show all root products. They show only child products for which the Quote Visibility field isn't selected, is set to Always, or is set to Quote Document Only. See Product Relationship Management in Revenue Management.

Go to a quote.
From , select Generate PDF Document.
Select Preview PDF to preview your quote document.
Review the details on the quote document, and then select Create PDF.
You receive a notification when the PDF is ready.
On the quote record, go to the Related tab and scroll to the Quote PDFs section.
To view the PDF, select a quote document name in the list view.
To email the PDF to your customer, click next to the quote document and select Email PDF.

The default quote template applies when a user generates a quote PDF unless the user selects an alternative template. To use a different default, create or update a quote template in Document Builder and assign it as the default during activation. Assigning a different default template replaces the previous default. Only one default quote template can be active in a Salesforce org at a time. For instructions, see Create a Quote Template with Document Builder.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_generate_quote_document_doc_builder.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
