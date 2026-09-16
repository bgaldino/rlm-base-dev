---
article_id: ind.billing_invoice_aging_component.htm
title: Add Invoice Aging for Account to an Account or Order Page
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_aging_component.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_generation.htm
fetched_at: 2026-09-04
---

# Add Invoice Aging for Account to an Account or Order Page

Add the Invoice Aging for Account component to an Account or Order page in Lightning App Builder. Sales reps and accounts receivable teams then see overdue invoices, aging buckets, and average invoice age without opening individual invoice records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To add the Invoice Aging for Account component:	Customize Application
To view invoice aging summaries:	

Billing Admin permission set

OR

Billing Operations User permission set

The Invoice Aging for Account component shows an aging summary of account invoices so that sales reps and accounts receivable teams can prioritize collections. On an Order page, the component shows aging data for the associated account. See Invoice Aging Summaries on Accounts and Orders.

Open an Account or Order record.
From Setup, select Edit Page.
From the Lightning App Builder components palette, drag Invoice Aging for Account onto the page canvas.
Save your changes, then activate the page.
To change the bucket duration, select Customize Bucket Size from the actions menu on the Invoice Aging for Account component, enter a value in the Days per Bucket field, and then save your changes.
