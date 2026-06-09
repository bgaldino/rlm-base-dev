---
page_id: sforce_api_objects_generalldgracctprdsummary.htm
title: GeneralLdgrAcctPrdSummary
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_generalldgracctprdsummary.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# GeneralLdgrAcctPrdSummary

Represents a junction between a general ledger account and a legal
entity accounting period. Stores information about the total credit amount, total debit
amount, opening balance, and closing balance of a general ledger account for a specific
legal entity accounting period. This object is available in API version 65.0 and
later.

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
| ClosingBalanceAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The closing balance amount for a general ledger accounting period summary is calculated based on the general ledger account's type. For asset and expense type general ledger accounts, it’s the opening balance amount plus total debit amount minus total credit amount. For liability, equity, and revenue type general ledger accounts, it’s the opening balance amount plus total credit amount minus total debit amount. |
| GeneralLedgerAccountId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The general ledger account that’s related to the general ledger accounting period summary.  This field is a relationship field.  Relationship Name  GeneralLedgerAccount  Relationship Type  Master-detail  Refers To  GeneralLedgerAccount (the master object) |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed general ledger accounting period summary record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed general ledger accounting period summary record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| LegalEntityAccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The legal entity accounting period that’s related to the general ledger account.  This field is a relationship field.  Relationship Name  LegalEntityAccountingPeriod  Refers To  LegalEntyAccountingPeriod |
| OpeningBalanceAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  The opening balance is the same as the closing balance of the previous general ledger account period summary. |
| TotalCreditAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  The sum of the credit fields from all transaction journals of the general ledger account for a specific legal entity accounting period. |
| TotalDebitAmount | Type  currency  Properties  Create, Filter, Sort, Update  Description  The sum of the debit fields from all transaction journals of the general ledger account for a specific legal entity accounting period. |
