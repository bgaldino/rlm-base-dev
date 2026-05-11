---
article_id: ind.billing_accounting_periods_close.htm
title: Close an Accounting Period
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_accounting_periods_close.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Close an Accounting Period

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Close an Accounting Period

Close an accounting period after its duration ends and after all journal entries are validated for financial reporting of that period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To close accounting periods:	Accounts Receivables Admin permission set

Before closing an accounting period, ensure there are no related open legal entity accounting periods. If there are related legal entity accounting periods that are open, an error message appears and the accounting period remains open.

Open the record of the accounting period that you want to close.
Click Close Accounting Period and confirm that you want to close it.

When there aren't any related open legal entity accounting periods, the accounting period's status is set to Closed.

When you close an accounting period, several key metrics are updated. The Total Asset Amount, Total Liabilities Amount, Total Equities Amount, Total Revenue Amount, and Total Expenses Amount fields are recalculated. These amounts are calculated by aggregating the corresponding field values from all associated legal entity accounting periods and are shown in corporate currency configured for your Salesforce org.
