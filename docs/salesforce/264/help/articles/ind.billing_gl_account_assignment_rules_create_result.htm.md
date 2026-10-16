---
article_id: ind.billing_gl_account_assignment_rules_create_result.htm
title: Record Creation for the General Ledger Account Assignment Rule
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_gl_account_assignment_rules_create_result.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_general_ledger_account_assignment_rules_create.htm
fetched_at: 2026-09-04
---

# Record Creation for the General Ledger Account Assignment Rule

When billing transactions are Posted, Canceled, Voided, or Processed and they match the defined filter criteria and journal entry rules, then dual transaction journals are created for the defined general ledger accounts for each general ledger journal entry rule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

The debit general ledger account is populated for the debit transaction journal entry, and the credit general ledger account is populated for the credit transaction journal entry. See Automatic Creation of Dual Transaction Journals.

If multiple general ledger journal entry rules apply to the same transaction type, a corresponding number of transaction journals are generated. For example, if two general ledger journal entry rules are defined for a single transaction type, four transaction journals are created.

The table specifies the records that are created based on the sections filled.

SECTIONS	RESULT
Details section	
One General Ledger Account Assignment Rule record is created immediately.
Dual transaction journals are created when billing transactions that meet the rule are created for an active general ledger account assignment rule.

Details and Filter Criteria sections	
One General Ledger Account Assignment Rule record is created.
One Billing Batch Filter Criteria record for each filter criterion is created.
Dual transaction journals are created when billing transactions that meet the rule are created for an active general ledger account assignment rule.

Details and General Ledger Journal Entry Rules sections	
One General Ledger Account Assignment Rule record is created immediately.
One General Ledger Journal Entry Rule record is created for each row.
Dual transaction journals are created when billing transactions that meet the rule are created for an active general ledger account assignment rule.

Details, Filter Criteria, and General Ledger Journal Entry Rules sections	
One General Ledger Account Assignment Rule record is created immediately.
One Billing Batch Filter Criteria record is created for each filter criterion.
One General Ledger Journal Entry Rule record is created for each row.
Dual transaction journals are created when billing transactions that meet the rule are created for an active general ledger account assignment rule.
NOTE If you clone a general ledger account assignment rule, the filter criteria and general ledger journal entry rule sections aren't cloned.
