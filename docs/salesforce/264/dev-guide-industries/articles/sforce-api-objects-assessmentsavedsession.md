---
page_id: sforce-api-objects-assessmentsavedsession
title: AssessmentSavedSession
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentsavedsession.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_assessmentsavedsession.htm
fetched_at: 2026-11-25
---

# AssessmentSavedSession

Represents a session of an assessment that’s saved to resume for later. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssessmentId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The assessment record for which the session is saved.

This field is a relationship field.

- 

**Relationship Name**: Assessment

- 

**Relationship Type**: Master-detail

- 

**Refers To**: Assessment

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date on which a user referenced the record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date on which a user viewed the record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the assessment saved session record.

### UsageType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: Specifies the use case of the saved assessment session.

- 

**Possible values**:

  - `HealthCloud`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentsavedsession.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
