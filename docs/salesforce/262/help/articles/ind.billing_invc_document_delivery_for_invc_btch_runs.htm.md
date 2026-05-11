---
article_id: ind.billing_invc_document_delivery_for_invc_btch_runs.htm
title: Send Invoice Emails in Bulk from Invoice Batch Runs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invc_document_delivery_for_invc_btch_runs.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Send Invoice Emails in Bulk from Invoice Batch Runs

After an invoice batch run completes and the invoice PDF documents are generated for the posted invoices of the invoice batch run, send invoice emails in bulk to your customers who opted for invoice delivery through email. Attach invoice PDF documents to the emails based on the selected preferences.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To send invoice emails from an Invoice Batch Runs record:	

Billing Admin permission set

OR

Billing Operations User permission set

Before you send invoice emails from Invoice Batch Run records, you and your Billing Admin must define the invoice email delivery configuration and preferences.

Open the completed invoice batch run that you want to send emails for.
Click Email Invoices.

When you click Email Invoices, the system first looks for email preferences in this sequence.

To track the status of the invoice email delivery, view the Last Email Dispatch Status field on the Invoice record. You can also track the emails in the activity timeline on the Invoice record's Details page.

When an email delivery fails because of these reasons, a Revenue Transaction Error Log record is created.

Exceeded the daily email limit.
Missing email address on the invoice's Bill to Contact record.
Presence of merge fields other than the invoice merge fields on the customized email template.
