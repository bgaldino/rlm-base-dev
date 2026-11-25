---
page_id: tooling-api-objects-batchdatasource
title: BatchDataSource
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-batchdatasource.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch-management-setup-object
legacy_page_id: tooling_api_objects_batchdatasource.htm
fetched_at: 2026-11-25
---

# BatchDataSource

Represents the source of information from which a batch job retrieves records for processing. This object is available in API version 66.0 and later.

## Supported Calls

`describeSObjects()`, `query()`, `retrieve()`

## Special Access Rules

To know the permissions needed to access this object, See [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm).

## Fields

### BatchJobDefinitionId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Sort

- 

**Description**: The ID of the batch job definition associated with batch data source.

This field is a relationship field.

- 

**Relationship Name**: BatchJobDefinition

- 

**Relationship Type**: Master-detail

- 

**Refers To**: BatchJobDefinition (the master object)

### CriteriaJoinCondition

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The logic that’s used to decide how data source records are filtered.

### CriteriaJoinType

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Restricted picklist, Sort

- 

**Description**: Specifies the criteria type used to filter data source records.

- 

**Default value**: `all`

- 

**Possible values**:

  - `all`—All conditions are met (AND)

  - `any`—Any condition is met (OR)

  - `custom`—Customize the logic

  - `none`—No conditions are met

### DataSourceType

- 

**Type**: picklist

- 

**Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Specifies the type of data source.

- 

**Possible values**:

  - `MultipleSobjects`

  - `SingleSobject`

  - `File`

### RelatedSobjects

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The list of objects that are used as data sources for the batch job definition.

### SourceFieldName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The field from the source object that’s used to run the batch job.

### SourceTableName

- **Type**: string

- **Properties**: Filter, Group, Sort

- **Description**: The name of the object from which records are processed by the batch job.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/tooling-api-objects-batchdatasource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
