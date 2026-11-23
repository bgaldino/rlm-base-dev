---
article_id: ind.billing_write_off_invoices_impact.htm
title: Impact of Invoice Write-Offs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_write_off_invoices_impact.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_write_off_invoice_balance.htm
fetched_at: 2026-11-23
---

# Impact of Invoice Write-Offs

Invoices are written off by creating and applying credit memos to settle invoices. These credit memos are applied to the invoice or invoice lines based on the credit application level on the Billing Settings page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

The write-off process triggers specific updates to relevant records and fields.

On the Invoice record, the Write Off Status, Write Off Charge Amount, and Write Off Tax Amount fields are updated.
On the Credit Memo record, the Credit Memo Reason Code field is updated.
On the Credit Memo record, if the Reason was provided, it is populated on the Description field.

After an invoice is successfully written-off, you can't apply or unapply any further credit memos or payments to that invoice.

You can also use Write-Off API to write off invoices.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_write_off_invoices_impact.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
