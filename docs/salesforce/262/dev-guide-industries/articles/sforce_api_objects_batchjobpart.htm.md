---
page_id: sforce_api_objects_batchjobpart.htm
title: BatchJobPart
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_batchjobpart.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: monitor_workflow_services_dev_overview.htm
fetched_at: 2026-06-25
---

# BatchJobPart

Represents one part of a batch job. This object is available in API
version 51.0 and later.

When a batch job is run, it is divided in to multiple parts. Each part is used to process a
specific number of records.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`,
`retrieve()`

## Fields

| Field | Details |
| --- | --- |
| AdditionalInformation | Type  string  Properties  Filter, Nillable, Sort  Description  Contains additional information on the batch job part. |
| BatchJobId | Type  reference  Properties  Filter, Group, Sort  Description  The unique identifier of the associated batch job.  This is a relationship field.  Relationship Name  BatchJob  Relationship Type  Lookup  Refers To  BatchJob |
| EndTime | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the batch job part was processed. |
| ErrorDescription | Type  string  Properties  Filter, Nillable, Sort  Description  The error message in case the batch job part failed. |
| FailedRecFileBody | Type  base64  Properties  Nillable  Description  Contains the details of the records that the batch job part failed to process. |
| FailedRecFileContentType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Shows the type of data that the batch job part failed to process. For example, `application/html` or `text/csv` or `text/vcard`. |
| FailedRecFileLength | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The character length of the failed record file. |
| FailedRecFileName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the file that contains the details of the failed records. |
| FailedRecordCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of records that the batch job part couldn't process. |
| FailedRowCount | Type  long  Properties  Filter, Group, Nillable, Sort  Description  The number of records that were processed but the batch job part failed to write back for a Data Processing Engine definition run. This field is available in API version 66.0 and later. |
| InputRecordCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of records that the batch job part must process. |
| InputRowCount | Type  long  Properties  Filter, Group, Nillable, Sort  Description  The number of records that were submitted to the batch job part for a Data Processing Engine definition run. This field is available in API version 66.0 and later. |
| Name | Type  string  Properties  Filter, Group, idLookup, Sort  Description  The name of the batch job part. |
| OutputRecordCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of records the batch job part has processed. |
| OutputRowCount | Type  long  Properties  Filter, Group, Nillable, Sort  Description  The number of records that were processed by the batch job part for a Data Processing Engine definition run. This field is available in API version 66.0 and later. |
| ParentBatchJobPartId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier of the part batch job part associated with the batch job part.  This is a relationship field.  Relationship Name  ParentBatchJobPart  Relationship Type  Lookup  Refers To  BatchJobPart |
| RecordFileBody | Type  base64  Properties  Nillable  Description  Contains the details of the records that the batch job part processed. |
| RecordFileContentType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Shows the type of data that the batch job part processed. For example, `application/html` or `text/csv` or `text/vcard`. |
| RecordFileLength | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The character length of the file that contains the records that the batch job part processed. |
| RecordFileName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the file that contains the details of the records that the batch job part processed. |
| RetryCount | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The number of times the batch job part is automatically rerun in case it fails. |
| StartTime | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the batch job part's run was started. |
| Status | Type  picklist  Properties  Defaulted on create, Filter, Group, Restricted picklist, Sort  Description  The status of the batch job part.  Possible values are:  - `Canceled` - `Completed` - `Failed` - `InProgress` - `New` - `Waiting` |
| Type | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of node in case the associated batch job is of the type Calc (Data Processing Engine).  Possible values are:  - `Aggregate` - `Analysis` - `Append` - `AtomicWriteback` - `Compute` - `CsvIngestion` - `Custom` - `Datasync` - `Execution` - `Filter` - `Forecast` - `Hierarchy` - `Join` - `OutputRecordsNode` - `Register` - `Slice` - `Source` - `Summary` - `Transform` - `Writeback` |
| UserReference | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The ID of the user who is assigned as the writeback user in the Writeback Object node of the Data Processign Engine definition for which the batch job part has written back results. This field is available in API version 66.0 and later. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available in
the specified API version and later.

BatchJobPartFeed
:   Feed tracking is available for the object.

BatchJobPartHistory
:   History is available for tracked fields of the object.
