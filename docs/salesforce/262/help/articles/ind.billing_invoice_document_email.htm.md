---
article_id: ind.billing_invoice_document_email.htm
title: Send Invoice Emails from Invoice Records
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_document_email.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Send Invoice Emails from Invoice Records

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Send Invoice Emails from Invoice Records

After invoice PDF documents are generated, send them to your customers through an email.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To send invoice email from an Invoice record:	

Billing Admin permission set

OR

Billing Operations User permission set

Before you send invoice PDF documents from Invoice records, you and your Billing Admin must define the invoice email delivery configuration and preferences.

From the App Launcher, find and select Invoices.
Open the Invoice record that you want to send an email for.
Go to the Invoice Documents related list.
From the quick actions menu on the Invoice Document row that you want to send an email for, click Email Invoice.
When you click Email Invoice, the system doesn't consider email opt-out preference selected on the related Bill to Contact record.

When you click Email Invoice, the system first looks for email preferences in this sequence. An email, with the invoice PDF document attached, is then sent to the email address of the bill to contact of the invoice. The email body has the invoice ID, the balance amount, and the invoice due date.

If the invoice email is delivered, then a success message appears immediately on the record. If the invoice email delivery fails due to these reasons, an error message appears on the Invoice record.

Exceeded the daily email limit.
Missing email address on the invoice's Bill to Contact record.
Presence of merge fields other than the invoice merge fields on the customized email template.

You can also track the emails in the activity timeline on the Invoice record's Details page.
