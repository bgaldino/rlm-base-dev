---
page_id: sforce-api-objects-suggestedassessmentreason
title: SuggestedAssessmentReason
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-suggestedassessmentreason.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_suggestedassessmentreason.htm
fetched_at: 2026-11-25
---

# SuggestedAssessmentReason

Stores the reasons for a suggested assessment. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date on which a user referenced this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date on which a user viewed this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the record.

### PrimaryAsmtQuestionResponseId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The response value in the primary assessment that triggered the suggested assessment.

This field is a relationship field.

- 

**Relationship Name**: PrimaryAsmtQuestionResponse

- 

**Relationship Type**: Lookup

- 

**Refers To**: AssessmentQuestionResponse

### PrimaryAssessmentId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: The primary assessment from which a suggested assessment was triggered.

This field is a relationship field.

- 

**Relationship Name**: PrimaryAssessment

- 

**Relationship Type**: Lookup

- 

**Refers To**: Assessment

### SuggestedAssessmentDefId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The suggested assessment associated with the suggested assessment reason.

This field is a relationship field.

- 

**Relationship Name**: SuggestedAssessmentDef

- 

**Relationship Type**: Lookup

- 

**Refers To**: SuggestedAssessmentDef

### SuggestionSourceType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: Specifies the source of the logic by which an assessment was suggested.

- 

**Possible values**:

  - `Business Rule`

  - `MCG`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[SuggestedAssessmentReasonFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[SuggestedAssessmentReasonHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-suggestedassessmentreason.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
