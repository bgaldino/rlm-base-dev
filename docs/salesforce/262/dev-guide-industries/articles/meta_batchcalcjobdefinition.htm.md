---
page_id: meta_batchcalcjobdefinition.htm
title: BatchCalcJobDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_batchcalcjobdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: dpe_metadata.htm
fetched_at: 2026-06-25
---

# BatchCalcJobDefinition

Represents a Data Processing Engine definition.

## Parent Type

This type extends the Metadata metadata type and inherits its fullName
field.

## File Suffix and Directory Location

BatchCalcJobDefinition components have the suffix
.batchCalcJobDefinition and are stored in the
batchCalcJobDefinitions folder.

## Version

BatchCalcJobDefinition components are available in API version 51.0 and later.

## Special Access Rules

To use this metadata type, one of these licenses is required:

- Loyalty Management
- Financial Services Cloud
- Rebate Management
- Manufacturing Cloud
- Net Zero Cloud

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| aggregates | [BatchCalcJob​​​Aggregate](#bcjaggregateID)[] | Collection of aggregate nodes in a data processing engine. |
| appends | [BatchCalcJobUnion](#bcjunionID)[] | Collection of append nodes in a data processing engine. |
| atomicWritebacks | [BatchCalcJobAtomicWriteBack](#BatchCalcJobAtomicWriteback)[] | Collection of composite writeback nodes in a data processing engine definition. Available in API version 62.0 and later. |
| customNodes | [BatchCalcJobCustomNode](#bcjcustomnodeID)[] | Collection of custom nodes in a data processing engine. Available in API version 57.0 and later. |
| currencyConversion | string | Specifies the currency conversion type for the data processing engine definition. Available in API version 67.0 and later. |
| dataSpaceApiName | string | Stores the Data Space API Name from Data 360. Available in API version 60.0 and later. |
| datasources | [BatchCalcJob​Datasource](#bcjdatasourceID)[] | Collection of data source nodes in a data processing engine. |
| definitionRunMode | BatchCalcJobDefRunMode(enumeration of type string) | Specifies the execution mode in a data processing engine. Valid values are:  - `Batch` - `OnDemand` |
| description | string | Description of a data processing engine definition. |
| doesGenAllFailedRecords | boolean | Indicates whether the error file includes a complete list of all failed writeback records (`true`) or not (`false`). The default value is `false`, and only the first instance of a failure is recorded in the error file. If set to `true`, all failed records are recorded in the error file for the writeback node. Available in API version 65.0 and later. |
| executionPlatformObjectType | ExecutionPlatformObjectType(enumeration of type string) | The execution platform object type that's used during the read, transform, and writeback process for the Data Processing Engine definition. Possible values are:  - `CalculatedInsightsObject` - `DataLakeObject` - `DataModelObject` - `None`   Available in API version 65.0 and later. |
| executionPlatformType | ExecutionPlatformType(enumeration of type string) | The platform that's used to run the Data Processing Engine definition. Valid values are:  - `CRMA` - `CDP` - `CORE`   Available in API version 59.0 and later. |
| filters | [BatchCalcJobFilter](#bcjfilterID)[] | Collection of filter nodes in a data processing engine. definition. |
| forecasts | [BatchCalcJobForecast](#bcjforecastID)[] | Collection of forecast nodes in a data processing engine. definition. Available in API version 58.0 and later. |
| hierarchyPaths | [BatchCalcJobHierarchyPath](#bcjhierarchypathID)[] | Collection of hierarchy path nodes in a data processing engine definition. |
| isTemplate | boolean | Indicates whether it’s a template data processing engine definition. |
| joins | [BatchCalcJobSource​Join](#bcjsourcejoinID)[] | Collection of join nodes in a data processing engine. |
| label | string | The label of a data processing engine definition. |
| parameters | [BatchCalcJobParameter](#bcjparameterID)[] | Collection of input variables in a data processing engine. |
| processType | BatchCalcProcessType (enumeration of type string) | The process type of a data processing engine. These process types may be available to you depending on your industry solution and permission sets. Valid values are:  - `AccountingPeriodClosure` - `AccountingSubledger`—This value is   reserved for internal use. - `AccrualsAndPayoutEngine` - `ActionableList` - `AdvancedAccountForecast` - `AutomotiveFoundation` - `BenefitManagement` - `BillingSchedulesforInvoiceGeneration` - `CDPEnrichment` - `ChannelInventoryManagement`—Available in API version 63.0 and   later. - `CollectionPlan`—Available in API   version 65.0 and later. - `ContextService`—Available in API   version 67.0 and later. - `CriteriaBsdSearchAndFilter` - `DataProcessingEngine` - `DecisionMatrixDataUpload` - `Decisiontable` - `Education` - `EmployeeService`—Available in API   version 63.0 and later. - `EnergyUtilitiesSales` - `FinancialSummaryRollup` - `FlexibleHierarchy` - `ForeignExchangeGainLossCalculations`—Available in API version   65.0 and later. - `FSCHierarchyRollUp` - `Fundraising`—Available in API   version 64.0 and later. - `FundraisingRollups`—Available in   API version 63.0 and later. - `GeneralLedgerAccountBalancesSummary`—Available in API version   65.0 and later. - `InventoryBatchSearch`—Available in   API version 65.0 and later. - `InventorySearch`—Available in API   version 65.0 and later. - `InvoiceGeneration` - `Loyalty` - `LegalEntityAccountingPeriodClosureAdvanced`—Available in API   version 63.0 and later. - `LifeSciencbatchcalesCommercialTerritoryAlignment`—Available in   API version 63.0 and later. - `LifeSciencesCustomerEngagement`—Available in API version 64.0   and later. - `LoyaltyPartnerManagement` - `LoyaltyPointsAggregation` - `MediaAdSales` - `NextGenForecasting`—Available in   API version 64.0 and earlier. - `NetZero` - `PatientServicesProgram`—Available   in API version 64.0 and later. - `PlanningAndForecasting` - `PnmRosterFileUpload` - `PriceProtection` - `ProductCatalogManagement` - `ProgramBasedBusiness` - `ProviderSearch`—This value is   reserved for internal use. - `Rebates` - `RebateAndAccrualManagementAdvanced` - `Recruitment` - `RevenueTransactionManagement`—Available in API version 63.0 and   later. - `SalesAgreement`—Available in API   version 63.0 and later. - `TestAtomicWritebackScale`—Available   in API version 64.0 and later. - `TestProcessType` - `UsageManagement` |
| status | BatchJobDefinition​Status (enumeration of type string) | Status of a data processing engine definition. Valid values are:  - `Active` - `Inactive` |
| targetCurrencyIsoCode | string | ISO code of the target currency for currency conversion in the data processing engine definition. Available in API version 67.0 and later. |
| transforms | [BatchCalcJobTransform](#bcjtransformID)[] | Collection of data transformation nodes in a data processing engine. |
| writebacks | [BatchCalcJobWriteback​Object](#bcjwritebackobjectID)[] | Collection of writeback objects in which the results of the data processing engine are written back. |

## BatchCalcJob​​​Aggregate

Represents a collection of fields relating to an aggregate node in a data processing
engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | Description of an aggregate node. |
| fields | [BatchCalcJob​AggregateField](#bcjaggregatefieldID)[] | Required. Collection of aggregation fields. |
| groupBy | string[] | Required. Collections of fields used to group data in an aggregate node. |
| label | string | Required. Label of an aggregate node. |
| name | string | Required. Name of an aggregate node. |
| sourceName | string | Required. Name of the source node. |

## BatchCalcJob​AggregateField

Represents a collection of fields relating to an aggregation field in an aggregate node
of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| aggregateFunction | BatchCalcJobAggregateFunction (enumeration of type string) | Required. Function used for aggregation. Valid values are:   - `Unique`—A count of unique values. - `Sum`—The sum of all values. - `Max`—The largest value. - `Min`—The smallest value. - `Avg`—The average value, calculated as the   mean. - `Std`—The standard deviation. - `Stdp`—A standard deviation with population   variance. - `Var`—The variance. - `VarP`—The variance with population. - `Count`—The total count of values. |
| alias | string | Required. Name that subsequent nodes within the data processing engine use to refer to the aggregate field. |
| sourceFieldName | string | Required. Source node field on which the aggregate is calculated. |

## BatchCalcJobAtomicWriteback

Represents a node in a DPE definition that stores the details about the relationship
between the writeback nodes and the composite writeback operations between the nodes.

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | Description of the composite writeback object. |
| label | string | Required. Name of the composite writeback object. |
| name | string | Required. API name of the composite writeback object. |
| writebackObject​Relationships | [BatchCalcJobAtomicWritebackRelationship](#BatchCalcJobAtomicWritebackRelationship)[] | Specifies the relationship between the writeback objects that are involved in the writeback operation. |
| writebackSequence | int | Sequence in which the data processing engine executes the composite write back node. |

## BatchCalcJobAtomicWritebackRelationship

Represents the relationships between the writeback objects that are involved in a composite
writeback operation. It captures the relationships between these objects and the sequence in
which they should be processed.

| Field Name | Field Type | Description |
| --- | --- | --- |
| childWriteback​ObjectField | string | Field name that's associated with the child writeback object in a composite writeback relationship. Available in API version 63.0 and later. |
| childWriteback​ObjectName | string | Name of the child writeback object that's associated with the writeback relationship. |
| parentWriteback​ObjectField | string | Field name that's associated with the parent writeback object in a composite writeback relationship. Available in API version 63.0 and later. |
| parentWriteback​ObjectName | string | Required. Name of the parent writeback object that's associated with the writeback relationship. |
| relationshipName | string | Describes the relationship between the child and parent writeback objects in a composite writeback node. Available in API version 64.0 and later. |
| sequenceNumber | int | Sequence number of the writeback node that's associated with its parent node in the relationship. |

## BatchCalcJob​​​CustomNode

Represents a collection of custom nodes in a data processing engine. Use a custom node
to add a custom action.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | Description of a custom node. |
| extensionName | string | Required. Name of an extension node. |
| extensionNamespace | string | Required. Namespace of an extension node. |
| label | string | Required. Label of a custom node. |
| name | string | Required. Name of a custom node. |
| parameters | [BatchCalcJob​​​CustomNodeParameter](#bcjcustomnodeparameterID)[] | The field mappings of an extension node. |
| sources | string[] | Sources of an extension node. |

## BatchCalcJob​​​CustomNodeParameter

Represents the field mappings of an extension node.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| name | string | Required. Name of a parameter. |
| value | string | Required. Value of a parameter. |

## BatchCalcJob​Datasource

Represents a collection of fields relating to a data source node in a data processing
engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| CSVDelimiter | ​BatchCalcJobCSVDelimiter (enumeration of type string) | Specifies the field separator to read fields from a CSV file record. Possible values are:   - `COMMA` - `BACKQUOTE` - `CARET` - `PIPE` - `SEMICOLON` - `TAB`   The default value is `COMMA`.  The same delimiter value used for the CSV file can’t be used within any of the column values in the file. If you mistakenly use the same delimiter value in column values, it can cause data parsing issues. |
| description | string | Description of a data source node. |
| fields | [BatchCalcJob​DatasourceField](#bcjdatasourcefieldID)[] | Required. Collection of data source fields. |
| fileIdentifier | string | Specifies the source of the file or file storage system. |
| filePath | string | The file path for the specified file. |
| fileSource | BatchCalcJobFileSource (enumeration of type string) | Specifies the source of the file or file storage system. Possible value is:   - `ContentManagement` |
| label | string | Required. Label of a data source node. |
| name | string | Required. Name of a data source node. |
| parentDataSource | string | Name of the parent data source node. Available in API version 67.0 and later. |
| sourceName | string | Required. Name of a standard or custom object from which the data source node extracts data. |
| type | BatchCalcJobDataSource​Type (enumeration of type string) | Required. Type of object for the source object field. Supported values are:  - `Analytics` - `CalculatedInsightsObject` - `Context`—Available in API version 67.0 and   later. - `CRMObject` - `CSV` - `DataLakeObject` - `DataModelObject` - `StandardObject`  . |

## BatchCalcJob​DatasourceField

Represents a collection of fields relating to a source object field that are selected
in the data source node of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| alias | string | Name that subsequent nodes within the data processing engine use to refer to the data source field. Required when the field name is lookup. |
| dataType | BatchCalcJobDataType (enumeration of type string) | Specifies the data type of the input field when using a CSV file as a data source. Possible values are:   - `Boolean`—Available in API version   65.0 and later. - `Date` - `DateTime` - `MultiValue` - `Numeric` - `Text` |
| isPrimaryKey | boolean | Indicates whether a column name is the primary key (`true`) or not (`false`) for the Data Cloud CSV file. |
| name | string | Required. Name of the field. Can be either of the following:  - Name of the source field selected in the associated data source object. - Name from a nested lookup object with three child levels. |

## BatchCalcJobFilter

Represents a collection of fields relating to a filter node in a data processing
engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| criteria | [BatchCalcJobFilter​Criteria](#bcjfiltercriteriaID)[] | Collection of filter criteria in a filter node. The field is required when `isDynamicFilter` is set to `False`. |
| description | string | Description of the batch calculation job filter. |
| filterCondition | string | Logic that is specified to apply the filter conditions. The field is required when `isDynamicFilter` is set to `False`. |
| filterParameterName | string | Name of the parameter of type filter. |
| isDynamicFilter | boolean | Indicates whether the filter criteria is dynamic. If value is set to `True`, filter criteria is passed in runtime with `filterParameterName`. |
| label | string | Required. Label of the filter node. |
| name | string | Required. Name of the filter node. |
| sourceName | string | Required. Name of the source node. |

## BatchCalcJobForecast

Represents a collection of fields relating to a forecast node in a data processing
engine. Available in API version 58.0 and later.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| accuracyPercent | BatchCalcJobFrcstAccuracy (enumeration of type string) | The interval percentage to account for errors in forecasts.  Possible values are:   - `Eighty` - `NinetyFive` - `None`   The default value is `None`. |
| aggregationFields | [BtchCalcJobFrcstAggrFld[]](#BtchCalcJobFrcstAggrFld) | The list of fields to forecast. |
| dateFieldName | string | Required. The date field from the source node used to forecast values for the specified forecast length. |
| description | string | The description of the forecast node. |
| forecastModelType | BatchCalcJobFrcstModel (enumeration of type string) | The model used to forecast data. Possible values are:   - `Additive` - `Auto` - `Multiplicative`   The default value is `Auto`. |
| forecastPeriodCount | int | The number of time periods to generate forecast data. For example, if you select Year-Month as the forecast period type, and 4 as the forecast period count, the forecast results are generated for the next 4 months. The minimum and the default count is 1, and the maximum is 100. |
| forecastPeriodType | BatchCalcJobFrcstPeriodType (enumeration of type string) | Required. The type of forecast period to group date field values in the forecast results.  Possible values are:   - `FiscalYear` - `FiscalYearMonth` - `FiscalYearQuarter` - `FiscalYearWeek` - `Year` - `YearMonth` - `YearMonthDay` - `YearQuarter` - `YearWeek` |
| groupFields | [BatchCalcJobFrcstGrpFld[]](#BatchCalcJobFrcstGrpFld) | The source fields for grouping the data to be processed by the forecast node. |
| label | string | Required. The name of the forecast node in the UI. |
| name | string | Required. A unique name for the forecast node. |
| periodStartDateName | string | Required. The start date of the forecast period. |
| seasonality | BatchCalcJobFrcstSeasonality (enumeration of type string) | Represents the periodic fluctuations that occur around the same time every year.  Possible values are:   - `Two` - `Three` - `Four` - `Five` - `Six` - `Seven` - `Eight` - `Nine` - `Ten` - `Eleven` - `Twelve` - `Thirteen` - `Fourteen` - `Fifteen` - `Sixteen` - `Seventeen` - `Eighteen` - `Nineteen` - `Twenty` - `TwentyOne` - `TwentyTwo` - `TwentyThree` - `TwentyFour` - `Auto` - `None`   The default value is `None`. |
| shouldExcludeLastPeriod | boolean | Indicates whether to ignore the last period in the source node when it has incomplete data (`true`) or not (`false`). The default value is `false`. |
| sourceName | string | Required. The name of the source node.  A source can be any node other than the datasink and register node. |

## BtchCalcJobFrcstAggrFld

Represents a list of fields to forecast in a forecast node.

| Field Name | Field Type | Description |
| --- | --- | --- |
| aggregateFunction | BatchCalcJobAggregateFunction (enumeration of type string) | Required. The function of the aggregate field.  Possible values are:   - `Avg` - `Count` - `Max` - `Min` - `Std` - `StdP` - `Sum` - `Unique` - `Var` - `VarP` |
| aggregationResultLabel | string | Required. The name of the aggregation result generated from the aggregation function that’s applied to the source node field. |
| fieldName | string | Required. The name of the source field. |

## BatchCalcJobFrcstGrpFld

Represents source fields for grouping the data to be processed by the forecast node.

| Field Name | Field Type | Description |
| --- | --- | --- |
| fieldName | string | Required. The name of the source field to group the data to be processed by the forecast node. |
| groupBy | string | A comma-separated list of values to group data by. Required when the source field type is Date or DateTime.  Possible values are:   - `Second` - `Second Epoch` - `Minute` - `Hour` - `Day` - `Day Epoch` - `Week` - - `Month`   - `Quarter`   - `Year` |

## BatchCalcJobHierarchyPath

Represents a collection of hierarchy path nodes in a data processing engine
definition.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| aggregateFields | [BatchCalcJobHierarchyPath​AggregateField](#bcjhierarchypathaggfieldID)[] | Collection of aggregate fields for the hierarchy path node. Available in API version 67.0 and later. |
| description | string | Description of the hierarchy path node. |
| hierarchyFieldName | string | Required. Field name that contains the hierarchy path. |
| isAggregationRequired | boolean | Indicates whether aggregation is required for the hierarchy path node (`true`) or not (`false`). Available in API version 67.0 and later. |
| isSelfFieldValueIncluded | boolean | Indicates whether the self value is included in the calculated hierarchy path (`True`) or not (`False`). |
| label | string | Required. Label of the hierarchy path node. |
| name | string | Required. Name of the hierarchy path node. |
| parentFieldName | string | Required. Parent field name to calculate hierarchy path. |
| rollupPercentageFieldName | string | Field name used for rollup percentage calculation in the hierarchy path. Available in API version 67.0 and later. |
| selfFieldName | string | Required. Self field name to calculate hierarchy path. |
| sourceName | string | Required. Name of the source node. |

## BatchCalcJobHierarchyPath​AggregateField

Represents a collection of fields relating to an aggregation field in a hierarchy path
node of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| aggregateFunction | BatchCalcJobAggregateFunction (enumeration of type string) | Required. Function used for aggregation in the hierarchy path. Valid values are:   - `Unique` - `Sum` - `Max` - `Min` - `Avg` - `Std` - `Stdp` - `Var` - `VarP` - `Count`   Available in API version 67.0 and later. |
| alias | string | Required. Name that subsequent nodes within the data processing engine use to refer to the aggregate field. Available in API version 67.0 and later. |
| sourceFieldName | string | Required. Source node field on which the aggregate is calculated. Available in API version 67.0 and later. |

## BatchCalcJobFilter​Criteria

Represents a collection of fields relating to a filter condition in a filter node in a
data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| inputVariable | string | Name of the input variable used as a filter. |
| operator | BatchCalcJobFilter​Operator (enumeration of type string) | Required. Operator that is specified in the filter condition. Valid values are:   - `Equals` - `NotEquals` - `GreaterThan` - `GreaterThanOrEqual` - `LessThan` - `LessThanOrEqual` - `StartsWith` - `EndsWith` - `Contains` - `DoesNotContain` - `IsNull` - `IsNotNull` - `In` - `NotIn` |
| sequence | integer | Required. Sequence number used to refer the criteria in a filter node. |
| sourceFieldName | string | Required. Name of the field from the source node to apply the filter. |
| value | string | Value used to filter data from the source node. |

## BatchCalcJobParameter

Represents a collection of fields relating to an input variable in a data processing
engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| dataType | BatchCalcJobParameter​DataType (enumeration of type string) | Required. Data type of the parameter. Valid values are:  - `Date` - `DateTime` - `Expression` - `FileIdentifier` - `Filter` - `Numeric` - `Text` |
| defaultValue | string | Default value of the parameter. |
| description | string | Description of the batch calculation job parameter. |
| isMultiValue | boolean | Indicates whether the parameter has different values (`True`) or not (`False`). This field is supported only for the `Text` data type. |
| label | string | Required. Label of the batch calculation job parameter. |
| name | string | Required. Name of the batch calculation job parameter. |

## BatchCalcJobSource​Join

Represents a collection of fields relating to a join node in a data processing
engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | Description of the join node. |
| fields | [BatchCalcJobJoin​ResultField](#bcjjoinresultfieldID)[] | Collection of fields in a join node. |
| hasLookUpMultipleValues | boolean | Indicates whether the lookup join returns multiple values (`true`) or not (`false`). Available in API version 67.0 and later. |
| joinKeys | [BatchCalcJobJoin​Key](#bcjjoinkeyID)[] | Collection of mapping of fields from the primary source node and the second source node in a join node. |
| label | string | Required. Label of the join node. |
| name | string | Required. Name of the join node. |
| primarySourceName | string | Required. Name associated with the node as the primary source node. |
| secondarySourceName | string | Required. Name associated with the node as the secondary source node. |
| type | BatchCalcJobSource​JoinType (enumeration of type string) | Required. Type of join specified between the primary source node and secondary source node. Valid values are:  - `LeftOuter` - `RightOuter` - `Inner` - `Outer` - `Lookup` |

## BatchCalcJobJoin​Key

Represents a collection of fields relating to a mapping of fields from the first source
node and second source node in a join node of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| primarySourceFieldName | string | Required. Mapped field name of the primary source node. |
| secondarySourceFieldName | string | Required. Mapped field name of the secondary source node. |

## BatchCalcJobJoin​ResultField

Represents a collection of fields relating to a set of resultant fields in a join node
of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| alias | string | Required. Name that subsequent nodes within the data processing engine definition use to refer to the resultant field. |
| sourceFieldName | string | Required. Name of field from the primary or secondary data source. |
| sourceName | string | Required. Source node of the primary or secondary data source. |

## BatchCalcJobTransform

Represents a collection of fields relating to a data transformation in a data
processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | The description of the batch calculation job transform. |
| droppedFields | [BatchCalcJobTransform​DroppedField](#bcjtransformdroppedfieldID)[] | The collection of dropped fields in a data transformation. Available when the transformation type is `Slice`. |
| expressionFields | [BatchCalcJobTransform​AddedField](#bcjtransformaddedfieldID)[] | The collection of formula fields in a data transformation. Available when the transformation type is `Expression`. |
| label | string | Required. The label of the batch calculation job transform. |
| name | string | Required. The name of the batch calculation job transform. |
| orderBy | [BatchCalcJobOrderByField](#bcjorderbyfieldID)[] | A collection of fields that’s used to sort the records within each partition group. |
| partitionBy | string[] | A group of fields that’s used to partition the source data into partition groups. |
| sourceName | string | Required. Name of the source node. |
| transformType | BatchCalcJobTransform​Type (enumeration of type string) | Required. The type of transformation. Valid values are:   - `ComputeRelative—`This transformation   calculates values based on values of the same partition group. - `Expression`—This transformation calculates   values based on existing values of fields in the same record. - `Slice`—This transformation removes fields   from the source node. |

## BatchCalcJobTransform​DroppedField

Represents a collection of fields relating to a dropped field in a data transformation
of a data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| sourceFieldName | string | Required. Name of the field that is dropped. |

## BatchCalcJobTransform​AddedField

Represents a collection of fields relating to a formula in a data transformation of a
data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| alias | string | Required. Name that subsequent nodes within the data processing engine use to the transform node. |
| dataType | BatchCalcJobDataType (enumeration of type string) | Required. Data type of the formula. Valid values are:   - `Boolean`—Available in API version   65.0 and later. - `Date` - `DateTime` - `MultiValue` - `Numeric` - `Text` |
| decimalPlaces | integer | Number of digits to the right of a decimal point in the value. Required for the `Numeric` data type. |
| expression | string | Required. Formula defined by the user. |
| length | integer | Total length of the value including the decimal places. Required for data types: `Text` and `Numeric`. |

## BatchCalcJobOrderByField

Represents a collection of fields that are used to sort the partitioned data.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| name | string | Required. Name of the field that is used to sort data. |
| orderType | BatchCalcJobOrderType(enumeration of type string) | Order in which the data is sorted. Valid values are:   - Ascending - Descending |

## BatchCalcJobUnion

Represents a collection of fields relating to the union of data from two nodes in a
data processing engine.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| description | string | Description of the batch calculation job union. |
| isDisjointedSchema | boolean | Indicates whether the union is of two disjointed datasets (`true`) or not (`false`). Set to `True` to allow joining of two datasets having no common fields. |
| label | string | Required. Label of the batch calculation job union. |
| name | string | Required. Name of the batch calculation job union. |
| sources | string[] | Names of the source nodes. |

## BatchCalcJobWriteback​Object

Represents a collection of fields relating to the object in which the results of the
data processing engine are written back.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| canWrtbckToNonEditableFields | boolean | Indicates whether the non-editable fields are included in field mapping when the action type is upsert. The default value is `false`. Available in API version 64.0 and later. |
| description | string | Descriptions of the batch calculation job writeback object. |
| externalId​FieldName | string | Unique external field ID for the target object name. Available in API version 60.0 and later. |
| fields | [BatchCalcJobWriteback​Mapping](#bcjwritebackmappingID)[] | Collection of the writeback fields. |
| filterCondition | string | The condition that filters the records from a writeback dataset for a user. Examples of a filter condition include a user ID, stage name, and a security policy that returns only the records that a user owns. Available in API version 57.0 and later. |
| folderName | string | The folder where the writeback dataset is saved. Available in API version 57.0 and later. |
| groupBy | string | Reserved for future use. |
| isChangedRow | boolean | Indicates whether a row in the write back object is changed. Set to `True` to write back the changed rows. |
| isExistingDataset | boolean | Indicates whether a CRM Application (CRMA) dataset or a Data 360 Data Lake object is present (`true`) or will be created (`false`). Available in API version 62.0 and later. |
| jsonStructureType | string | JSON structure type for the writeback object. Available in API version 67.0 and later. |
| label | string | Required. Name of the write back object. |
| name | string | Required. Name of the batch calculation job write back object. |
| operationType | BatchCalcJobWriteback​Opn (enumeration of type string) | Type of operation specified. Valid values are:   - `Delete`—This value is available in API   version 56.0 and later. - `Insert` - `Overwrite`—Available only when   storageType is `DataLakeObject`. This value is available in API version 60.0 and   later. - `Update` - `Upsert` |
| sharingInheritanceObjectName | string | The name of the source object from which the row-level sharing inheritance settings are applied. Available in API version 57.0 and later. |
| shouldCreateTargetObject | boolean | Indicates whether target Data Lake Object or Salesforce Object is created in Salesforce (`true`) or not (`false`). Available in API version 65.0 and later. |
| shouldMngRow​LockFor​GroupedRec | boolean | Reserved for future use. |
| sourceName | string | Required. Name of the source node associated with the write back object. |
| storageType | BatchCalcJobWriteback​Type (enumeration of type string) | Specifies where you want to use the data stored in the source node. Available in API version 57.0 and later. Valid values are:   - `Analytics` - `DataLakeObject` - `sObject`   The default value is `sObject`. |
| targetObjectName | string | Required. Object that is inserted or upserted by the data processing engine. |
| targetObjectCategory | string | Category of the target object for the writeback operation. Available in API version 67.0 and later. |
| writebackSequence | integer | Sequence in which the target object is updated by the data processing engine. |
| writebackUser | string | ID of the user whose permissions decide which objects and fields of the target object can be updated. |

## BatchCalcJobWriteback​Mapping

Represents a collection of fields relating to the mapping between results and the
fields in the target object.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| fieldType | string | Target field type on the writeback object. Valid values are:  - `EventTimeField`—Available in API version   67.0 and later. - `ParentRecordIdentifierField`—Available in   API version 67.0 and later. - `PrimaryKey` - `QualifierKey` - `RecordIdentifierField`—Available in API   version 67.0 and later.   Available in API version 64.0 and later. |
| isAutogenerated | boolean | Indicates whether the target field value on the writeback object is autogenerated (`true`) or not (`false`). Available in API version 64.0 and later. |
| parentName | string | Name of the lookup object. Required only when the `relationshipName` field is defined. |
| relationshipName | string | Name of the lookup relationship. |
| runtimeParameter | boolean | Indicates whether the source field from runtime parameter is `true` or `false`. The default value is `false`. Available in API version 59.0 and later. |
| sourceFieldName | string | Required. Name of the field in the source node that is written back. |
| targetFieldName | string | Name of the sObject field to which the results are written back. |

## Declarative Metadata Sample Definition

The following is an example of a BatchCalcJobDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<BatchCalcJobDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <aggregates>
        <description>Aggregate Description</description>
        <fields>
            <aggregateFunction>Count</aggregateFunction>
            <alias>NameCount</alias>
            <sourceFieldName>Name</sourceFieldName>
        </fields>
        <groupBy>ContactId</groupBy>
        <groupBy>Name</groupBy>
        <label>AggregateOpportunities</label>
        <name>AggregateOpportunities</name>
        <sourceName>Opportunity</sourceName>
    </aggregates>
    <forecasts>
        <description>ForecastNode Description</description>
        <label>ContactForecast</label>
        <name>ContactForecast</name>
        <sourceName>Contact</sourceName>
        <dateFieldName>CreatedDate</dateFieldName>
        <forecastPeriodType>YearMonth</forecastPeriodType>
        <shouldExcludeLastPeriod>false</shouldExcludeLastPeriod>
        <forecastPeriodCount>12</forecastPeriodCount>
        <periodStartDateName>CreatedDateYM</periodStartDateName>
        <forecastModelType>Auto</forecastModelType>
        <seasonality>None</seasonality>
        <accuracyPercent>None</accuracyPercent>
        <aggregationFields>
            <aggregateFunction>Count</aggregateFunction>
            <aggregationResultLabel>CountOfLastName</aggregationResultLabel>
            <fieldName>LastName</fieldName>
        </aggregationFields>
        <groupFields>
            <fieldName>LastModifiedDate</fieldName>
            <groupBy>Week</groupBy>
        </groupFields>
    </forecasts>
    <appends>
        <description>Append desc</description>
        <isDisjointedSchema>true</isDisjointedSchema>
        <label>AppendAllAccounts</label>
        <name>AppendAllAccounts</name>
        <sources>AccountsOfManufacturingIndustry</sources>
        <sources>ComputeRelativeManufacturingIndustry</sources>
    </appends>
    <datasources>
        <description>Desc Contact</description>
        <fields>
            <alias>Id</alias>
            <name>Id</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Text</dataType>
        </fields>
        <fields>
            <alias>LastName</alias>
            <name>LastName</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Text</dataType>
        </fields>
        <fields>
            <alias>CreatedDate</alias>
            <name>CreatedDate</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Date</dataType>
        </fields>
        <fields>
            <alias>LastModifiedDate</alias>
            <name>LastModifiedDate</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Date</dataType>
        </fields>
        <label>Contact</label>
        <name>Contact</name>
        <sourceName>Contact</sourceName>
        <type>StandardObject</type>
        <fileSource>ContentManagement</fileSource>
        <fileIdentifier>069xx0000004CAeAAM</fileIdentifier>
        <CSVDelimiter>COMMA</CSVDelimiter>
        <filePath>parentFolder/childFolder</filePath>
    </datasources>
    <datasources>
        <fields>
            <alias>Name</alias>
            <name>Name</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Text</dataType>
        </fields>
        <fields>
            <alias>ContactId</alias>
            <name>ContactId</name>
            <isPrimaryKey>false</isPrimaryKey>
            <dataType>Text</dataType>
        </fields>
        <label>Opportunity</label>
        <name>Opportunity</name>
        <sourceName>Opportunity</sourceName>
        <type>StandardObject</type>
        <fileSource>ContentManagement</fileSource>
        <fileIdentifier>069xx0000004CAeAAM</fileIdentifier>
        <CSVDelimiter>COMMA</CSVDelimiter>
        <filePath>parentFolder/childFolder</filePath>
    </datasources>
    <description>Calculates and creates transaction journal records based on the orders placed by the loyalty program members. The transaction journals are used to accrue points to the member.</description>
    <filters>
        <criteria>
            <operator>Equals</operator>
            <sequence>1</sequence>
            <sourceFieldName>LastName</sourceFieldName>
            <value>Salesforce</value>
        </criteria>
        <description>Filter Desc</description>
        <filterCondition>1</filterCondition>
        <isDynamicFilter>false</isDynamicFilter>
        <label>AccountsOfManufacturingIndustry</label>
        <name>AccountsOfManufacturingIndustry</name>
        <sourceName>AccountOpportunities</sourceName>
    </filters>
    <hierarchyPaths>
        <description>Hierarchy Path Node</description>
        <hierarchyFieldName>Hierarchy_Path</hierarchyFieldName>
        <isAggregationRequired>true</isAggregationRequired>
        <isSelfFieldValueIncluded>true</isSelfFieldValueIncluded>
        <label>Get Hierarchy</label>
        <name>Get_Hierarchy</name>
        <parentFieldName>ContactId</parentFieldName>
        <selfFieldName>LastName</selfFieldName>
        <sourceName>AppendAllAccounts</sourceName>
        <aggregateFields>
            <aggregateFunction>Count</aggregateFunction>
            <aggregationFieldName>*</aggregationFieldName>
            <aggregateFieldAliasName>CountOfLastName</aggregateFieldAliasName>
        </aggregateFields>
    </hierarchyPaths>
    <isTemplate>false</isTemplate>
    <executionPlatformObjectType>None</executionPlatformObjectType>
    <joins>
        <description>Left Outer Join</description>
        <fields>
            <alias>ContactId</alias>
            <sourceFieldName>Id</sourceFieldName>
            <sourceName>Contact</sourceName>
        </fields>
        <fields>
            <alias>LastName</alias>
            <sourceFieldName>LastName</sourceFieldName>
            <sourceName>Contact</sourceName>
        </fields>
        <fields>
            <alias>NameCount</alias>
            <sourceFieldName>NameCount</sourceFieldName>
            <sourceName>AggregateOpportunities</sourceName>
        </fields>
        <fields>
            <alias>OpportunityName</alias>
            <sourceFieldName>Name</sourceFieldName>
            <sourceName>AggregateOpportunities</sourceName>
        </fields>
        <joinKeys>
            <primarySourceFieldName>Id</primarySourceFieldName>
            <secondarySourceFieldName>ContactId</secondarySourceFieldName>
        </joinKeys>
        <label>AccountOpportunities</label>
        <name>AccountOpportunities</name>
        <primarySourceName>Contact</primarySourceName>
        <secondarySourceName>AggregateOpportunities</secondarySourceName>
        <type>LeftOuter</type>
    </joins>
    <label>Create Transaction Journals Based on Orders</label>
    <parameters>
        <dataType>Date</dataType>
        <defaultValue>2020-01-01</defaultValue>
        <description>Desc TextParameter</description>
        <isMultiValue>false</isMultiValue>
        <label>DateParameter</label>
        <name>DateParameter</name>
    </parameters>
    <parameters>
        <dataType>Filter</dataType>
        <defaultValue>{&quot;filterCondition&quot;: &quot;1 AND 2&quot;, &quot;criteria&quot;: [{&quot;sourceFieldName&quot;: &quot;NameCount&quot;,&quot;operator&quot;: &quot;GreaterThan&quot;,&quot;value&quot;: &quot;20&quot;,&quot;sequence&quot;: &quot;1&quot;}, {&quot;sourceFieldName&quot;: &quot;Name&quot;,&quot;operator&quot;: &quot;Equals&quot;,&quot;value&quot;: &quot;Salesforce&quot;,&quot;sequence&quot;: &quot;2&quot;}]}</defaultValue>
        <isMultiValue>false</isMultiValue>
        <label>FilterParameter</label>
        <name>FilterParameter</name>
    </parameters>
    <parameters>
        <dataType>Numeric</dataType>
        <defaultValue>5000</defaultValue>
        <description>Desc TextParameter</description>
        <isMultiValue>false</isMultiValue>
        <label>NumericParameter</label>
        <name>NumericParameter</name>
    </parameters>
    <parameters>
        <dataType>Text</dataType>
        <defaultValue>@salesforce.com</defaultValue>
        <description>Desc TextParameter</description>
        <isMultiValue>false</isMultiValue>
        <label>TextParameter</label>
        <name>TextParameter</name>
    </parameters>
    <processType>Rebates</processType>
    <definitionRunMode>Batch</definitionRunMode>
    <status>Inactive</status>
    <transforms>
        <description>transforms Desc</description>
        <expressionFields>
            <alias>NewLastName</alias>
            <dataType>Text</dataType>
            <expression>TODAY()</expression>
            <length>80</length>
        </expressionFields>
        <label>ManufacturingIndustry</label>
        <name>ManufacturingIndustry</name>
        <sourceName>AccountsOfManufacturingIndustry</sourceName>
        <transformationType>Expression</transformationType>
    </transforms>
    <transforms>
        <droppedFields>
            <sourceFieldName>NewLastName</sourceFieldName>
        </droppedFields>
        <label>MediaIndustry</label>
        <name>MediaIndustry</name>
        <sourceName>ManufacturingIndustry</sourceName>
        <transformationType>Slice</transformationType>
    </transforms>
    <transforms>
        <description>compute relative transforms Desc</description>
        <expressionFields>
            <alias>NewLastName</alias>
            <dataType>Text</dataType>
            <expression>rank()</expression>
            <length>80</length>
        </expressionFields>
        <label>ComputeRelativeManufacturingIndustry</label>
        <name>ComputeRelativeManufacturingIndustry</name>
        <orderBy>
            <name>LastName</name>
            <orderType>Ascending</orderType>
        </orderBy>
        <partitionBy>LastName</partitionBy>
        <sourceName>MediaIndustry</sourceName>
        <transformationType>ComputeRelative</transformationType>
    </transforms>
    <customNodes>
        <name>RebatesCustomNode</name>
        <label>Rebates Custom Node</label>
        <description>customNodes Desc</description>
        <sources>Get_Hierarchy</sources>
        <extensionName>RebatesExpression</extensionName>
        <extensionNamespace>industries_mfg</extensionNamespace>
        <parameters>
            <name>inputColumn</name>
            <value>LastName</value>
        </parameters>
        <parameters>
            <name>isFilterCriteria</name>
            <value>true</value>
        </parameters>
        <parameters>
            <name>outputColumn</name>
            <value>GenName</value>
        </parameters>
    </customNodes>
    <writebacks>
        <fields>
            <sourceFieldName>GenName</sourceFieldName>
            <targetFieldName>LastName</targetFieldName>
        </fields>
        <isChangedRow>false</isChangedRow>
        <label>exportToContact</label>
        <name>exportToContact</name>
        <description>Export To Contact</description>
        <operationType>Insert</operationType>
        <sourceName>RebatesCustomNode</sourceName>
        <targetObjectName>Contact</targetObjectName>
        <writebackSequence>1</writebackSequence>
        <canWrtbckToNonEditableFields>false</canWrtbckToNonEditableFields>
    </writebacks>
    <writebacks>
        <fields>
            <sourceFieldName>CreatedDateYM</sourceFieldName>
            <targetFieldName>CreatedDate</targetFieldName>
        </fields>
        <isChangedRow>false</isChangedRow>
        <isExistingDataset>false</isExistingDataset>
        <label>exportToContactFC</label>
        <name>exportToContactFC</name>
        <description>Export To Contact</description>
        <operationType>Insert</operationType>
        <sourceName>ContactForecast</sourceName>
        <targetObjectName>Contact</targetObjectName>
        <writebackSequence>2</writebackSequence>
        <canWrtbckToNonEditableFields>false</canWrtbckToNonEditableFields>
    </writebacks>
</BatchCalcJobDefinition>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<!--
   ~ Copyright 2020 Salesforce, Inc.
   ~ All Rights Reserved
   ~ Company Confidential
-->
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
   <types>
      <members>*</members>
      <name>BatchCalcJobDefinition</name>
   </types>
   <version>60.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest
file. For information about using the manifest file, see Deploying and Retrieving Metadata with the Zip File.
