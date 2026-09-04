---
article_id: ind.billing_write_off_invoices_impact.htm
title: Impact of Invoice Write-Offs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_write_off_invoices_impact.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_write_off_invoice_balance.htm
fetched_at: 2026-09-04
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
