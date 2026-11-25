---
page_id: meta.datamapperdefinition
title: DataMapperDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.datamapperdefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
fetched_at: 2026-11-25
---

# DataMapperDefinition

Represents a Data Mapper’s header configurations, such as its name and type. Data Mappers transfer and transform data between Salesforce and Omnistudio components. They act as data sources in Flexcards and as actions in Omniscripts.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

DataMapperDefinition components have the suffix `.dataMapperDefinition` and are stored in the `dataMapperDefinitions` folder.

## Version

DataMapperDefinition components are available in API version 67.0 and later.

## Special Access Rules

## Fields

### batchSize

- **Field Type**: double

- **Description**: The number of items to process in a batch action. You can add any value up to 2000.

### cleanResponseCacheType

- **Field Type**: CleanResponseCacheType

- **Description**: Specifies the cache type used to store response data for this definition.

### dataMapperDefinitionItem

- **Field Type**: [DataMapperDefinitionItem](#datamapperdefinitionitem)

- **Description**: The configuration of a component inside a Data Mapper.

### description

- **Field Type**: string

- **Description**: The description added to the Data Mapper.

### expectedInputJson

- **Field Type**: string

- **Description**: The sample input JSON format to assist the user with Data Mapper configuration, such as providing auto complete options.

### expectedInputOtherData

- **Field Type**: string

- **Description**: The expected custom input payload format to assist in the Data Mapper configuration when data must be transformed.

### expectedInputXml

- **Field Type**: string

- **Description**: The expected XML format of the input.

### expectedOutputJson

- **Field Type**: string

- **Description**: The sample output JSON format to assist the user with Data Mapper configuration in various ways, such as by providing auto complete options.

### expectedOutputOtherData

- **Field Type**: string

- **Description**: The sample output in a custom format to assist the user with Data Mapper configuration in various ways, such as by providing auto complete options.

### expectedOutputXml

- **Field Type**: string

- **Description**: The sample output XML format to assist the user with Data Mapper configuration in various ways, such as by providing auto complete options.

### globalKey

- **Field Type**: string

- **Description**: The globally unique identifier of the Data Mapper definition. Use this identifier to identify the component across Salesforce orgs.

### inputParsingClassName

- **Field Type**: string

- **Description**: The custom Apex class used to deserialize input to support any serialization format.

### inputType

- 

**Field Type**: DataMapperInputType (enumeration of type string)

- 

**Description**: The format of the input data, such as JSON, XML, SObject, and so on.

- 

**Values**: Values are:

  - `JSON`

  - `XML`

  - `SObject`

  - `Custom`

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether this Data Mapper is currently active (`true`) or not (`false`).

### isAssignmentRulesUsed

- **Field Type**: boolean

- **Description**: Indicates whether Salesforce Assignment Rules must used (`true`) or not (`false`).

### isDeletedOnSuccess

- **Field Type**: boolean

- **Description**: Indicates whether bulk records must be deleted after being successfully processed on bulk-loading (`true`) or not (`false`).

### isErrorIgnored

- **Field Type**: boolean

- **Description**: Indicates whether the Data Mapper definition must continue processing if there are errors (`true`) or not (`false`).

### isFldLevelSecurityEnabled

- **Field Type**: boolean

- **Description**: Indicates whether the Data Mapper definition must check the user’s field-level access (`true`) or not (`false`).

### isManagedUsingStdDesigner

- **Field Type**: boolean

- **Description**: Indicates whether the Data Mapper is created or updated using the Omnistudio standard designer.

### isNullInpIncludedInOput

- **Field Type**: boolean

- **Description**: Indicates whether fields missing in the input (or null) must nullify the values in the record (`true`) or ignore the missing input and only update the fields that were provided in the input (`false`).

### isProcessSuperBulk

- **Field Type**: boolean

- **Description**: Indicates whether the Load Data Mapper processes the record upsert spread over multiple Salesforce Apex batch jobs (`true`) or not (`false`). Process Super Bulk is a Data Mapper property available if the Input Type is sObject. It helps process large jobs spread over multiple Salesforce Apex batch jobs without exceeding Salesforce governor limits.

### isRollbackOnError

- **Field Type**: boolean

- **Description**: Indicates whether the Data Mapper definition must continue executing if there’s an error (`false`) or not (`true`). Control whether the current transaction is rolled back and any records created up until the point of error are removed.

### isSourceObjectDefault

- **Field Type**: boolean

- **Description**: Indicates whether it is the default Data Mapper definition setting for the specified Interface Object (`true`) or not (`false`).

### isXmlDeclarationRemoved

- **Field Type**: boolean

- **Description**: Indicates whether the XML header declaration must be removed (`true`) or not (`false`).

### masterLabel

- **Field Type**: string

- **Description**: The user-defined label of the component.

### outputParsingClassName

- **Field Type**: string

- **Description**: The unique identifier of the custom Apex class that’s used to deserialize the output to support any serialization format.

### outputType

- 

**Field Type**: DataMapperOutputType (enumeration of type string)

- 

**Description**: The data format or object used in the output, such as JSON, XML, SObejct, PDF, or Document.

- 

**Values**: Values are:

  - `JSON`

  - `XML`

  - `SObject`

  - `PDF`

  - `Custom`

  - `DocuSign`

### overrideKey

- **Field Type**: string

- **Description**: The unique identifier of the Data Mapper that’s being overriden.

### preprocessorClassName

- **Field Type**: string

- **Description**: The custom Apex class name to be executed before the Data Mapper definition is triggered.

### previewJsonData

- **Field Type**: string

- **Description**: The preview of the Data Mapper’s JSON with the existing input data.

### previewOtherData

- **Field Type**: string

- **Description**: The custom content in the Data Mapper’s preview, when an input is added while previewing.

### previewSourceObjectData

- **Field Type**: string

- **Description**: The source object record in the Data Mapper’s preview when an input is added while previewing.

### previewXmlData

- **Field Type**: string

- **Description**: The XML content in the Data Mapper’s preview, when an input is added while previewing.

### references

- **Field Type**: string

- **Description**: The list of referenced components used by this definition.

### requiredPermission

- **Field Type**: string

- **Description**: The list of custom permissions that allow a user to execute the Data Mapper definition.

### responseCacheTtlMinutes

- **Field Type**: double

- **Description**: The number of minutes the Data Mapper Definition response must stay in the cache.

### sourceObject

- **Field Type**: string

- **Description**: The sObject used as an input in a Load Data Mapper.

### synchronousProcessThreshold

- **Field Type**: double

- **Description**: The foreign key to the Apex class the Data Mapper Definition references.

### targetOutputDocIdentifier

- **Field Type**: string

- **Description**: The envelope ID of a document template when using DocuSign.

### targetOutputFileName

- **Field Type**: string

- **Description**: The document name that receives the output of the Data Mapper Definition.

### type

- 

**Field Type**: DataMapperType (enumeration of type string)

- 

**Description**: Specifies the category or type of this component.

- 

**Values**: Values are:

  - `Extract`

  - `Load`

  - `Transform`

### xmlOutputTagsOrder

- **Field Type**: string

- **Description**: The XML tag sequence to be used in the output.

## DataMapperDefinitionItem

### dataMapperDefItemName

- **Field Type**: string

- **Description**: The name of a specific item within a Data Mapper.

### dataMapperDefinitionName

- **Field Type**: string

- **Description**: The name of the Data Mapper that this item belongs to.

### defaultValue

- **Field Type**: string

- **Description**: The user-defined value for the Default Value field, entered when completing the output mappings.

### filterDataType

- 

**Field Type**: DMItemFilterDataType (enumeration of type string)

- 

**Description**: The field data type used in a Data Mapper Turbo definition.

- 

**Values**: Values are:

  - `ADDRESS`

  - `ANYTYPE`

  - `BASE64`

  - `BOOLEAN`

  - `COMBOBOX`

  - `CURRENCY`

  - `DATACATEGORY`

  - `GROUPREFERENCE`

  - `DATE`

  - `DATETIME`

  - `DOUBLE`

  - `EMAIL`

  - `ENCRYPTEDSTRING`

  - `ID`

  - `INTEGER`

  - `LONG`

  - `MULTIPICKLIST`

  - `PERCENT`

  - `PHONE`

  - `PICKLIST`

  - `REFERENCE`

  - `STRING`

  - `TEXTAREA`

  - `TIME`

  - `URL`

### filterGroup

- **Field Type**: double

- **Description**: An internal grouping of filter conditions used to process Data Mappers.

### filterOperator

- 

**Field Type**: DMItemFilterOperator (enumeration of type string)

- 

**Description**: The operator used in a filter in a Data Mapper.

- 

**Values**: Values are:

  - `EQUAL`

  - `NOTEQUAL`

  - `LESS`

  - `GRATER`

  - `LESS_OR_EQUAL`

  - `GRATER_OR_EQUAL`

  - `APPROX`

  - `LIKE`

  - `NOT_LIKE`

  - `INCLUDES`

  - `EXCLUDES`

  - `AND`

  - `OR`

  - `LIMIT`

  - `OFFSET`

  - `ORDER_BY`

  - `IN`

  - `IS_NULL`

### filterValue

- **Field Type**: string

- **Description**: The field used in a filter in a Data Mapper.

### formulaConverted

- **Field Type**: string

- **Description**: The Reverse Polish Notation (RPN) of the formula.

### formulaExpression

- **Field Type**: string

- **Description**: The user-defined formula entered into the Formula tab of the Data Mapper.

### formulaResultPath

- **Field Type**: string

- **Description**: The user-defined variable name used to store the output of the formula.

### formulaSequence

- **Field Type**: double

- **Description**: The order in which the formulas are executed.

### globalKey

- **Field Type**: string

- **Description**: The globally unique identifier of the Data Mapper definition to identify the component across Salesforce orgs.

### inputField

- **Field Type**: string

- **Description**: The field or variable path used while configuring inputs.

### inputObject

- **Field Type**: string

- **Description**: The object used to configure the input.

### inputObjectQuerySequence

- **Field Type**: double

- **Description**: The order in which the object in the input is queried and executed.

### isDisabled

- **Field Type**: boolean

- **Description**: Indicates whether the output must not be generated (`true`) or is active and must be generated (`false`).

### isRequiredForUpsert

- **Field Type**: boolean

- **Description**: Indicates whether the field is mandatory for the upsert (`true`) or not (`false`).

### isUpsertKey

- **Field Type**: boolean

- **Description**: Specifies that the field is a key for the object being loaded. The Data Mapper uses the value to determine whether it updates an existing record or inserts a new one.

### linkedField

- **Field Type**: string

- **Description**: The field name used to lookup another object in a Data Mapper Load.

### linkedObjectSequence

- **Field Type**: double

- **Description**: The order in which the associated object in a Data Mapper Load is executed.

### lookupByField

- **Field Type**: string

- **Description**: The field name used to look up a record in a Data Mapper Load output.

### lookupObject

- **Field Type**: string

- **Description**: The object name used to look up a record in a Data Mapper Load output.

### lookupReturnedField

- **Field Type**: string

- **Description**: The field name that must be returned and used in the Data Mapper Load output.

### outputCreationSequence

- **Field Type**: double

- **Description**: The order in which the output paths must be created.

### outputField

- **Field Type**: string

- **Description**: The field, node, or tag in the object used in the output path.

### outputFieldDataType

- **Field Type**: string

- **Description**: The data type of the field, node, or tag in the output path.

### outputObject

- **Field Type**: string

- **Description**: The name of the object used in the output path.

### valueMapping

- **Field Type**: string

- **Description**: The key-value pair JSON list used to convert output values into another value.

## Declarative Metadata Sample Definition

The following is an example of a DataMapperDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<DataMapperDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>TestDataMapperDefinition</fullName>
    <masterLabel>Test Data Mapper Definition</masterLabel>
    <batchSize>200</batchSize>
    <description>Test Data Mapper Definition for Metadata Gauntlet</description>
    <expectedInputJson>{"testInput":"value"}</expectedInputJson>
    <expectedInputOtherData></expectedInputOtherData>
    <expectedInputXml>&lt;test&gt;value&lt;/test&gt;</expectedInputXml>
    <expectedOutputJson>{"testOutput":"value"}</expectedOutputJson>
    <expectedOutputOtherData></expectedOutputOtherData>
    <expectedOutputXml>&lt;output&gt;value&lt;/output&gt;</expectedOutputXml>
    <globalKey>TestDataMapperDefinition_1</globalKey>
    <inputType>JSON</inputType>
    <isActive>true</isActive>
    <isAssignmentRulesUsed>false</isAssignmentRulesUsed>
    <isDeletedOnSuccess>false</isDeletedOnSuccess>
    <isErrorIgnored>false</isErrorIgnored>
    <isFldLevelSecurityEnabled>false</isFldLevelSecurityEnabled>
    <isManagedUsingStdDesigner>true</isManagedUsingStdDesigner>
    <isNullInpIncludedInOput>false</isNullInpIncludedInOput>
    <isProcessSuperBulk>false</isProcessSuperBulk>
    <isRollbackOnError>true</isRollbackOnError>
    <isSourceObjectDefault>false</isSourceObjectDefault>
    <isXmlDeclarationRemoved>false</isXmlDeclarationRemoved>
    <outputType>JSON</outputType>
    <overrideKey></overrideKey>
    <previewJsonData>{"preview":"data"}</previewJsonData>
    <previewOtherData></previewOtherData>
    <previewSourceObjectData></previewSourceObjectData>
    <previewXmlData></previewXmlData>
    <references>[]</references>
    <requiredPermission></requiredPermission>
    <cleanResponseCacheType>Session Cache</cleanResponseCacheType>
    <responseCacheTtlMinutes>0</responseCacheTtlMinutes>
    <sourceObject></sourceObject>
    <synchronousProcessThreshold>0</synchronousProcessThreshold>
    <targetOutputDocIdentifier></targetOutputDocIdentifier>
    <targetOutputFileName></targetOutputFileName>
    <type>Transform</type>
    <xmlOutputTagsOrder></xmlOutputTagsOrder>
    <dataMapperDefinitionItem>
        <dataMapperDefItemName>Item1</dataMapperDefItemName>
        <dataMapperDefinitionName>TestDataMapperDefinition</dataMapperDefinitionName>
        <defaultValue>defaultValue</defaultValue>
        <filterDataType>STRING</filterDataType>
        <filterGroup>1</filterGroup>
        <filterOperator>EQUAL</filterOperator>
        <filterValue>testFilter</filterValue>
        <formulaConverted></formulaConverted>
        <formulaExpression></formulaExpression>
        <formulaResultPath></formulaResultPath>
        <formulaSequence>1</formulaSequence>
        <globalKey>TestItem1_Key</globalKey>
        <inputField>inputFieldPath</inputField>
        <inputObject>Account</inputObject>
        <inputObjectQuerySequence>1</inputObjectQuerySequence>
        <isDisabled>false</isDisabled>
        <isRequiredForUpsert>false</isRequiredForUpsert>
        <isUpsertKey>false</isUpsertKey>
        <linkedField></linkedField>
        <linkedObjectSequence>0</linkedObjectSequence>
        <lookupByField></lookupByField>
        <lookupObject></lookupObject>
        <lookupReturnedField></lookupReturnedField>
        <outputCreationSequence>1</outputCreationSequence>
        <outputField>outputFieldPath</outputField>
        <outputFieldDataType>STRING</outputFieldDataType>
        <outputObject>Contact</outputObject>
        <valueMapping></valueMapping>
    </dataMapperDefinitionItem>
</DataMapperDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>DataMapperDefinition</name>
    </types>
    <version>[ftest]</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.datamapperdefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
