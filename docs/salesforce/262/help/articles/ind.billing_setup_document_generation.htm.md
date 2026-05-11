---
article_id: ind.billing_setup_document_generation.htm
title: Turn On Invoice PDF Document Generation
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_document_generation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-05-11
---

# Turn On Invoice PDF Document Generation

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Turn On Invoice PDF Document Generation

Enable generation of PDF documents for invoices and invoice previews.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To enable Billing features:	Billing Admin permission set
To create, view, or edit document templates:	DocGen Designer permission set

Before turning on Document Generation for Billing, turn on Design Document Templates and server-side document generation.

From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
Turn on Document Generation.

The Default Invoice Template and Default Invoice Preview Template document templates are preselected as the default templates for generating invoice PDF documents and invoice preview PDF documents. You can clone and customize these default document templates or the Sample Invoice Template document template, or create your own document templates, and then select the custom document templates as the default ones.

IMPORTANT

When your Salesforce org upgrades to Summer ’25 or a later release, to view the preselected Default Invoice Preview Template document template, your Billing admin must complete the one-time task of turning off Document Generation for Billing and turning it on again.

After you turn on document generation, you or your Billing Operations users can generate invoice PDF documents.

SEE ALSO
Default Document Template to Generate Invoice PDF Documents
Default Document Template to Generate Invoice Preview PDF Documents
Clone a Document Template
Create a Microsoft Word or Microsoft PowerPoint Template for Omnistudio Document Generation
