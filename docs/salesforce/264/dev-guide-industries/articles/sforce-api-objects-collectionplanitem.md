---
page_id: sforce-api-objects-collectionplanitem
title: CollectionPlanItem
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-collectionplanitem.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Collections and Recovery
parent_page: collections-standard-objects
legacy_page_id: sforce_api_objects_collectionplanitem.htm
fetched_at: 2026-11-25
---

# CollectionPlanItem

Represents an instance of a collection plan. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CollectionPlanId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The ID of the parent collection plan associated with the collection plan item record.

This field is a relationship field.

- 

**Relationship Name**: CollectionPlan

- 

**Relationship Type**: Master-detail

- 

**Refers To**: CollectionPlan (the master object)

### FinancialAccountStatementId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: Financial account statement associated with the collection plan item record.

This field is a relationship field.

- 

**Relationship Name**: FinancialAccountStatement

- 

**Refers To**: FinancialAccountStatement

### Invoice

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The invoice associated with the collection plan item record.

This field is a relationship field.

- 

**Relationship Name**: Invoice

- 

**Refers To**: Invoice

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and <parmname>LastReferenceDate</parmname> is not null, the user accessed this record or list view indirectly.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the collection plan item record.

### SourceSystemRecordIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort, Update

- **Description**: The unique identifier of the collection plan item in an external system.

### Status

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: Specifies the status of the collection plan item, such as new, pending, paid, and closed.

- 

**Possible values**:

  - `New`

  - Paid

  - `Pending`

  - `Closed`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[CollectionPlanItemChangeEvent](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-change-event.html)**

: 

Change events are available for the object.

**[CollectionPlanItemHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-collectionplanitem.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
