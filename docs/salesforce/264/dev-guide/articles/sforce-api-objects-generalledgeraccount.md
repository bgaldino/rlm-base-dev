---
page_id: sforce-api-objects-generalledgeraccount
title: GeneralLedgerAccount
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-generalledgeraccount.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_generalledgeraccount.htm
fetched_at: 2026-11-25
---

# GeneralLedgerAccount

Represents information about the accounting codes, types, and names that are used to store and organize financial transactions. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

You need Revenue Cloud Billing license and the Accounts Receivables Admin permission set to access this object.

## Fields

### AccountingCode

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The code that’s used to organize information about the general ledger account.

### AccountingName

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The user-specified name for the general ledger account.

### AccountingType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The accounting type for the general ledger account.

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Additional details about the general ledger account.

### FinancialStatement

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The financial statement that’s created by using the information from the general ledger account.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferenceDate` is not null, the user accessed this record or list view indirectly.

### LegalEntityId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The legal entity that’s related to the general ledger account.

This field is a relationship field.

- **Relationship Name**: LegalEntity

- **Refers To**: LegalEntity

### Name

- **Type**: string

- **Properties**: Filter, Group, idLookup, Sort

- **Description**: An auto-generated name identifying the general ledger account, which is a combination of the accounting code and the account name.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner of this object or ID of the creator of this object.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### Type

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Specifies the accounting type for the general ledger account. This field is available in API version 65.0 and later.

Valid values are:

- `Asset`

- `Liability`

- `Equity`

- `Revenue`

- `Expense`

- `Others`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-generalledgeraccount.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
