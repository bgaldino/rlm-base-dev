---
page_id: meta_expressionsetobjectalias.htm
title: ExpressionSetObjectAlias
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_expressionsetobjectalias.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ExpressionSetObjectAlias

Represents information about the alias of the source
object that’s used in an expression set.

## Parent Type

This type extends the Metadata metadata type and inherits its
fullName field.

## File Suffix and Directory Location

ExpressionSetObjectAlias components have the suffix
.expressionSetObjectAlias and are stored in the
expressionSetObjectAlias folder.

## Version

ExpressionSetObjectAlias components are available in API version 56.0 and later.

## Fields

| Field Name | Description |
| --- | --- |
| dataType | Field Type  ExpsSetObjectDataType (enumeration of type string)  Description  Required.  The data type of the object alias. Values are:   - `JSON` - `sObject` |
| mappings | Field Type  [ExpressionSetObjectAliasField[]](#ExpressionSetObjectAliasField)  Description  The mapping between a source field and its corresponding field alias. |
| objectApiName | Field Type  string  Description  Required.  The API name of the top-level object, when the data type is sObject. The key of the top-level object, when the data type is JSON. |
| usageType | Field Type  ExpsSetProcessType (enumeration of type string)  Description  Required.  The type of application associated with the industry that's using an expression set. Your Salesforce org admin can define the values. Valid values are:   - `Bre` - `GpaCalculation` - `InsuranceClaimProcessing`—Available   in API version 65.0 and later. - `ItServiceManagement`—Available in   API version 65.0 and later. - `PlanCostCalculation` - `RatingDiscovery` - `StudentInformationSystem`—Available   in API version 65.0 and later. - `StudentSuccess`  When Business Rules Engine is enabled for a Salesforce instance, the default value is '`Bre`’. Other usage types are available to you depending on your industry solution and permission sets. |

## ExpressionSetObjectAliasField

The fields associated with the source object for which the object
alias is created.

| Field Name | Description |
| --- | --- |
| fieldAlias | Field Type  string  Description  Required.  The field alias associated with the source field name. |
| sourceFieldName | Field Type  string  Description  Required.  The name of the source field for which the field alias is created. The source field name under an object alias must be unique. |

## Declarative Metadata Sample Definition

The following is an example of an ExpressionSetObjectAlias component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ExpressionSetObjectAlias xmlns="http://soap.sforce.com/2006/04/metadata">
    <dataType>sObject</dataType>
    <mappings>
        <fieldAlias>dum2</fieldAlias>
        <sourceFieldName>CreatedBy.Contact.Name</sourceFieldName>
    </mappings>
    <mappings>
        <fieldAlias>dum3</fieldAlias>
        <sourceFieldName>CreatedBy.Name</sourceFieldName>
    </mappings>
    <mappings>
        <fieldAlias>dum1</fieldAlias>
        <sourceFieldName>Owner.Contact.Name</sourceFieldName>
    </mappings>
    <objectApiName>Account</objectApiName>
    <usageType>Bre</usageType>
</ExpressionSetObjectAlias>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<types>
		<members>*</members>
		<name>ExpressionSetObjectAlias</name>
	</types>
	<version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip
File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based.htm "HTML (New Window)").
