---
page_id: meta_decisionmatrixdefinition.htm
title: DecisionMatrixDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_decisionmatrixdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# DecisionMatrixDefinition

Represents a definition of a decision matrix.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

Before deploying a decision matrix or a decision matrix version to a target org,
review these [decision matrix migration considerations](https://help.salesforce.com/s/articleView?id=ind.decision_matrix_migration_considerations.htm&type=5&language=en_US "HTML (New Window)").

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

DecisionMatrixDefinition components have the suffix
.decisionMatrixDefinition and are stored in the
decisionMatrixDefinition folder.

## Version

DecisionMatrixDefinition components are available in API version 55.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  Describes a decision matrix definition. |
| groupKey | Field Type  string  Description  A key for grouping matrix rows in different versions, such as a geographic region or a product code. |
| label | Field Type  string  Description  Required.  The UI label of a decision matrix definition. |
| processType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  The process type that uses the expression set rule.  Valid values are:  - `Bre` - `GpaCalculation` - `InsuranceClaimProcessing`—Available   in API version 65.0 and later. - `ItServiceManagement`—Available in   API version 65.0 and later. - `PlanCostCalculation` - `RatingDiscovery` - `StudentInformationSystem`—Available   in API version 65.0 and later. - `StudentSuccess`  Note Note When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other usage types may be available to you depending on your industry solution and permission sets.  Available in API version 59.0 and later. |
| subGroupKey | Field Type  string  Description  A subgroup key for grouping matrix rows in different versions, such as a geographic region or a product code. For example, if the groupKey is `Country`, the subGroupKey can be `State` or `Province`. |
| type | Field Type  DecisionMatrixType (enumeration of type string)  Description  The type of a decision matrix.  Valid values are:  - `Grouped` - `Standard` |
| versions | Field Type  [DecisionMatrixDefinitionVersion](#DMDV)[]  Description  Represents an array of decision matrix version definitions in a decision matrix. This array must contain at least one version. |

## DecisionMatrixDefinitionVersion

Represents a definition of a decision matrix version.

| Field Name | Description |
| --- | --- |
| columns | Field Type  [DecisionMatrixDefinitionVersionColumn​​](#DMDVcolumn)[]  Description  Represents an array of columns in a decision matrix definition version. |
| decisionMatrixDefinition | Field Type  string  Description  The full name of a decision matrix version. |
| endDate | Field Type  dateTime  Description  The date until which a decision matrix definition version is available for use. |
| groupKeyValue | Field Type  string  Description  The value of the groupKey for a decision matrix definition version. For example, if the groupKey is `Country`, the groupKeyValue can be `United States`. |
| label | Field Type  string  Description  Required.  The UI label of a decision matrix definition version. |
| rank | Field Type  int  Description  The rank of the Decision Matrix Definition Version. When more than one enabled version matches a decision matrix call, and the start date time to end date time spans overlap, the version with the highest rank is chosen. Available in API version 64.0 and later. |
| startDate | Field Type  dateTime  Description  Required.  The date from when a decision matrix definition version is available for use. |
| status | Field Type  DecisionMatrixDefStatus (enumeration of type string)  Description  Required.  Specifies the status of a decision matrix definition version.  Valid values are:  - `Active` - `Draft` - `Inactive` - `InvalidDraft` - `Obsolete` |
| subGroupKeyValue | Field Type  string  Description  The value of the subgroup key for a decision matrix definition version. For example, if the subGroupKey is `State` or `Province`, the subGroupKeyValue can be `California`. |
| versionNumber | Field Type  int  Description  Required.  The version number of a decision matrix definition. |

## DecisionMatrixDefinitionVersionColumn​​

Represents a definition of a column in a decision matrix definition version.

| Field Name | Description |
| --- | --- |
| columnType | Field Type  DecisionMatrixColumnType (enumeration of type string)  Description  Required.  Specifies whether a column is for an input or output.  Valid values are:  - `Input` - `Output` |
| dataType | Field Type  DecisionMatrixDataType (enumeration of type string)  Description  Required.  The type of data that’s stored in a column.  Valid values are:  - `Boolean` - `Currency` - `Number` - `NumberRange` - `Percent` - `Text` - `TextRange` |
| displaySequence | Field Type  int  Description  Required.  Represents the position of a column in the column order. |
| isWildcardColumn | Field Type  boolean  Description  Required.  Specifies whether a column stores a wildcard value (`true`) or not (`false`).  The default value is `false`. |
| name | Field Type  string  Description  Required.  The full name of a decision matrix definition version column. |
| rangeValue | Field Type  string  Description  A list of values that define range boundaries. |
| wildcardValue | Field Type  string  Description  The wildcard value such as `ALL`. |

## Declarative Metadata Sample Definition

The following is an example of a DecisionMatrixDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DecisionMatrixDefinition
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<label>HealthCloudUM_ValidRegions</label>
	<type>Standard</type>
	<versions>
		<fullName>HealthCloudUM_ValidRegions_V1</fullName>
		<columns>
			<columnType>Input</columnType>
			<dataType>Text</dataType>
			<displaySequence>2</displaySequence>
			<isWildcardColumn>false</isWildcardColumn>
			<name>State</name>
		</columns>
		<columns>
			<columnType>Input</columnType>
			<dataType>Text</dataType>
			<displaySequence>1</displaySequence>
			<isWildcardColumn>false</isWildcardColumn>
			<name>City</name>
		</columns>
		<columns>
			<columnType>Output</columnType>
			<dataType>Boolean</dataType>
			<displaySequence>3</displaySequence>
			<isWildcardColumn>false</isWildcardColumn>
			<name>IsValid</name>
		</columns>
		<decisionMatrixDefinition>HealthCloudUM_ValidRegions</decisionMatrixDefinition>
		<label>HealthCloudUM_ValidRegions V1</label>
		<startDate>2022-05-02T13:04:06.000Z</startDate>
		<status>Draft</status>
		<versionNumber>1</versionNumber>
	</versions>
</DecisionMatrixDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>DecisionMatrixDefinition</name>
	</types>
	<version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based.htm "HTML (New Window)").
