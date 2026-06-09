---
page_id: sforce_api_objects_generalledgerjrnlentryrule.htm
title: GeneralLedgerJrnlEntryRule
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_generalledgerjrnlentryrule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# GeneralLedgerJrnlEntryRule

Represents information about the transaction journal entry rule, based on
which transaction journals are created for the selected credit and debit general ledger
accounts, transaction amount field, and percentage. This object is available in API
version 65.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where possible, we changed noninclusive terms
to align with our company value of Equality. We maintained certain terms to avoid any
effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and the Accounts Receivables Admin permission set
to access this object.

## Fields

| Field | Details |
| --- | --- |
| CreditGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The general ledger account for a credit transaction.  This field is a relationship field.  Relationship Name  CreditGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| DebitGeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The general ledger account for a debit transaction.  This field is a relationship field.  Relationship Name  DebitGeneralLedgerAccount  Refers To  GeneralLedgerAccount |
| GeneralLedgerAcctAsgntRuleId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The general ledger account assignment rule that’s related to the general ledger journal entry rule.  This field is a relationship field.  Relationship Name  GeneralLedgerAcctAsgntRule  Relationship Type  Master-detail  Refers To  GeneralLedgerAcctAsgntRule (the master object) |
| Percentage | Type  percent  Properties  Create, Filter, Sort, Update  Description  The percentage of the amount field value that’s used to record the credit or debit amount in the transaction journals generated for the general ledger journal entry rule. |
| TransactionAmountField | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The amount field on the transaction type that’s used to record the credit or debit amount in the transaction journals generated for that specific transaction type. |
