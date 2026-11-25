---
page_id: sforce-api-objects-omniprocessasmtquestionver
title: OmniProcessAsmtQuestionVer
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omniprocessasmtquestionver.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_omniprocessasmtquestionver.htm
fetched_at: 2026-11-25
---

# OmniProcessAsmtQuestionVer

Represents a junction between an OmniScript process and an assessment question version. This object is available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssessmentQuestionVersionId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Required. The ID of assessment question version associated with the Omni Process assessment question version record.

This is a relationship field.

- 

**Relationship Name**: AssessmentQuestionVersion

- 

**Relationship Type**: Lookup

- 

**Refers To**: AssessmentQuestionVersion

### IsImportant

- 

**Type**: boolean

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: Indicates whether the assessment question version is important (`true`) or not (`false`).

Available in API version 59.0 and later.

- 

**Default value**: `false`

### IsPrefill

- 

**Type**: boolean

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: Indicates whether the assessment question version is prefilled (`true`) or not (`false`).

Available in API version 60.0 and later.

- 

**Default value**: `false`

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

- **Description**: Required. The name of the Omni Process assessment question version record.

### OmniProcessElementId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Required. The ID of the Omni Process element associated with the Omni Process assessment question version record.

This is a relationship field.

- 

**Relationship Name**: OmniProcessElement

- 

**Relationship Type**: Lookup

- 

**Refers To**: OmniProcessElement

### OmniProcessId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Required. The ID of the Omni Process associated with the Omni Process assessment question version record.

This is a relationship field.

- 

**Relationship Name**: OmniProcess

- 

**Relationship Type**: Lookup

- 

**Refers To**: OmniProcess

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

### QuestionWeight

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: A non-negative weight assigned to the question in the Omni process. Higher values give the question more weight. This field is available in API version 67.0 and later.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[OmniProcessAsmtQuestionVerChangeEvent](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-change-event.html)**

: 

Change events are available for the object.

**[OmniProcessAsmtQuestionVerFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[OmniProcessAsmtQuestionVerHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

**[OmniProcessAsmtQuestionVerOwnerSharingRule](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-ownersharingrule.html)**

: 

Sharing rules are available for the object.

**[OmniProcessAsmtQuestionVerShare](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-share.html)**

: 

Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omniprocessasmtquestionver.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
