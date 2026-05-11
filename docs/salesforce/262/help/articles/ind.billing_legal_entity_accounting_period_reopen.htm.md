---
article_id: ind.billing_legal_entity_accounting_period_reopen.htm
title: Reopen a Legal Entity Accounting Period
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_legal_entity_accounting_period_reopen.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Reopen a Legal Entity Accounting Period

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Reopen a Legal Entity Accounting Period

Reopen legal entity accounting periods to reconcile any previous journal entries. This exercise helps maintain accurate and compliant financial records during accounting period closure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


This feature is available for the Invoice and Credit Memo records, and their related records with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

This feature is available for the Payment, Refund, and Debit Memo records, and their related records with the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

The Delete Transaction Journals with Unrealized Foreign Exchange Gains or Losses data processing engines is available only with the Agentforce Revenue Management Billing license.

USER PERMISSIONS NEEDED
To reopen legal entity accounting periods:	

Accounts Receivables Admin permission set

AND

Data Pipelines Base User permission set

Before reopening a legal entity accounting period, make sure the status of the related Accounting Period record is Open.

NOTE Make sure that data pipelines is enabled. See Enable Data Piepelines.
Open the legal entity accounting period that you want to reopen.
Click Reopen Legal Entity Accounting Period and confirm that you want to reopen it.

When you click Reopen Legal Entity Accounting Period, the Delete Transaction Journals with Unrealized Foreign Exchange Gains or Losses data processing engine deletes all unrealized foreign exchange gain and loss transaction journals that were created during the legal entity accounting period closure. The Legal Entity Accounting Period record opens immediately and its status changes to Reopened.

SEE ALSO
Close Legal Entity Accounting Periods
