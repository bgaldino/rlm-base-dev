---
article_id: ind.billing_sequential_number_assignment_and_sequence_gap_reconciliation.htm
title: Sequential Invoice and Credit Memo Number Assignment
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_sequential_number_assignment_and_sequence_gap_reconciliation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Sequential Invoice and Credit Memo Number Assignment

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Sequential Invoice and Credit Memo Number Assignment

When you post an invoice or a credit memo record, the system evaluates all active sequence policies. If the target object matches the selection conditions of a unique sequence policy, the system assigns the next available sequential number based on that sequence policy to the target object record.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Invoice and Credit Memo Number Assignment

Invoice and credit memo numbers are assigned based on how you create or post invoices and credit memos, or ingest invoices. These scenarios show when and how the invoice and credit memo numbers are applied.

Setup: If you turn on Mandate Sequence Policy for Posted Invoices, every invoice record must have an invoice number before you post. If an invoice number isn't assigned, the invoice moves to Error or Posting In Progress status. A Revenue Transaction Error Logs (RTEL) is logged for the Invoice record with the sequencing error details.
Setup: If you turn on Mandate Sequence Policy for Posted Credit Memos, every credit memo record must have a credit memo number before you post. If a credit memo number isn't assigned, the credit memo moves to Error status. A Revenue Transaction Error Logs (RTEL) is logged for the Credit Memo record with the sequencing error details.
Generate Invoices: When you generate posted invoices by using the Generate Invoices option on Account or Order record, or via the Invoice generation API invoice numbers are automatically assigned to the posted invoices.
Generate Credit Memo: When you generate a credit memo by using the Standalone Credit Memo API, the Void Credit Memo API, the Post a Draft Memo API, the Create and Apply Credit Memo API, or the Negative Invoice Lines to Credit Conversion API, a credit memo number is automatically assigned if the credit memo is posted and matches a unique active sequence policy.
Invoice Run: When you schedule an invoice run by using the Billing Batch Scheduler, invoice numbers are automatically assigned to all posted invoices.
Draft to Posted: When you post an invoice or a credit memo, an invoice or credit memo number is automatically assigned to it.
Preview Invoices: Invoice previews don't create actual Invoice records, so no invoice number is assigned to them.
Void a Posted Invoice: If you void a posted invoice with an invoice number, the number remains assigned to the voided invoice and can’t be reassigned to another invoice. The credit memo created to void the invoice isn't automatically assigned a credit memo number. This is because the credit memo transitions from a pending status to a voided status without ever being posted. To assign a sequential number to this credit memo, use the Sequence Assignment API.
Void a Posted Credit Memo: If you void a posted credit memo with a credit memo number, the number remains assigned to the voided credit memo and can't be reassigned to another credit memo. The credit memo generated as a result of the void operation isn't assigned a credit memo number, because it isn't posted through the standard posting flow.
Invoice Ingestion: For an ingested draft invoice, an invoice number is assigned during the posting process, provided the invoice aligns with a unique active sequence policy. When an already posted invoice is ingested, the Mandate Sequence Policy for Posted Invoices setting determines whether the invoice is accepted. If you enable this setting, a preexisting invoice number must be supplied in the Invoice Ingestion API payload, as the system won't generate one. If you disable this setting, even an ingested posted invoice without an invoice number is accepted.
NOTE An invoice number isn't assigned if:
Multiple active sequence policies match the same invoice record.
No active sequence policies match the invoice.
Sequence Gap Reconciliation

When you enforce gapless sequence in the sequence policy, the system creates a Sequence Gap Reconciliation record if any gaps are introduced in the sequence. Sequence gap reconciliation applies only to gapless sequences, where unassigned gaps in the sequence are reassigned to matching target object records so the sequence remains continuous.

Every 24 hours, a gap reconciliation scheduled job looks for any gaps in the active gapless sequence policies and stores any missing sequence values in the Sequence Gap Reconciliation record. If required, you can also trigger the Assign Sequences API manually to run the sequence gap reconciliation function.

Here are a few scenarios which could result in gaps:

Any error occurs during sequential number assignment.
An invoice with an invoice number associated with a sequence policy is deleted. Similarly, a credit memo with a credit memo number associated with a sequence policy is deleted.
NOTE If the invoice or the credit memo with the invoice or credit memo number is deleted, the corresponding record is in Blocked status, so that it isn't reassigned. The record is in Unassigned status if sequence number assignment fails for an invoice or a credit memo.

To see the details about these gaps, from the App Launcher, find and select Sequence Gap Reconciliation.
