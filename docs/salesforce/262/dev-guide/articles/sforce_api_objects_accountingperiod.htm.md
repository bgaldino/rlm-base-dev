---
page_id: sforce_api_objects_accountingperiod.htm
title: AccountingPeriod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_accountingperiod.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# AccountingPeriod

Represents information about a time period for which businesses
prepare reports and analyze performance. Each billing transaction is associated with an
accounting period. This object is available in API version 62.0 and later.

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
| EndDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  Required. The end date of an accounting period. |
| FinancialYear | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The financial year in which an accounting period falls. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed an accounting period indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed an accounting period. If this value is null, it’s possible that the user only accessed the accounting period or a related list view (LastReferencedDate), but not viewed the accounting period itself. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The auto-generated name of an accounting period. The name is a combination of the accounting period's start date, start month, end date, and end month. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The user who owns an Accounting Period record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| StartDate | Type  date  Properties  Create, Filter, Group, Sort, Update  Description  Required. The start date of an accounting period. |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of an accounting period.  Valid values are:  - `Closed` - `Open` |
| TotalAssetsAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The sum of all the assets from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later. |
| TotalEquitiesAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The sum of all the equities from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later. |
| TotalExpensesAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The sum of all the expenses from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later. |
| TotalLiabilitiesAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The sum of all the liabilities from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later. |
| TotalRevenueAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The sum of all the revenue from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later. |

## Associated Objects

This object has the following associated objects.
If the API version isn’t specified, they’re available in the same API versions as this
object. Otherwise, they’re available in the specified API version and later.

[AccountingPeriodShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.

[AccountingPeriodFeed](./sforce_api_associated_objects_feed.htm.md "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[AccountingPeriodHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
