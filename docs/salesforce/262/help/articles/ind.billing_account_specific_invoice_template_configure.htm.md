---
article_id: ind.billing_account_specific_invoice_template_configure.htm
title: Generate Invoice PDF Documents Specific to Billing Profiles
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_account_specific_invoice_template_configure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate Invoice PDF Documents Specific to Billing Profiles

Generate a PDF document for an invoice directly from the invoice record. Provide billing profile specific individual invoice documents without waiting for invoice batch runs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create and generate invoice PDF documents:	

Billing Admin permission set OR Billing Operations User permission set

AND

DocGen User permission set

AND

DocGen Designer permission set

AND

DocGen Runtime Community User

NOTE

Before generating invoice PDF documents, review the default limits for document generation requests and the process for increasing the maximum number of content versions that are published per day.

NOTE If you can’t access DocGen records, add yourself to the DocGen Document Template Library and make sure you have one of the required permissions.
From the App Launcher, find and select Invoices.
Open a draft or posted invoice for which you want to generate a document.
Click Generate Invoice Document.
You can preview the invoice document in the Generate Invoice Document window. If necessary, download a local copy of the invoice document. You can also regenerate the invoice document as needed.

Billing selects the appropriate invoice template based on these resolution order:

If the invoice has a billing profile with an invoice document template, Billing uses that template.
If the invoice’s billing profile has no invoice document template, Billing uses the default template from the billing account’s billing profile.
If neither is available, Billing uses the default invoice document template defined for the Salesforce org.
