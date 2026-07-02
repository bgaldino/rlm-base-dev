---
page_id: meta_omnidatatransform.htm
title: OmniDataTransform
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omnidatatransform.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniDataTransform

Represents the header configuration of a DataRaptor.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniDataTransform components have the suffix .omniDataTransform and are
stored in the OmniDataTransforms folder.

## Version

OmniDataTransform components are available in API version 54.0 and later.

## Special Access Rules

To use this metadata type, you must have an Omnistudio license and the Discovery
Framework feature enabled in your Salesforce org.

## Fields

| Field Name | Description |
| --- | --- |
| active | Field Type  boolean  Description  Indicates whether the omni data transformation is active (`true`) or not (`false`). The default value is `false`. |
| assignmentRulesUsed | Field Type  boolean  Description  Indicates whether Salesforce Assignment Rules must be used (`true`) or not (`false`). The default value is `false`. |
| deletedOnSuccess | Field Type  boolean  Description  Indicates whether bulk records must be deleted after successfully processed on bulk loading (`true`) or not (`false`). |
| description | Field Type  string  Description  The comment added in the Omni Data Transformation. |
| errorIgnored | Field Type  boolean  Description  Indicates whether the Omni Data Transformation must continue processing if there are errors (`true`) or not (`false`). |
| expectedInputJson | Field Type  string  Description  The expected JSON input payload format to assist in the Omni Data Transformation configuration. |
| expectedInputOtherData | Field Type  string  Description  The expected custom input payload format to assist in the Omni Data Transformation configuration. |
| expectedInputXml | Field Type  string  Description  The expected XML input payload format to assist in the Omni Data Transformation configuration. |
| expectedOutputJson | Field Type  string  Description  The expected JSON output payload format to assist in the Omni Data Transformation configuration. |
| expectedOutputOtherData | Field Type  string  Description  The expected custom output payload format to assist in the Omni Data Transformation configuration. |
| expectedOutputXml | Field Type  string  Description  The expected XML output payload format to assist in the Omni Data Transformation configuration. |
| fieldLevelSecurityEnabled | Field Type  boolean  Description  Indicates whether the Omni Data Transformation must check the user field-level access (`true`) or not (`false`). |
| inputParsingClass | Field Type  string  Description  Custom class that's used to deserialize input to support any serialization format. |
| inputType | Field Type  OmniDataTransformInputType (enumeration of type string)  Description  The data format in the input. Values are:   - `Custom` - `JSON` - `SObject` - `XML` |
| isManagedUsingStdDesigner | Field Type  boolean  Description  Indicates whether the Omni Data Transformation is managed using standard designer (`true`) or not (`false`). |
| name | Field Type  string  Description  Required.  The name that uniquely identifies a Omni Data Transformation. |
| namespace | Field Type  string  Description  The namespace associated with the omni data transformation record. |
| nullInputsIncludedInOutput | Field Type  boolean  Description  Indicates whether fields missing in the input (or null) must nullify the values in the record (`true`) or ignore the missing input and only update the fields that were provided in the input (`false`). |
| omniDataTransformItem | Field Type  [OmniDataTransformItem[]](#OmniDataTransformItem)  Description  The configuration of a component inside a DataRaptor. |
| outputParsingClass | Field Type  string  Description  Custom class that's used to serialize output to support any serialization format. |
| outputType | Field Type  string  Description  The data format or object that's used in the output (JSON, XML, SObejct, PDF, Document). |
| overrideKey | Field Type  string  Description  Reserved for future use. |
| preprocessorClassName | Field Type  string  Description  The Apex class name to be executed before the Omni Data Transformation (acting as a before insert trigger/process). |
| previewJsonData | Field Type  string  Description  The preview of input JSON. |
| previewOtherData | Field Type  string  Description  The preview of input other data. |
| previewSourceObjectData | Field Type  string  Description  The preview of input source object records. |
| previewXmlData | Field Type  string  Description  The preview of input XML. |
| processSuperBulk | Field Type  boolean  Description  Indicates whether the load Omni Data Transformation process the record upsert spread over multiple Salesforce Apex batch jobs (`true`) or not (`false`). |
| requiredPermission | Field Type  string  Description  The list of custom permissions required to execute the Omni Data Transformation. |
| responseCacheTtlMinutes | Field Type  double  Description  The number of minutes the Omni Data Transformation response must stay in the platform cache. |
| responseCacheType | Field Type  string  Description  The platform cache used to store the Omni Data Transformation response, either org cache or session cache. |
| rollbackOnError | Field Type  boolean  Description  Indicates whether the Omni Data Transformation must not commit if there is an error (`true`) or commit what has been executed (`false`). |
| sourceObject | Field Type  string  Description  The SObject that's used as input in a Load Omni Data Transformation. |
| sourceObjectDefault | Field Type  boolean  Description  Indicates whether it's the default Omni Data Transformation setting for the specified interface object (`true`) or not (`false`). |
| synchronousProcessThreshold | Field Type  double  Description  The number of input records that can be processed synchronously in a Load Omni Data Transformation. If it's more than this number, then it uses a batch job. |
| targetOutputDocumentIdentifier | Field Type  string  Description  The envelope ID of the document template. |
| targetOutputFileName | Field Type  string  Description  The document name that receives the output of the Omni Data Transformation. |
| type | Field Type  string  Description  Required.  The definition of what the Omni Data Transformation performs: extract (SOQL), transform, or load (DML). |
| uniqueName | Field Type  string  Description  The unique name for the Omni Data Transformation. |
| versionNumber | Field Type  double  Description  A numeric version that's used with subtype, type, and language to create a unique identifier for Omni Data Transformation. |
| xmlDeclarationRemoved | Field Type  boolean  Description  Indicates whether the XML declaration (e.g. <?xml version="1.0" encoding="UTF-8"?>) must be removed (`true`) or not (`false`). |
| xmlOutputTagsOrder | Field Type  string  Description  The XML tag sequence to be used in the output. |

## OmniDataTransformItem

Represents the configuration of a component inside a DataRaptor.

| Field Name | Description |
| --- | --- |
| defaultValue | Field Type  string  Description  The default value that's used in output map. |
| disabled | Field Type  boolean  Description  Indicates whether the output must not be generated (`true`) or is active and must be generated (`false`). |
| filterDataType | Field Type  ODTItemFilterDataType (enumeration of type string)  Description  The field data type that's used in a Turbo Omni Data Transformation. Values are:   - `ADDRESS` - `ANYTYPE` - `BASE64` - `BOOLEAN` - `COMBOBOX` - `CURRENCY` - `DATACATEGORY` - `DATE` - `DATETIME` - `DOUBLE` - `EMAIL` - `ENCRYPTEDSTRING` - `GROUPREFERENCE` - `ID` - `INTEGER` - `LONG` - `MULTIPICKLIST` - `PERCENT` - `PHONE` - `PICKLIST` - `REFERENCE` - `STRING` - `TEXTAREA` - `TIME` - `URL` |
| filterGroup | Field Type  double  Description  The grouping of WHERE clauses in the SOQL. |
| filterOperator | Field Type  string  Description  The operator in the WHERE clause of the SOQL. |
| filterValue | Field Type  string  Description  The field in the WHERE clause of the SOQL. |
| formulaConverted | Field Type  string  Description  The reverse polish notation of the formula. |
| formulaExpression | Field Type  string  Description  The formula that the user typed in. |
| formulaResultPath | Field Type  string  Description  The variable name where the formula output is stored. |
| formulaSequence | Field Type  double  Description  The sequence of execution of the formulas. |
| globalKey | Field Type  string  Description  The globally unique identifier of the Omni Data Transformation Item that's used to identify the product across Salesforce orgs. |
| inputFieldName | Field Type  string  Description  The field or variable path that's used in the configuration of the inputs. |
| inputObjectName | Field Type  string  Description  The object that's used in the configuration of the inputs. |
| inputObjectQuerySequence | Field Type  double  Description  The execution sequence of the inputs. |
| linkedFieldName | Field Type  string  Description  The field name that's used to look up another object in a Load Omni Data Transformation. |
| linkedObjectSequence | Field Type  double  Description  The UI number (sequence number) associated with the object that's used in the lookup in a Load Omni Data Transformation. |
| lookupByFieldName | Field Type  string  Description  The field name that's used to look up a record in a Load Omni Data Transformation output. |
| lookupObjectName | Field Type  string  Description  The object name that's used to look up a record in a Load Omni Data Transformation output. |
| lookupReturnedFieldName | Field Type  string  Description  The field name that must be returned and used in the lookup in a Load Omni Data Transformation output. |
| migrationAttribute | Field Type  string  Description  Field that's used for DataPacks. |
| migrationCategory | Field Type  string  Description  Field that's used for DataPacks. |
| migrationGroup | Field Type  string  Description  Field that's used for DataPacks. |
| migrationKey | Field Type  string  Description  Field that's used for DataPacks. |
| migrationPattern | Field Type  string  Description  Field that's used for DataPacks. |
| migrationProcess | Field Type  string  Description  Field that's used for DataPacks. |
| migrationType | Field Type  string  Description  Field that's used for DataPacks. |
| migrationValue | Field Type  string  Description  Field that's used for DataPacks. |
| name | Field Type  string  Description  Required.  The Omni Data Transformation name where this configuration belongs to. |
| omniDataTransformation | Field Type  string  Description  Omni Data Transformation associated with the item configuration |
| omniDataTransformationId | Field Type  string  Description  The ID of the Omni Data Transformation associated with this item configuration. |
| outputCreationSequence | Field Type  double  Description  The sequence of the output path items. |
| outputFieldFormat | Field Type  string  Description  The data type of the field, node, or tag in the output path. |
| outputFieldName | Field Type  string  Description  The field, node, or tag in the object that's used in the output path. |
| outputObjectName | Field Type  string  Description  The name of the object that's used in the output path. |
| requiredForUpsert | Field Type  boolean  Description  Indicates whether the field is mandatory for the upsert (`true`) or not (`false`). |
| transformValuesMappings | Field Type  string  Description  The key-value pair JSON list that's used to convert output values into another value. |
| upsertKey | Field Type  boolean  Description  Indicates whether the field is the key to find the records to upsert in the object (`true`) or is a value that's to be used during the upsert (`false`). |

## Declarative Metadata Sample Definition

The following is an example of an OmniDataTransform component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniDataTransform xmlns="http://soap.sforce.com/2006/04/metadata">
    <active>false</active>
    <assignmentRulesUsed>false</assignmentRulesUsed>
    <deletedOnSuccess>false</deletedOnSuccess>
    <errorIgnored>false</errorIgnored>
    <fieldLevelSecurityEnabled>true</fieldLevelSecurityEnabled>
    <inputType>JSON</inputType>
    <isManagedUsingStdDesigner>false</isManagedUsingStdDesigner>
    <name>COODMtest</name>
    <nullInputsIncludedInOutput>false</nullInputsIncludedInOutput>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <globalKey>c7622d95-6995-4b57-8102-716e034e15e4</globalKey>
        <inputFieldName>Account:Type</inputFieldName>
        <inputObjectQuerySequence>0.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>COODMtest</name>
        <outputCreationSequence>1.0</outputCreationSequence>
        <outputFieldName>Type</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <transformValuesMappings>{ }</transformValuesMappings>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <filterOperator>&lt;&gt;</filterOperator>
        <filterValue>&apos;&apos;</filterValue>
        <globalKey>fffd4cd6-7ad8-4e90-adaa-d534a8f75dde</globalKey>
        <inputFieldName>Id</inputFieldName>
        <inputObjectName>Account</inputObjectName>
        <inputObjectQuerySequence>1.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>COODMtest</name>
        <outputCreationSequence>0.0</outputCreationSequence>
        <outputFieldName>Account</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <globalKey>34b482a6-b64e-4d7f-9610-ef1c4f613b44</globalKey>
        <inputFieldName>Account:Id</inputFieldName>
        <inputObjectQuerySequence>0.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>COODMtest</name>
        <outputCreationSequence>1.0</outputCreationSequence>
        <outputFieldName>Id</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <transformValuesMappings>{ }</transformValuesMappings>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <globalKey>5e7ae38a-0cb1-4383-aab9-43e4d88caff2</globalKey>
        <inputFieldName>Account:Name</inputFieldName>
        <inputObjectQuerySequence>0.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>COODMtest</name>
        <outputCreationSequence>1.0</outputCreationSequence>
        <outputFieldName>Name</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <transformValuesMappings>{ }</transformValuesMappings>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <omniDataTransformItem>
        <disabled>false</disabled>
        <filterGroup>0.0</filterGroup>
        <globalKey>1a6f7464-1157-4ec3-b62f-f795c5caceb2</globalKey>
        <inputFieldName>Account:BillingStreet</inputFieldName>
        <inputObjectQuerySequence>0.0</inputObjectQuerySequence>
        <linkedObjectSequence>0.0</linkedObjectSequence>
        <name>COODMtest</name>
        <outputCreationSequence>1.0</outputCreationSequence>
        <outputFieldName>BS</outputFieldName>
        <outputObjectName>json</outputObjectName>
        <requiredForUpsert>false</requiredForUpsert>
        <transformValuesMappings>{ }</transformValuesMappings>
        <upsertKey>false</upsertKey>
    </omniDataTransformItem>
    <outputType>JSON</outputType>
    <processSuperBulk>false</processSuperBulk>
    <responseCacheTtlMinutes>0.0</responseCacheTtlMinutes>
    <rollbackOnError>false</rollbackOnError>
    <sourceObjectDefault>false</sourceObjectDefault>
    <synchronousProcessThreshold>0.0</synchronousProcessThreshold>
    <type>Extract</type>
    <uniqueName>COODMtest_1</uniqueName>
    <versionNumber>1.0</versionNumber>
    <xmlDeclarationRemoved>false</xmlDeclarationRemoved>
</OmniDataTransform>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniDataTransform</name>
    </types>
    <version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information
about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
