---
page_id: sforce_api_objects_caseproceedingparticipant.htm
title: CaseProceedingParticipant
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_caseproceedingparticipant.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Collections and Recovery
parent_page: collections_standard_objects.htm
fetched_at: 2026-06-25
---

# CaseProceedingParticipant

Represents a junction between the case proceeding and a participant, such as
an account or a contact. This object stores the details of a participant who is involved in
a case proceeding. This object is available in API version
64.0
and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

When Compliant Data Sharing is enabled for the Case Proceeding object, a case proceeding
participant represents information about a user or group of participants who have access
to a case proceeding.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| CaseProceedingId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The case proceeding associated with the case proceeding participant record.  This field is a relationship field.  Relationship Name  CaseProceeding  Relationship Type  Master-detail  Refers To  CaseProceeding (the master object) |
| Comments | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The comments about why the participant has access to the case proceeding. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Specifies whether the participant's association with the case proceeding is active (`true`) or not (`false`).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferencedDate is not null, the user accessed this record or list view indirectly. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the case proceeding participant record. |
| ParticipantId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The participant associated with the case proceeding record.  This field is a polymorphic relationship field.  Relationship Name  Participant  Relationship Type  Lookup  Refers To  Account, Contact, Group, User |
| ParticipantRoleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The participant role associated with the case proceeding participant record.  This field is a relationship field.  Relationship Name  ParticipantRole  Refers To  ParticipantRole |
| ParticipationType | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The actual type of presence of the participant during the case proceeding.  Possible values are:  - `Absent` - `Present In Person` - `Virtual` |
| Role | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The role of the participant associated with the case proceeding record.  Possible values are:  - `Attorney` - `Defendant` - `Judge` - `Perpetrator` - `Plaintiff` - `Victim` - `Witness` |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Specifies the status of the participant in the case proceeding.  Possible values are:  - `Active` - `Inactive` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

[CaseProceedingParticipantFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CaseProceedingParticipantHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.
