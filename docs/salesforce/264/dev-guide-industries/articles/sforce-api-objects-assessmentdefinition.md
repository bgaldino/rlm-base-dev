---
page_id: sforce-api-objects-assessmentdefinition
title: AssessmentDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentdefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_assessmentdefinition.htm
fetched_at: 2026-11-25
---

# AssessmentDefinition

Represents the definition of an assessment including details such as the last revised date and purpose. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### ApprovalDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the assessment was approved by the publisher.

### DisplayType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Specifies the display format for questions in the assessment for the end-user.

### EffectiveFromDate

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date when the assessment takes effect.

### EffectiveToDate

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date until the assessment is in effect.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when the record was last referenced.

### LastRevisedDateTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the assessment was last revised.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when the record was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the record.

### OwnerId

- 

**Type**: reference

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: The user who owns the record.

This field is a polymorphic relationship field.

- 

**Relationship Name**: Owner

- 

**Refers To**: Group, User

### PerformerType

- **Type**: multipicklist

- **Properties**: Create, Filter, Nillable, Update

- **Description**: Specifies the type of performer that can record responses to the assessment.

### PublisherId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The organization or individual that published the assessment.

This field is a polymorphic relationship field.

- 

**Relationship Name**: Publisher

- 

**Refers To**: Account, Contact, User

### Purpose

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The purpose of the assessment.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AssessmentDefinitionChangeEvent](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-change-event.html)**

: 

Change events are available for the object.

**[AssessmentDefinitionHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

**[AssessmentDefinitionOwnerSharingRule](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-ownersharingrule.html)**

: 

Sharing rules are available for the object.

**[AssessmentDefinitionShare](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-share.html)**

: 

Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentdefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
