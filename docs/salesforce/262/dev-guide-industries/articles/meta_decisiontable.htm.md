---
page_id: meta_decisiontable.htm
title: DecisionTable
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_decisiontable.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_metadata_api.htm
fetched_at: 2026-06-25
---

# DecisionTable

Represents the information about a decision
table.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to
align with our company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the Metadata metadata type and inherits its fullName field.

## File Suffix and Directory Location

DecisionTable components have the suffix .decisionTable and are stored
in the decisionTables folder.

## Version

DecisionTable components are available in API version 51.0 and later.

## Special Access Rules

To use this metadata type, your Salesforce org must have the Loyalty Management or the
Rebate Management license.

## Fields

| Field Name | Description |
| --- | --- |
| collectOperator | Field Type  DecisionTable​CollectOperator (enumeration of type string)  Description  Specifies the operator that's used when the result is filtered by the Collect operator. Valid values are:   - `Count` - `Maximum` - `Minimum` - `None` - `Sum` |
| condition​Criteria | Field Type  string  Description  Logic that's used to decide how the input fields are processed. |
| conditionType | Field Type  DecisionTable​ConditionType (enumeration of type string)  Description  Condition logic that's used for input fields. Valid values are:   - `All` - `Any` - `Custom` |
| dataSource​Type | Field Type  DecisionTable​DataSourceType (enumeration of type string)  Description  Specifies the type of data source that's used to create a decision table. Valid values are:   - `ContextDefinition` - `CsvUpload` - `MultipleSobjects` - `SingleSobject` |
| decisionTable​FileImportVersions | Field Type  [DecisionTableFileImportVersion](#DecisionTableFileImportVersion)[]  Description  Versions of the decision table that were imported from a CSV file. Each version captures a separate import iteration with its own activation window, rank, and refresh status.  Available in API version 67.0 and later. |
| decisionTable​Parameters | Field Type  [DecisionTableParameter[]](#DecisionTableParameter)  Description  Parameters that you specify in a decision table. |
| decisionTable​SourceCriterias | Field Type  [DecisionTableSourceCriteria[]](#DecisionTableSourceCriteria)  Description  The fields and values from a data source that are used to define the condition logic of the data that's used in a decision table. |
| description | Field Type  string  Description  Description of the decision table. |
| doesConsider​NullValue | Field Type  boolean  Description  Indicates whether a column that has a null value is considered for lookup (`true`) or not (`false`). The default value is false. |
| downloadStatus | Field Type  DecisionTableDownloadStatus (enumeration of type string)  Description  Specifies the progress status of a CSV download from a CSV-based lookup table. Available in API version 64.0 and later. Valid values are:   - `Completed` - `DownloadInProgress` - `Failed` |
| executionType | Field Type  DecisionTableExecutionType (enumeration of type string)  Description  Indicates the backing storage for the Decision Table. Valid values are:   - `DLO`—Available in API version 67.0   and later. Replaces `DMO`. - `HBASE` - `HBPO` - `SOLR` - `SOQL` |
| filterResultBy | Field Type  DecisionTableHitPolicy (enumeration of type string)  Description  Specifies how the results of a decision table are filtered if a set of inputs returns multiple matching outputs. Valid values are:   - `AnyValue` - `CollectOperator` - `FirstMatch` - `OutputOrder` - `Priority` - `RuleOrder` - `UniqueValues` |
| hasIncremental​SyncFailed | Field Type  boolean  Description  Indicates if the last incremental refresh failed. |
| isIncremental​SyncEnabled | Field Type  boolean  Description  Indicates if incremental refresh is enabled for the Decision Table. |
| isVersioned | Field Type  boolean  Description  Indicates whether the CSV based decision table supports multiple file-import versions (`true`) or not (`false`). When set to `true`, the decisionTableFileImportVersions collection captures each version. The default value is `true`.  Available in API version 67.0 and later. |
| lastIncremental​SyncDate | Field Type  string  Description  The date and time on which the last incremental refresh occured for the decision table. |
| lastSyncDate | Field Type  string  Description  Latest date on which the decision table was refreshed. |
| refresh​FailureReason | Field Type  string  Description  Reason why the refresh of the decision table data failed. |
| refreshStatus | Field Type  DecisionTableRefreshStatus (enumeration of type string)  Description  Specifies the refresh status of the cached data in the decision table. Valid values are:   - `Completed` - `CompletedWithWarnings`—Available in   API version 67.0 and later. - `Failed` - `InProgress` - `Initiated` |
| setupName | Field Type  string  Description  Required. Name of the decision table, which appears in Salesforce Setup. |
| sourceCondition​Logic | Field Type  string  Description  The condition logic that's used to define the decision table from the source data. |
| sourceObject | Field Type  string  Description  Required. Object that contains the rules based on which the decision table must provide outcomes. |
| status | Field Type  DecisionTableStatus (enumeration of type string)  Description  Required. Status of the decision table.  Valid values are:   - `ActivationInProgress` - `Active` - `Draft` - `Inactive` |
| type | Field Type  DecisionTableType (enumeration of type string)  Description  Stores the type of decision table. Valid values are:   - `Advanced` - `HighScaleExecution` - `HighVolume` - `LowVolume` - `MediumVolume` - `RealTime` |
| uploadStatus | Field Type  DecisionTableUploadStatus (enumeration of type string)  Description  Specifies the progress status of the CSV upload for a CSV based Lookup table. Valid values are:   - `Completed` - `CompletedWithErrors` - `Failed` - `UploadInProgress` |
| usageType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  Type of industry or the application within the industry that's using a decision table. Valid values are:   - `Bre` - `ComplianceControl` - `DecompositionEnrichmentMapping` - `DefaultPricing` - `DefaultRating` - `EventOrchestration` - `FinancialServicesCloud` - `FulfillmentCondition` - `GpaCalculation` - `InsuranceClaimProcessing`—Available in API version 65.0   and later. - `ItServiceManagement`—Available in API version 65.0 and   later. - `PlanCostCalculation` - `PriceProtection` - `PricingDiscovery` - `ProductCategoryQualification` - `ProductQualification` - `RatingDiscovery` - `RecordAlert` - `ShipAndDebit` - `StudentInformationSystem`—Available in API version 65.0   and later. - `StudentSuccess` - `TestProcess` - `WarrantyClaim`   When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other usage types are available to you depending on your industry solution and permission sets. |

## DecisionTableFileImportVersion

Represents a version of a CSV file-import for a CSV-based decision table. Each version
captures a separate import iteration with its own activation window, rank, and refresh
status. Available in API version 67.0 and later.

| Field Name | Description |
| --- | --- |
| endDate | Field Type  string  Description  The date and time when the decision table version becomes inactive. |
| lastIncremental​SyncDate | Field Type  string  Description  The date and time on which the last incremental refresh occured for the decision table version. |
| lastSyncDate | Field Type  string  Description  The date and time on which the last refresh occured for the decision table version. |
| rank | Field Type  int  Description  Required.  The current rank of the decision table version that’s used to determine when it can get chosen for processing. |
| refresh​FailedReason | Field Type  string  Description  The reason the most recent refresh of the decision table version data failed. |
| refreshStatus | Field Type  DecisionTable​RefreshStatus (enumeration of type string)  Description  Specifies the refresh status of the cached data in the decision table version. Valid values are:   - `Completed` - `CompletedWithWarnings` - `Failed` - `InProgress` - `Initiated` |
| startDate | Field Type  string  Description  Required.  The date and time when the decision table version becomes active. |
| uploadStatus | Field Type  DecisionTable​UploadStatus (enumeration of type string)  Description  Specifies the progress status of the CSV upload for the decision table version. Valid values are:   - `Completed` - `CompletedWithErrors` - `Failed` - `UploadInProgress` |
| versionName | Field Type  string  Description  Required.  The name of the decision table version. The maximum length is 120 characters. |
| versionNumber | Field Type  int  Description  Required.  The decision table version number. The combination of decisionTable and versionNumber must be unique. |
| versionStatus | Field Type  DecisionTableStatus (enumeration of type string)  Description  Required.  The status of the decision table version. Valid values are:   - `ActivationInProgress` - `Active` - `Inactive` |

## DecisionTableParameter

Represents an input or output field of a decision table.

| Field Name | Description |
| --- | --- |
| dataType | Field Type  DTParameterDataType (enumeration of type string)  Description  The data type of the field used in a decision table. Valid values are:   - `Boolean` - `Currency` - `Date` - `DateTime` - `Number` - `Percent` - `String` |
| decimalScale | Field Type  int  Description  The number of digits to the right of the decimal point. |
| domainObject | Field Type  string  Description  For polymorhpic fields, indicates the domain object in the field hierarchy. |
| fieldName | Field Type  string  Description  Required. API name of the fields that selected as an input or output for the decision table. |
| fieldPath | Field Type  string  Description  The path of the field used in a decision table in relation to the object that the field belongs to. |
| isGroup​ByField | Field Type  boolean  Description  Indicates whether an input field is used to group the business rules of the decision table. |
| isPriority​Field | Field Type  boolean  Description  Indicates whether a field is given priority. |
| isRequired | Field Type  boolean  Description  Indicates whether a field is required to be used for lookups. |
| length | Field Type  int  Description  The maximum number of characters supported for a field that's used in a decision table. |
| operator | Field Type  DecisionTableOperator (enumeration of type string)  Description  Operator used for the input field. Valid values are:   - `Contains` - `DoesNotExistIn` - `DoesNotMatch` - `Equals` - `ExistsIn` - `GreaterOrEqual` - `GreaterThan` - `IsNotNull` - `IsNull` - `LessOrEqual` - `LessThan` - `Matches` - `NotEquals` |
| sequence | Field Type  int  Description  The sequence in which input fields are processed. This field is available in API version 52.0 and later. |
| sortType | Field Type  DecisionTableSortType (enumeration of type string)  Description  Sort outputs of a decision table based on the values of the input or output parameter field. This field is available in API version 56.0 and later. Valid values are:   - `AscNullFirst` - `AscNullLast` - `DescNullFirst` - `DescNullLast` - `None` |
| usage | Field Type  DecisionTableParameterType (enumeration of type string)  Description  Required. Usage type of a field.  Valid values are:   - `INPUT` - `OUTPUT` - `ROWCRITERIA` |

## DecisionTableSourceCriteria

Represents the fields and values from a data source that are used to define the condition
logic of the data that's used in a decision table.

| Field Name | Description |
| --- | --- |
| operator | Field Type  DTSourceCriteriaOperator (enumeration of type string)  Description  Required. The operator that’s applied to an associated decision table’s field to filter the data.  Valid values are:   - `Contains` - `DoesNotExistIn` - `DoesNotMatch` - `Equals` - `ExistsIn` - `GreaterOrEqual` - `GreaterThan` - `IsNotNull` - `IsNull` - `LessOrEqual` - `LessThan` - `Matches` - `NotEquals` |
| sequenceNumber | Field Type  int  Description  Required. The sequence number used in the associated decision table's source condition logic. |
| sourceField​Name | Field Type  string  Description  Required. The name of the field that's used in the decision table. |
| value | Field Type  string  Description  The value that’s expected in the source field used in the decision table. |
| valueType | Field Type  DTSourceCriteriaValueType (enumeration of type string)  Description  Required. The type of the value that’s used to filter the source data.  Valid values are:   - `Formula` - `Literal` - `Lookup` - `Parameter` - `Picklist` |

## Declarative Metadata Sample Definition

The following is an example of a DecisionTable component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DecisionTable xmlns="http://soap.sforce.com/2006/04/metadata">
    <collectOperator>None</collectOperator>
    <conditionCriteria>1 and 2 and 3 and 4</conditionCriteria>
    <conditionType>All</conditionType>
    <dataSourceType>SingleSobject</dataSourceType>
    <decisionTableParameters>
        <fieldName>IsDeleted</fieldName>
        <operator>Equals</operator>
        <usage>INPUT</usage>
        <sequence>1</sequence>
        <isGroupByField>true</isGroupByField>
        <sortType>AscNullFirst</sortType>
        <dataType>Number</dataType>
        <fieldPath>AccountFeed.CommentsCount</fieldPath>
        <domainObject>AccountFeed</domainObject>
        <isPriorityField>false</isPriorityField>
        <decimalScale>2</decimalScale>
        <length>14</length>
        <isRequired>false</isRequired>
    </decisionTableParameters>
    <decisionTableParameters>
        <fieldName>IsActive</fieldName>
        <usage>OUTPUT</usage>
    </decisionTableParameters>
    <decisionTableParameters>
        <fieldName>LimitNumber</fieldName>
        <operator>Equals</operator>
        <usage>INPUT</usage>
        <sequence>2</sequence>
        <isGroupByField>false</isGroupByField>
    </decisionTableParameters>
    <decisionTableParameters>
        <fieldName>LimitStartDate</fieldName>
        <usage>OUTPUT</usage>
    </decisionTableParameters>
    <decisionTableParameters>
        <fieldName>GivenBadgeCount</fieldName>
        <operator>Equals</operator>
        <usage>INPUT</usage>
        <sequence>3</sequence>
        <isGroupByField>false</isGroupByField>
    </decisionTableParameters>
    <decisionTableParameters>
        <fieldName>Name</fieldName>
        <operator>Equals</operator>
        <usage>INPUT</usage>
        <sequence>4</sequence>
        <isGroupByField>false</isGroupByField>
    </decisionTableParameters>
    <decisionTableSourceCriterias>
        <sourceFieldName>IsDeleted</sourceFieldName>
        <operator>Equals</operator>
        <value>false</value>
        <sequenceNumber>1</sequenceNumber>
        <valueType>Literal</valueType>
    </decisionTableSourceCriterias>
    <description>Sample DT created for md-common tests</description>
    <filterResultBy>UniqueValues</filterResultBy>
    <setupName>Sample DT</setupName>
    <sourceObject>WorkBadgeDefinition</sourceObject>
    <sourceConditionLogic>1</sourceConditionLogic>
    <status>Draft</status>
    <type>LowVolume</type>
    <usageType>Bre</usageType>
    <doesConsiderNullValue>false</doesConsiderNullValue>
    <refreshStatus>Failed</refreshStatus>
    <refreshFailureReason>Failed due to limit violation.</refreshFailureReason>
    <executionType>Hbpo</executionType>
    <lastIncrementalSyncDate>""</lastIncrementalSyncDate>
    <uploadStatus>Completed</uploadStatus>
    <isIncrementalSyncEnabled>false</isIncrementalSyncEnabled>
    <hasIncrementalSyncFailed>false</hasIncrementalSyncFailed>
</DecisionTable>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
   <fullName>Sample DT Package</fullName>
   <description>Package created for md-common tests</description>
   <types>
      <members>Sample_DT</members>
      <name>DecisionTable</name>
   </types>
   <types>
      <members>DSL_Sample</members>
      <members>Sample_DT_Default</members>
      <name>DecisionTableDatasetLink</name>
   </types>
   <version></version>
</Package>
```
