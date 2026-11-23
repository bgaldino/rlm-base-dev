---
article_id: ind.billing_sequential_numbering_for_invoices_configure.htm
title: Sequential Numbering in Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_sequential_numbering_for_invoices_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-11-23
---

# Sequential Numbering in Revenue Cloud

Use a sequence policy to configure automated sequential numbering for your invoices and credit memos. Generate unique, gapless numbers to create fully traceable records for financial audits.

Gapless Sequential Numbering
For businesses that handle large volumes of transactions, assigning unique, gapless sequential numbers to invoice and credit memo records is essential for legal compliance, auditing, and reconciliation. Manual numbering introduces operational complexity and increases the risk of errors or fraudulent activity. Billing addresses this challenge by automating the assignment of unique identifiers according to the defined sequence policies.
Turn On Sequential Numbering Features
Apply unique, gapless sequence numbers to transaction records to ensure financial compliance and a clear audit trail. You can also mandate assigning an invoice number to every posted invoice.
Configure Sequence Policies
Define the sequential number structure and the filters for choosing which invoice or credit memo records to number.
Manage Sequential Numbering by Using APIs
Use APIs to create and update sequence policies, assign sequence pattern values to records, and restore missing sequence values.
Sequential Invoice and Credit Memo Number Assignment
When you post an invoice or a credit memo record, the system evaluates all active sequence policies. If the target object matches the selection conditions of a unique sequence policy, the system assigns the next available sequential number based on that sequence policy to the target object record.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_sequential_numbering_for_invoices_configure.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
