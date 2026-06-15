---
article_id: ind.billing_invoices_void.htm
title: Void Invoices
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoices_void.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Void Invoices

Simplify invoice corrections by voiding posted invoices directly from the Invoice record.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create credit memos:	

Billing Admin permission set

OR

Billing Operations User permission set

From the App Launcher, find and select Invoices.
Open the posted invoice that you want to void.
Click Void Invoice.

Billing creates a credit memo that mirrors the original invoice. The invoice status changes to Void in Progress while the process completes. The related billing schedules are updated automatically to reflect the voided invoice.

If an invoice remains in Void in Progress status for a long time, you can recover it by using the Billing Schedule Recovery API. Recovery restores the invoice to the Posted status, allowing you to take corrective action.

NOTE You can void invoices in reverse chronological order, starting with the most recent invoice. You can't void invoices that credit memos, payments, or write-offs have partially or fully settled.
