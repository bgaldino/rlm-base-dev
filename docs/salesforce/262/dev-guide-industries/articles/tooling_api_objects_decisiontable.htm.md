---
page_id: tooling_api_objects_decisiontable.htm
title: DecisionTable
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_decisiontable.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_setup_objects.htm
fetched_at: 2026-06-25
---

# DecisionTable

Represents the information about a decision table. This object is
available in API version 51.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Where possible, we changed noninclusive terms to align with our company value of
Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported SOAP API Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`,
`update()`, `upsert()`

## Supported REST API Methods

`DELETE, GET, HEAD, PATCH, POST, Query`

## Fields

| Field | Details |
| --- | --- |
| CollectOperator | Type  string  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  For internal use only. |
| ConditionCriteria | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Custom logic that's used to decide how the input fields are processed. |
| ConditionType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Condition logic that's used for input fields.  Possible values are:  - `All`—All conditions are met   (AND) - `Any`—Any condition is met   (OR) - `Custom`—Custom Logic  The default value is 'All'. |
| DataSourceType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Type of data source that’s used to create a decision table. Available in API version 59.0 and later.  Valid values are:  - `ContextDefinition` - `CsvUpload` - `MultipleSobjects` - `SingleSobject`  The default value is `SingleSobject`. |
| DecisionTableParameters | Type  [QueryResult](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_tooling.meta/api_tooling/tooling_api_objects_queryresult.htm "HTML (New Window)")  Properties  Nillable  Description  Input or output field in a decision table. |
| DecisionTableSourceCriterias | Type  [QueryResult](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_tooling.meta/api_tooling/tooling_api_objects_queryresult.htm "HTML (New Window)")  Properties  Nillable  Description  Filter criteria that’s associated with the decision table condition. Available in API version 59.0 and later. |
| Description | Type  textarea  Properties  Filter, Nillable, Sort  Description  Description of the decision table. |
| DeveloperName | Type  string  Properties  Filter, Group, Sort  Description  Developer name of the decision table. |
| DoesConsiderNullValue | Type  boolean  Properties  Defaulted on create, Filter, Group, Nillable, Sort  Description  Indicates whether a column that has a null value is considered for lookup (`true`) or not (`false`). The default value is `false`. Available in API version 60.0 and later. |
| DownloadStatus | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Specifies the progress status of a CSV download from a CSV-based lookup table. Available in API version 64.0 and later.  Valid values are:  - `Completed` - `DownloadInProgress` - `Failed` |
| executionType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the backing storage for the Decision Table. Valid values are:   - `Dmo` - `Hbase` - `Hbpo` - `Solr` - `Soql` |
| FilterResultBy | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  If a collection of inputs returns multiple matching outputs, then the FilterResultBy field specifies how the results of a decision table are filtered.  Available in API version 59.0 and later.  Valid values are:  - `AnyValue` - `CollectOperator` - `FirstMatch` - `OutputOrder` - `Priority` - `RuleOrder` - `UniqueValues` |
| FullName | Type  string  Properties  Create, Group, Nillable  Description  Name of the decision table.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| IsVersioned | Type  boolean  Properties  Filter, Group, Nillable, Sort  Description  Indicates whether the CSV based decision table has multiple versions (`true`) or not (`false`). The default value is `false`. Available in API version 60.0 and later. |
| Language | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Language in which the decision table is created.  Possible values are:  - `da`—Danish - `de`—German - `en_US`—English - `es`—Spanish - `es_MX`—Spanish (Mexico) - `fi`—Finnish - `fr`—French - `it`—Italian - `ja`—Japanese - `ko`—Korean - `nl_NL`—Dutch - `no`—Norwegian - `pt_BR`—Portuguese   (Brazil) - `ru`—Russian - `sv`—Swedish - `th`—Thai - `zh_CN`—Chinese   (Simplified) - `zh_TW`—Chinese   (Traditional) |
| LastSyncDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  Latest date on which the decision table was refreshed. |
| ManageableState | Type  ManageableState enumerated list  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the manageable state of the specified component that is contained in a package:  - `beta` - `deleted` - `deprecated` - `deprecatedEditable` - `installed` - `installedEditable` - `released` - `unmanaged` |
| MasterLabel | Type  string  Properties  Filter, Group, Sort  Description  Label of the decision table. |
| Metadata | Type  complexvalue  Properties  Create, Nillable, Update  Description  Metadata of the decision table.  Query this field only if the query result contains no more than one record. Otherwise, an error is returned. If more than one record exists, use multiple queries to retrieve the records. This limit protects performance. |
| NamespacePrefix | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Namespace prefix that’s associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation.  The namespace prefix can have one of the following values.   - In Developer Edition orgs, NamespacePrefix is set   to the namespace prefix of the org for all objects that support it, unless   an object is in an installed managed package. In that case, the object has   the namespace prefix of the installed managed package. This field’s value   is the namespace prefix of the Developer Edition org of the package   developer. - In orgs that aren’t Developer Edition orgs,   NamespacePrefix is set only for objects that are   part of an installed managed package. All other objects have no namespace   prefix. |
| PricingElementDecisionTables | Type  [QueryResult](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_tooling.meta/api_tooling/tooling_api_objects_queryresult.htm "HTML (New Window)")  Properties  Nillable  Description  Reserved for future use. |
| RefreshFailureReason | Type  string  Properties  Filter, Nillable, Sort  Description  Reason for the refresh of the decision table data to fail. Available in API version 60.0 and later. |
| RefreshStatus | Type  string  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Refresh status of the cached data in the decision table. Available in API version 60.0 and later.  Valid values are:   - `Initiated` - `Failed` - `Completed` - `CompletedWithWarnings` - `In Progress` |
| RowLevelOverrideType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the row-level criteria that overrides the Decision Table column criteria.  Valid values are:  - `Both` - `Condition` - `None` - `Operator` The default value is `None`. |
| SetupName | Type  string  Properties  Filter, Group, Sort  Description  Required. Name of the decision table, which appears in Setup. |
| SourceConditionLogic | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Condition logic that's used to define the decision table from the source data.  Available in API version 59.0 and later. |
| SourceObject | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Required. Object that contains the rules based on which the decision table must provide outcomes. |
| Status | Type  picklist  Properties  Filter, Group, Restricted picklist, Sort  Description  Required. Status of the decision table.  Valid values are:  - `ActivationInProgress` - `Active` - `Draft` - `Inactive` |
| Type | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Determine whether a decision table’s data volume is high or low.  Available in API version 59.0 and later.  Valid values are:  - `Advanced` - `HighScaleExecution` - `HighVolume`–Reserved for   future use - `LowVolume` - `MediumVolume` - `RealTime`   The default value is `LowVolume`. |
| UsageType | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort  Description  Usage type of the decision table.  Available in API version 59.0 and later.   - `Bre`–Default - `ProductCategoryQualification` - `ProductQualification` - `RecordAlert`   When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. |
