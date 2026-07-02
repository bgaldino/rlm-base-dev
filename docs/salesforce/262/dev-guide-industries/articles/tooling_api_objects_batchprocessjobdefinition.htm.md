---
page_id: tooling_api_objects_batchprocessjobdefinition.htm
title: BatchProcessJobDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_batchprocessjobdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: batch_management_setup_object.htm
fetched_at: 2026-06-25
---

# BatchProcessJobDefinition

Represents the details of a Batch Management job. This object is available
in API version 51.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our company value of
Equality. We maintained certain terms to avoid any effect on customer
implementations.

Data and processes in your org are impacted if you update or delete a
BatchProcessJobDefinition record. Update or delete a Batch Management job using the [Metadata API](./batch_metadata.htm.md "Use a Metadata API to create, update, and activate Batch Management jobs.").

## Supported SOAP API Calls

`describeSObjects()`, `query()`, `retrieve()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| BatchJobDefinitionId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier of the associated batch job definition.  This is a relationship field.  Relationship Name  BatchJobDefinition  Relationship Type  Lookup  Refers To  BatchJobDefinition |
| BatchJobDefinitionName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the associated batch job definition. |
| BatchSize | Type  int  Properties  Filter, Group, Sort  Description  Required. The number of records that each Batch Management job part can process. The maximum number of transaction journal records that a batch management job can process for flow or loyalty program process is 2000. |
| Description | Type  textarea  Properties  Filter, Group, Nillable, Sort  Description  The description of the Batch Management job. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  The developer name of the Batch Management job. |
| FlowDefinitionId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The input variable of the associated flow that uniquely identifies each record that the Batch Management job processes. |
| FullName | Type  string  Properties  Create, Group, Nillable  Description  The name of the Batch Management job.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The language in which the batch job is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  The label of the Batch Management job. |
| Metadata | Type  complexvalue  Properties  Create, Nillable, Update  Description  The Batch Management job's metadata.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation.  The namespace prefix can have one of the following values.   - In Developer Edition orgs, NamespacePrefix is set   to the namespace prefix of the org for all objects that support it, unless   an object is in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This field’s value   is the namespace prefix of the Developer Edition org of the package   developer. - In orgs that are not Developer Edition orgs,   NamespacePrefix is set only for objects that are   part of an installed managed package. All other objects have no namespace   prefix. |
| ProcessGroup | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The group or team for which the Batch Management job processes records. |
| RecordIdVariable | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The unique identifier that identifies each record that must be processed by the Batch Management job. |
| RetryCount | Type  int  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. The number of times this Batch Management job must be rerun in case it fails. |
| RetryInterval | Type  int  Properties  Defaulted on create, Filter, Group, Sort  Description  Required. The number of milliseconds after which the Batch Management job must be rerun in case it fails. A retry interval can be 1,000–10,000 milliseconds. |
| Status | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The status of the Batch Management job.  Possible values are:  - `Active` - `Inactive` |
| Type | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of process for which the Batch Management job processes records.  Possible values are:  - `Flow` - `BulkUpdate` - `ConsumptionOveragesCalculation` - `DecisionTableRefresh` - `DeepCloneSalesAgreement` - `EntitlementCreationBatchJob` - `HighScaleBreProcess` - `IndustriesLSCommercial` - `LoyaltyProgramProcess` - `ManagerProvisioning` - `NetUnitRateCalculation` - `PbbToOptyConversion` - `ProductCatalogCacheRefresh` - `RatableSummaryCreation` - `SummaryCreation`   The default value is `Flow`. Other types may be available to you depending on the licenses available in your org.  This field is available in API version 55.0 and later. |
| TypeInstance | Type  string  Properties  Filter, Group, Sort  Description  Required. The API name of the process that the Batch Management job must execute. |
