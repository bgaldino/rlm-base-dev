---
article_id: ind.billing_legal_entity_accounting_periods_create_result.htm
title: Considerations and Result
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_periods_create_result.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_legal_entity_accounting_periods_create.htm
fetched_at: 2026-09-04
---

# Considerations and Result

Review the considerations for selecting a valid accounting period. Learn how legal entities assigned to accounting periods are automatically populated on the billing transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Considerations for Selecting Accounting Period

When you select an accounting period while assigning legal entities to accounting periods, keep these considerations in mind:

The accounting period can't overlap with any existing accounting period for the same legal entity.
There can't be any gaps between the selected period, and the previous or next accounting periods for the same legal entity.
The total duration between the earliest and latest accounting period for a single legal entity can't be longer than 10 years.
How Are Legal Entity Accounting Periods Auto-Populated?

After legal entity accounting periods are created, they are auto-populated on billing transactions as mentioned in this table:

SCENARIO	BEHAVIOR
No legal entity is selected for the billing transaction.	The system uses the legal entity accounting period that's related to the default legal entity of your Salesforce org.
No open legal entity accounting period is available for the legal entity and date of the billing transaction.	The billing transaction record is created without any legal entity accounting period.

For transaction journal records created for the general ledger account assignment rules, the legal entity accounting period is derived from the transaction type record.

All the related billing transactions appear on the related list of the Legal Entity Accounting Period record.

Usage of Legal Entity Accounting Period

During the legal entity accounting period closure, the system validates the billing transaction record's legal entity and transaction date with the legal entity accounting period. See Legal Entity Accounting Period Closure Procedure.

Considerations for Editing Legal Entity Accounting Period

Review these considerations before editing the Legal Entity Accounting Period field on billing transactions.

The legal entity accounting period field can't be edited if the specified legal entity accounting period is closed.
The legal entity of the new legal entity accounting period must be same as the legal entity of the billing transaction.
When a legal entity accounting period is missing on the billing transaction, specify a legal entity accounting period that's in Open or Reopen status where the date of the billing transaction is within the accounting period's start and end dates. If that legal entity accounting period is closed, specify the next open legal entity accounting period.
When legal entity is edited on a billing transaction, update the billing transaction's Legal Entity Accounting Period field manually.
If the Legal Entity Accounting Period field is automatically updated when you edit the legal entity of a billing transaction, or if you edit the Legal Entity Accounting Period field on a billing transaction record for which transaction journals and general ledger accounting period summaries have been created, then:
Manually update the Legal Entity Accounting Period field on the transaction journals created for the general ledger accounting assignment rule.
Reopen and close Legal Entity Accounting Period record to update the foreign exchange unrealized gain and loss transaction journals and the general ledger accounting period summaries.
Manually update the existing foreign exchange realized gain and loss transaction journals that are created for the Payment Line Invoice, Payment Line Invoice Line, and Credit Memo Line Invoice Line records.
