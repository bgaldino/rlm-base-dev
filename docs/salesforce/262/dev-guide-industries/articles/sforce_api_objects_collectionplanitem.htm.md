---
page_id: sforce_api_objects_collectionplanitem.htm
title: CollectionPlanItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_collectionplanitem.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Collections and Recovery
parent_page: collections_standard_objects.htm
fetched_at: 2026-06-25
---

# CollectionPlanItem

Represents an instance of a collection plan. This object is available in
API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| CollectionPlanId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The ID of the parent collection plan associated with the collection plan item record.  This field is a relationship field.  Relationship Name  CollectionPlan  Relationship Type  Master-detail  Refers To  CollectionPlan (the master object) |
| FinancialAccountStatementId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Financial account statement associated with the collection plan item record.  This field is a relationship field.  Relationship Name  FinancialAccountStatement  Refers To  FinancialAccountStatement |
| Invoice | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The invoice associated with the collection plan item record.  This field is a relationship field.  Relationship Name  Invoice  Refers To  Invoice |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and <parmname>LastReferenceDate</parmname> is not null, the user accessed this record or list view indirectly. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the collection plan item record. |
| SourceSystemRecordIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The unique identifier of the collection plan item in an external system. |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the status of the collection plan item, such as new, pending, paid, and closed.  Possible values are:  - `New` - Paid - `Pending` - `Closed` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[CollectionPlanItemChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm "A ChangeEvent object is available for each object that supports Change Data Capture. You can subscribe to a stream of change events using Change Data Capture to receive data tied to record changes in Salesforce. Changes include record creation, updates to an existing record, deletion of a record, and undeletion of a record. A change event isn’t a Salesforce object—it doesn’t support CRUD operations or queries. It’s included in the object reference so you can discover which Salesforce objects support change events.")
:   Change events are available for the object.

[CollectionPlanItemHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
