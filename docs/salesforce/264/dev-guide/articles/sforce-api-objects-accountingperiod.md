---
page_id: sforce-api-objects-accountingperiod
title: AccountingPeriod
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-accountingperiod.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_accountingperiod.htm
fetched_at: 2026-11-25
---

# AccountingPeriod

Represents information about a time period for which businesses prepare reports and analyze performance. Each billing transaction is associated with an accounting period. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need the Accounts Receivables Admin permission set to access this object.

## Fields

### EndDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The end date of an accounting period.

### FinancialYear

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The financial year in which an accounting period falls.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed an accounting period indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed an accounting period. If this value is null, it’s possible that the user only accessed the accounting period or a related list view (`LastReferencedDate`), but not viewed the accounting period itself.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The auto-generated name of an accounting period. The name is a combination of the accounting period’s start date, start month, end date, and end month.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Required. The user who owns an Accounting Period record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### StartDate

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The start date of an accounting period.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Required. The status of an accounting period.

Valid values are `Closed` or `Open`.

### TotalAssetsAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The sum of all the assets from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later.

### TotalEquitiesAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The sum of all the equities from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later.

### TotalExpensesAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The sum of all the expenses from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later.

### TotalLiabilitiesAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The sum of all the liabilities from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later.

### TotalRevenueAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The sum of all the revenue from legal entity accounting periods associated with the accounting period. This field is available in API version 65.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AccountingPeriodShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

**[AccountingPeriodFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[AccountingPeriodHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-accountingperiod.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
