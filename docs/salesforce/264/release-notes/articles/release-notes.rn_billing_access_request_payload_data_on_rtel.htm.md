---
article_id: release-notes.rn_billing_access_request_payload_data_on_rtel.htm
title: Recover Failed Transaction Journals Using Payload from Revenue Transaction Error Logs
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_access_request_payload_data_on_rtel.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_billing.htm
fetched_at: 2026-11-23
---

# Recover Failed Transaction Journals Using Payload from Revenue Transaction Error Logs

If transaction journal generation fails for a posted billing transaction, you can view the transaction journal payload on related Revenue Transaction Error Log records. Use the JSON payload with custom TransactionJournalReconciler and TransactionJournalBatchReconciler Apex classes to simplify the recovery of dual transaction journal records automatically.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Cloud, formerly Revenue Cloud, with the Revenue Cloud Billing license.

Who: Your users need the Accounts Receivables Admin permission set to view revenue transaction error log records.

How: To view the revenue transaction error logs, from the App Launcher, find and select Revenue Transaction Error Logs. Open a revenue transaction error log record with category Transaction Journal Generation and view the Request field.

To reconcile the failed transaction journals, specify the Revenue Transaction Error Log IDs for the failed transaction journals as input to the TransactionJournalReconciler and TransactionJournalBatchReconciler Apex classes and execute them.

SEE ALSO
Salesforce Help: Reconcile Failed Transaction Journals

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_billing_access_request_payload_data_on_rtel.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
