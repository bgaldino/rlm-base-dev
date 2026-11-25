---
page_id: sforce-api-objects-caseproceedingparticipant
title: CaseProceedingParticipant
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-caseproceedingparticipant.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Collections and Recovery
parent_page: collections-standard-objects
legacy_page_id: sforce_api_objects_caseproceedingparticipant.htm
fetched_at: 2026-11-25
---

# CaseProceedingParticipant

Represents a junction between the case proceeding and a participant, such as an account or a contact. This object stores the details of a participant who is involved in a case proceeding. This object is available in API version 64.0 and later.

**Note:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

When Compliant Data Sharing is enabled for the Case Proceeding object, a case proceeding participant represents information about a user or group of participants who have access to a case proceeding.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CaseProceedingId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The case proceeding associated with the case proceeding participant record.

This field is a relationship field.

- 

**Relationship Name**: CaseProceeding

- 

**Relationship Type**: Master-detail

- 

**Refers To**: CaseProceeding (the master object)

### Comments

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The comments about why the participant has access to the case proceeding.

### IsActive

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Specifies whether the participant’s association with the case proceeding is active (`true`) or not (`false`).

- **Default value**: `false`

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed a record related to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed this record or list view. If this value is null, and `LastReferencedDate` is not null, the user accessed this record or list view indirectly.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the case proceeding participant record.

### ParticipantId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The participant associated with the case proceeding record.

This field is a polymorphic relationship field.

- 

**Relationship Name**: Participant

- 

**Relationship Type**: Lookup

- 

**Refers To**: Account, Contact, Group, User

### ParticipantRoleId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The participant role associated with the case proceeding participant record.

This field is a relationship field.

- 

**Relationship Name**: ParticipantRole

- 

**Refers To**: ParticipantRole

### ParticipationType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The actual type of presence of the participant during the case proceeding.

- 

**Possible values**:

  - `Absent`

  - `Present In Person`

  - `Virtual`

### Role

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The role of the participant associated with the case proceeding record.

- 

**Possible values**:

  - `Attorney`

  - `Defendant`

  - `Judge`

  - `Perpetrator`

  - `Plaintiff`

  - `Victim`

  - `Witness`

### Status

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: Specifies the status of the participant in the case proceeding.

- 

**Possible values**:

  - `Active`

  - `Inactive`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[CaseProceedingParticipantFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[CaseProceedingParticipantHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-caseproceedingparticipant.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
