---
page_id: sforce_api_objects_legalentyaccountingperiod.htm
title: LegalEntyAccountingPeriod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_legalentyaccountingperiod.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# LegalEntyAccountingPeriod

Represents a junction between a legal entity and an accounting
period. This object is available in API version 62.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Special Access Rules

You need the Accounts Receivables Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| AccountingPeriodId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the accounting period record that's related to a legal entity accounting period.  This field is a relationship field.  Relationship Name  AccountingPeriod  Refers To  AccountingPeriod |
| ClosureStage | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the closure stage of the legal entity accounting period. This field is available in API version 65.0 and later.  Valid values are:  - `CloseLegalEntityAccountingPeriod` - `Completed` - `Open` - `CreateGeneralLedgerAccountingPeriodSummaries` - `CreateUnrealizedGainOrLossTransactionJournals` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a legal entity accounting period record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a legal entity accounting period record. If this value is null, it’s possible that the user only accessed the legal entity accounting period record or a related list view (LastReferencedDate), but not viewed the legal entity accounting period record itself. |
| LegalEntityId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the legal entity record that's related to a legal entity accounting period.  This field is a relationship field.  Relationship Name  LegalEntity  Refers To  LegalEntity |
| Name | Type  string  Properties  Filter, Group, idLookup, Sort  Description  Required. The auto-generated name of a legal entity accounting period. The name is a combination of the names of the legal entity and the accounting period. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the user who owns a legal entity accounting period record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort  Description  Required. The status of a legal entity accounting period record.  Valid values are:  - `Closed` - `Error` - `Open` - `PendingClosure` - `PendingReopen` - `Reopened` |
| TotalAssetsAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total assets for a legal entity accounting period is a roll up summary of the closing balances of the general ledger accounting period summary records that are related to an asset type general ledger account. This field is available in API version 65.0 and later. |
| TotalEquitiesAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total equities for a legal entity accounting period is a roll up summary of the closing balances of the general ledger accounting period summary records that are related to an equity type general ledger account. This field is available in API version 65.0 and later. |
| TotalExpensesAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total expenses for a legal entity accounting period is a roll up summary of the closing balances of the general ledger accounting period summary records that are related to an expense type general ledger account. This field is available in API version 65.0 and later. |
| TotalLiabilitiesAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total liabilities for a legal entity accounting period is a roll up summary of the closing balances of the general ledger accounting period summary records that are related to a liability type general ledger account. This field is available in API version 65.0 and later. |
| TotalRevenueAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total revenue for a legal entity accounting period is a roll up summary of the closing balances of the general ledger accounting period summary records that are related to a revenue type general ledger account. This field is available in API version 65.0 and later. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[LegalEntyAccountingPeriodShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
