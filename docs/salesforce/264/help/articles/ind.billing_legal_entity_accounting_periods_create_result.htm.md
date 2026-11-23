---
article_id: ind.billing_legal_entity_accounting_periods_create_result.htm
title: Considerations and Result
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_create_result.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_legal_entity_accounting_periods_create.htm
fetched_at: 2026-11-23
---

# Considerations and Result

Review the considerations for selecting a valid accounting period. Learn how legal entities assigned to accounting periods are automatically populated on the billing transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Considerations for Selecting Accounting Period

When you select an accounting period while assigning legal entities to accounting periods, keep these considerations in mind.

The accounting period can't overlap with any existing accounting period for the same legal entity.
There can't be any gaps between the selected period and the previous or next accounting periods for the same legal entity.
The total duration between the earliest and latest accounting period for a single legal entity can't be longer than 10 years.
Automatic Population of Legal Entity Accounting Period

The system automatically populates the legal entity accounting period when invoices, credit memos, and debit memos are posted, and when payments and refunds are processed. The system matches the legal entity and finds the open legal entity accounting period where the billing transaction's date falls within the accounting period's date range.

This table lists the date field on the billing transactions or related billing transactions that the system uses to calculate the legal entity accounting period.

BILLING TRANSACTIONS	DATE FIELD
Invoice	Invoice Date
Invoice Line	Invoice Date of the related Invoice record
Invoice Line Tax	Tax Effective Date
Credit Memo	Credit Date
Credit Memo Line	Credit Date of the related Credit Memo record
Credit Memo Line Tax	Tax Effective Date
Debit Memo Line	Posted Date of the related Debit Memo record
Debit Memo Line Tax	Tax Effective Date of the related Debit Memo Line record
Payment	Effective Date
Payment Line Invoice	Effective Date
Payment Line Invoice Line	Effective Date Time
Refund	Effective Date
Refund Line Payment	Effective Date
Credit Memo Invoice Application	Effective Date
Credit Memo Line Invoice Line	Effective Date Time
Credit Memo Refund	Effective Date Time
Credit Memo Line Refund	Effective Date Time

This table shows the system's behavior in these scenarios.

SCENARIO	BEHAVIOR
No legal entity is selected for the billing transaction.	The system uses the legal entity accounting period that's related to the default legal entity of your Salesforce org.
No open legal entity accounting period is available for the legal entity and date of the billing transaction.	The system leaves the Legal Entity Accounting Period field on the billing transaction blank.
If the matching legal entity accounting period is closed	The system finds the next open legal entity accounting period.

All the related billing transactions appear on the related list of the Legal Entity Accounting Period record.

When the system creates transaction journal records using the general ledger account assignment rules, it copies the legal entity accounting period from the billing transaction record.

Usage of Legal Entity Accounting Period

During the legal entity accounting period closure, the system validates the billing transaction record's legal entity and transaction date with the legal entity accounting period. See Legal Entity Accounting Period Closure Procedure.

Considerations for Editing Legal Entity Accounting Period

Review these considerations before editing the Legal Entity Accounting Period field on billing transactions.

The Legal Entity Accounting Period field can't be edited if the specified legal entity accounting period is closed.
The legal entity of the new legal entity accounting period must be same as the legal entity of the billing transaction.
When a legal entity accounting period is missing on the billing transaction, specify a legal entity accounting period that's in Open or Reopen status where the date of the billing transaction is within the accounting period's start and end dates. If that legal entity accounting period is closed, specify the next open legal entity accounting period.
When legal entity is edited on a billing transaction, update the billing transaction's Legal Entity Accounting Period field manually.
If the Legal Entity Accounting Period field is automatically updated when you edit the legal entity of a billing transaction, or if you edit the Legal Entity Accounting Period field on a billing transaction record for which transaction journals and general ledger accounting period summaries have been created, then:
Manually update the Legal Entity Accounting Period field on the transaction journals created for the general ledger accounting assignment rule.
Reopen and close Legal Entity Accounting Period record to update the foreign exchange unrealized gain and loss transaction journals and the general ledger accounting period summaries.
Manually update the existing foreign exchange realized gain and loss transaction journals that are created for the Payment Line Invoice, Payment Line Invoice Line, and Credit Memo Line Invoice Line records.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_create_result.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
