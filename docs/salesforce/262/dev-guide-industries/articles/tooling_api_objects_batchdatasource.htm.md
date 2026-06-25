---
page_id: tooling_api_objects_batchdatasource.htm
title: BatchDataSource
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchdatasource.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_setup_object.htm
fetched_at: 2026-06-25
---

# BatchDataSource

Represents the source of information from which a batch job retrieves records
for processing. This object is available in API version 66.0 and later.

## Supported Calls

`describeSObjects()`, `query()`, `retrieve()`

## Fields

| Field | Details |
| --- | --- |
| BatchJobDefinitionId | Type  reference  Properties  Filter, Group, Sort  Description  The ID of the batch job definition associated with batch data source.  This field is a relationship field.  Relationship Name  BatchJobDefinition  Relationship Type  Master-detail  Refers To  BatchJobDefinition (the master object) |
| CriteriaJoinCondition | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The logic that's used to decide how data source records are filtered. |
| CriteriaJoinType | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  Specifies the criteria type used to filter data source records.  Possible values are:  - `all`—All   conditions are met (AND) - `any`—Any   condition is met (OR) - `custom`—Customize   the logic - `none`—No   conditions are met  The default value is `all`. |
| DataSourceType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the type of data source.  Possible values are:  - `MultipleSobjects` - `SingleSobject` - `File` |
| RelatedSobjects | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The list of objects that are used as data sources for the batch job definition. |
| SourceFieldName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The field from the source object that's used to run the batch job. |
| SourceTableName | Type  string  Properties  Filter, Group, Sort  Description  The name of the object from which records are processed by the batch job. |
