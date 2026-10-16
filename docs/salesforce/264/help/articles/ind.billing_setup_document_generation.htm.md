---
article_id: ind.billing_setup_document_generation.htm
title: Turn On Invoice PDF Document Generation and Account Statement
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_document_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-09-04
---

# Turn On Invoice PDF Document Generation and Account Statement

Before Billing can create PDF documents for invoices, invoice previews, and account statements, enable server-side and batch document generation, then turn on Document Generation in Billing Settings. Batch document generation is required to generate invoice PDF documents from an invoice batch run.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To enable Billing features:	Billing Admin permission set
To enable Document Generation Settings and to create, view, or edit document templates:	DocGen Designer permission set

Before turning on Document Generation for Billing, turn on Design Document Templates.

Document Generation creates PDF documents for invoices, invoice previews, and account statements. Complete this task in Document Generation Settings and then in Billing Settings.

From Setup, in the Quick Find box, enter document generation, and then select Document Generation Settings.
Click the arrow corresponding to the document generation setting, and then select Edit.
If your org doesn’t have a Document Generation Setting record, create one. See Enable Server-Side Document Generation Setting for the Omnistudio Package. Then edit the record and continue with these steps to turn on Enable Batch Document Generation.
Turn on Enable Server-Side Document Generation and Enable Batch Document Generation.
Enable Batch Document Generation is required to generate invoice PDF documents from an invoice batch run.
Click Continue.
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
Turn on Document Generation.

The Default Invoice Template and Default Invoice Preview Template document templates are preselected as the default templates for generating invoice PDF documents and invoice preview PDF documents.

After you turn on document generation, you or your Billing Operations users can generate invoice PDF documents and account statements.

You can clone and customize the Default Invoice Template, Default Invoice Preview Template, or Sample Invoice Template document templates, or create your own document templates, and then select the custom document templates as the default ones.

IMPORTANT

When your Salesforce org upgrades to Summer ’25 or a later release, to view the preselected Default Invoice Preview Template document template, your Billing admin must complete the one-time task of turning off Document Generation for Billing and turning it on again.

SEE ALSO
Enable Design Document Templates in Salesforce Setting
Enable Server-Side Document Generation Setting for the Omnistudio Package
Enable Document Generation Batch Process
Generate a Batch of Invoice PDF Documents
Default Document Template to Generate Invoice PDF Documents
Default Document Template to Generate Invoice Preview PDF Documents
Clone a Document Template
Create a Microsoft Word or Microsoft PowerPoint Template for Omnistudio Document Generation
