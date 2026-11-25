---
page_id: sforce-api-objects-assessmentquestioncatgdata
title: AssessmentQuestionCatgData
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentquestioncatgdata.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
fetched_at: 2026-11-25
---

# AssessmentQuestionCatgData

Stores category-level aggregated scores for an assessment. This object is available in API version 67.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssessedScore

- **Type**: double

- **Properties**: Filter, Nillable, Sort

- **Description**: Score assigned to the category for the evaluation.

### AssessmentId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort

- 

**Description**: ID of the submitted assessment.

This field is a relationship field.

- 

**Relationship Name**: Assessment

- 

**Relationship Type**: Master-detail

- 

**Refers To**: Assessment (the master object)

### MaximumScore

- **Type**: double

- **Properties**: Filter, Nillable, Sort

- **Description**: Maximum score derived from all applicable response choices for a question in the category, used as the denominator in percentage calculations.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Name of this assessment question category data.

### QuestionCategory

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: Question category for which the aggregate score is calculated.

- 

**Possible values**:

  - `Demographic`

  - `Financial`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentquestioncatgdata.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
