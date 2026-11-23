---
article_id: ind.billing_payment_reconciliation_troubleshooting.htm
title: Troubleshoot Common Payment Reconciliation Issues
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_troubleshooting.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-11-23
---

# Troubleshoot Common Payment Reconciliation Issues

Resolve common issues that can occur when you set up and run payment reconciliation, such as connector failures, missing data, a stale Process Content refresh, or empty Document AI output.

ISSUE	RESOLUTION
The connector fails to connect, often because its credentials expired.	Review the connector’s credentials and update them.
A data stream didn’t run or failed.	On the data stream, check Last Run Status and the Refresh History tab. To run the stream again, click Refresh Now.
Records are missing from Data 360.	In Data Explorer or Query Editor, verify that the data stream ingested your records. If records are missing, open the data stream and click Refresh Now to rerun the stream.
Process Content shows a stale date under Last Refresh.	Click Rebuild to rerun Process Content.
Document AI produces no output.	In Data Explorer or Query Editor, check the Document AI output. If no data is flowing, review the Document AI configuration and the selected file types, and confirm that the source files meet those requirements.
Data actions show a high failure rate.	Open Event Activity to review published and failed records. If the failure rate stays high, contact Salesforce Customer Support.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_troubleshooting.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
