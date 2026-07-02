---
article_id: ind.billing_sequential_numbering_for_invoices_configure.htm
title: Configure Sequential Numbering for Invoices and Credit Memos
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_sequential_numbering_for_invoices_configure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Sequential Numbering for Invoices and Credit Memos

Use a sequence policy to configure automated sequential numbering for your invoices and credit memos. Generate unique, gapless numbers to create fully traceable records for financial audits.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Gapless Sequential Numbering
For businesses that handle large volumes of transactions, assigning unique, gapless sequential numbers to invoice and credit memo records is essential for legal compliance, auditing, and reconciliation. Manual numbering introduces operational complexity and increases the risk of errors or fraudulent activity. Billing addresses this challenge by automating the assignment of unique identifiers according to the defined sequence policies.
Configure Sequence Policies
Define the sequential number structure and the filters for choosing which invoice or credit memo records to number.
Manage Sequential Numbering by Using APIs
Use APIs to create and update sequence policies, assign sequence pattern values to records, and restore missing sequence values.
Sequential Invoice and Credit Memo Number Assignment
When you post an invoice or a credit memo record, the system evaluates all active sequence policies. If the target object matches the selection conditions of a unique sequence policy, the system assigns the next available sequential number based on that sequence policy to the target object record.
