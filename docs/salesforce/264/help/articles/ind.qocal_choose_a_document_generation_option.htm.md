---
article_id: ind.qocal_choose_a_document_generation_option.htm
title: Choose a Document Generation Option
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_choose_a_document_generation_option.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_document_generation_for_quotes.htm
fetched_at: 2026-11-23
---

# Choose a Document Generation Option

Use these guidelines to choose an option for generating quote documents.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Quote PDF Generation

Use the Create PDF action for standard quote documents. Legacy quote PDF generation serves most existing customers and Sales Cloud customers who don't use Revenue Cloud. It uses database records as its data source.

See Create a Quote PDF by Selecting a Template.

Document Builder

Use Document Builder for quick, built-in quote documents and a modern, drag-and-drop experience. Preview, generate, and email quote PDFs, or capture signatures on the web and in the Salesforce mobile app. Document Builder supports nonnested grouping and uses Sales Transaction Line Editor (STLE) data.

See Document Builder for Quotes.

Contract Lifecycle Management (CLM) Document Generation 2.0 and OmniStudio

To handle document generation for large-scale quotes, CLM Document Generation is the right option for you. It supports Microsoft Word integration, redlining, and change tracking. This option honors stored decimal currency values and supports groups with up to 15,000 lines. From a quote, select Generate Document, choose a template, and generate the PDF. Salesforce links the generated PDF to the quote. Nested groups up to 5 levels are supported.

See Set up CLM Document Generation for quotes.

Access to Document Generation Options

Revenue Cloud customers have access to quote PDF generation and Document Builder. Sales Cloud customers who don't use Revenue Cloud have access only to legacy quote PDF generation.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_choose_a_document_generation_option.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
