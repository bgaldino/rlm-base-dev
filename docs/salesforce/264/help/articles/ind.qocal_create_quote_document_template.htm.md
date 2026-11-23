---
article_id: ind.qocal_create_quote_document_template.htm
title: Create a Quote Template with Document Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_quote_document_template.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_document_builder_for_quotes.htm
fetched_at: 2026-11-23
---

# Create a Quote Template with Document Builder

Design a template that defines how information appears in quote documents. Use the template to generate customized quotes for your customers. Start with the default quote template or a blank template, and add standard Document Builder components that contain relevant quote details.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To create a quote document template:	Document Builder User
From Setup, in the Quick Find box, enter Document Builder, and then select Document Builder.
Select New Template.
Enter a label for the template, select Quote, and then select Next.
Select the default quote template or a blank template as the starting point, and then select Done.
The default quote template contains account and contact details, quote line items, and acceptance details.
Design the layout by using Template Builder and the standard components.
Save the template, and then select Activate.
During activation, you can assign the template as the Salesforce org default. The default template applies when a user generates a quote PDF unless the user selects an alternative template.

Standard components populate quote document templates with data from your quote.

Company Details: Captures your customer's company details in the quote document.
Quote Line Items: Shows a table with quantity and price details for quote line items. The table organizes quote line items into a hierarchy. You can't customize the fields shown in the table.
Grid: Provides a structural layout for document content.
Image and Image Gallery: Insert visual elements into the template.
Page Numbers: Adds page numbers to the document.
Related Record Table: Shows data from records that are related to the quote.
Rich Text: Provides custom-formatted text blocks.
Signature: Captures a text-based or manually drawn signature on the web or in the Salesforce mobile app. This component is available for quotes only in FSL-enabled Salesforce orgs.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_quote_document_template.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
