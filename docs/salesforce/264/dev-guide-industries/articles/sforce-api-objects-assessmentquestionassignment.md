---
page_id: sforce-api-objects-assessmentquestionassignment
title: AssessmentQuestionAssignment
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentquestionassignment.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_assessmentquestionassignment.htm
fetched_at: 2026-11-25
---

# AssessmentQuestionAssignment

Represents a junction between an assessment question set and an assessment question. This object is available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssessmentQuestionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Required. The ID of the assessment question associated with this record.

This is a relationship field.

- 

**Relationship Name**: AssessmentQuestion

- 

**Relationship Type**: Lookup

- 

**Refers To**: AssessmentQuestion

### AssessmentQuestionSetId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Required. The ID of the assessment question set associated with this record.

This is a relationship field.

- 

**Relationship Name**: AssessmentQuestionSet

- 

**Relationship Type**: Lookup

- 

**Refers To**: AssessmentQuestionSet

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The name of the record.

### OwnerId

- 

**Type**: reference

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: The ID of the user who created the relationship record.

This is a polymorphic relationship field.

- 

**Relationship Name**: Owner

- 

**Relationship Type**: Lookup

- 

**Refers To**: Group, User

### SequenceNumber

- 

**Type**: int

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The sequence number for an assessment question in an assessment question set.

Available in API version 64.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AssessmentQuestionAssignmentChangeEvent](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-change-event.html)**

: 

Change events are available for the object.

**[AssessmentQuestionAssignmentFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[AssessmentQuestionAssignmentHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

**[AssessmentQuestionAssignmentShare](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-share.html)**

: 

Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentquestionassignment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
