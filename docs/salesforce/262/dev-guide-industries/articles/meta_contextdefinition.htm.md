---
page_id: meta_contextdefinition.htm
title: ContextDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_contextdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# ContextDefinition

Represents the details of a context definition that
describe the relationship between the node structures within a context.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type
and inherits its fullName field.

## File Suffix and Directory Location

ContextDefinition components have the suffix .contextDefinition
and are stored in the contextDefinitions folder.

## Version

ContextDefinition components are available in API version 59.0 and later.

## Special Access Rules

Enable the organization preference ContextDefinitionsEnabled to access the
ContextDefinition metadata type.

## Fields

| Field Name | Description |
| --- | --- |
| canBeReferenceDefinition | Field Type  boolean  Description  Indicates whether the context definition can be referred by other context definitions (`true`) or not (`false`). Available in API version 63.0 and later.  The default value is `false`. |
| clonedFrom | Field Type  string  Description  The name of the context definition that's used to clone the current context definition. |
| contextDefinitionReferences | Field Type  [ContextDefinitionReference](#ContextDefinitionReference)[]  Description  References of the context definition. |
| contextDefinitionVersions | Field Type  [ContextDefinitionVersion[]](#ContextDefinitionVersion)  Description  Version of the context definition. |
| contextTtl | Field Type  int  Description  Duration to persist the data, which is loaded in the run-time context instances created by this context definition, in the cache.  The default value is 10 minutes. |
| description | Field Type  string  Description  Description of the context definition. |
| hasSystemTags | Field Type  boolean  Description  Indicates whether the context definition has system tags (`true`) or not (`false`). Available in API version 63.0 and later.  The default value is `false`. |
| inheritedFrom | Field Type  string  Description  Name of the parent context definition that's used to derive the current context definition. |
| inheritedFromVersion | Field Type  string  Description  Version number of the parent definition that's used to derive the current context definition. |
| isProtected | Field Type  boolean  Description  Auto-generated value that doesn’t impact the behavior of the metadata type. |
| masterLabel | Field Type  string  Description  Required.  User-friendly name for the context definition, which is defined when the context definition is created. |
| title | Field Type  string  Description  Required.  Name of the context definition. |

## ContextDefinitionReference

Represents details about the context definition reference.

| Field Name | Description |
| --- | --- |
| inheritedFrom | Field Type  string  Description  ID of the parent context definition reference that's used to derive the current context definition reference. |
| referenceContextDefinition | Field Type  string  Description  Required.  ID or name of the referred context definition. |

## ContextDefinitionVersion

Represents details about the context definition version. Only one version can be
active at a time.

| Field Name | Description |
| --- | --- |
| contextMappings | Field Type  [ContextMapping[]](#ContextMapping)  Description  Mapping of attributes and nodes to related objects. |
| contextNodes | Field Type  [ContextNode[]](#ContextNode)  Description  Details of the structure of the nodes within the context. |
| endDate | Field Type  string  Description  Date and time when the context definition version becomes inactive. |
| isActive | Field Type  boolean  Description  Indicates whether the context definition version is active (`true`) or not (`false`).  The default value is `false`. |
| startDate | Field Type  string  Description  Required. Date and time when the context definition version becomes active. |
| versionNumber | Field Type  int  Description  Required. Version number of the context definition. |

## ContextMapping

Represents the mapping of attributes and nodes to related objects.

| Field Name | Description |
| --- | --- |
| contextMappingIntents | Field Type  [ContextMappingIntent[]](#ContextMappingIntent)  Description  Purpose associated to a context mapping. |
| contextNodeMappings | Field Type  [ContextNodeMapping[]](#ContextNodeMapping)  Description  Mapping of the node in the context and values in the input schema. |
| default | Field Type  boolean  Description  Indicates whether the mapping for a context definition version is default (`true`) or not (`false`).  The default value is `false`. |
| description | Field Type  string  Description  Description of the context mapping. |
| inheritedFrom | Field Type  string  Description  Name of the parent mapping that's used to derive the current mapping. |
| title | Field Type  string  Description  Required. Name of the context mapping. |

## ContextMappingIntent

Represents the purpose associated to a context mapping.

| Field Name | Description |
| --- | --- |
| mappingIntent | Field Type  ContextMappingIntentType (enumeration of type string)  Description  Required.  Specifies the purpose that's used to identify the type of context mapping required.  Valid values are:   - `hydration` - `association` - `persistence` - `translation` |

## ContextNodeMapping

Represents the relationship between the node in the context and values in the input
schema.

| Field Name | Description |
| --- | --- |
| contextAttributeMappings | Field Type  [ContextAttributeMapping[]](#ContextAttributeMapping)  Description  Mapping of the attribute defined in the context and the values in the related objects. |
| contextNode | Field Type  string  Description  Context node record associated with the context node mapping. |
| contextNodeAttrDictionaries | Field Type  [ContextNodeAttrDictionary[]](#ContextNodeAttrDictionary)  Description  Facilitates relationships between context node mapping and context dictionary. Additionally, it records the relationship between context node and context dictionary. |
| inheritedFrom | Field Type  string  Description  Name of the parent context node mapping that's used to derive the current context node mapping. |
| mappedContextDefinition | Field Type  string  Description  API name of the context definition for existing context-to-context mappings. |
| object | Field Type  string  Description  Name of the object used for the mapping. |

## ContextAttributeMapping

Represents the relationship between the attributes defined in the context and the
values in the related objects.

| Field Name | Description |
| --- | --- |
| contextAttrHydrationDetails | Field Type  [ContextAttrHydrationDetail[]](#ContextAttrHydrationDetail)  Description  Details of the SOQL (database) queries that fetch data for a chosen attribute from the input schema. |
| contextAttribute | Field Type  string  Description  Context attribute record associated with the context attribute mapping. |
| contextInputAttributeName | Field Type  string  Description  Required. Name of the input attribute. |
| ctxAttrHydrationCtxs | Field Type  [CtxAttrHydrationCtx[]](#CtxAttrHydrationCtx)  Description  Query that fetches data for a chosen attribute from the input schema for context-to-context mapping. |
| inheritedFrom | Field Type  string  Description  Name of the parent context attribute mapping that's used to derive the current context attribute mapping. |

## ContextAttrHydrationDetail

Represents the SOQL (database) queries that fetch data for a chosen attribute from
the input schema.

| Field Name | Description |
| --- | --- |
| contextAttrHydrationDetails | Field Type  [ContextAttrHydrationDetail[]](#ContextAttrHydrationDetail)  Description  Details of the query that fetches the data for the specific query attribute. |
| inheritedFrom | Field Type  string  Description  Name of the parent context attribute hydration detail that's used to derive the current context attribute hydration detail. |
| objectName | Field Type  string  Description  Required. Name of the object used for the attribute hydration detail. |
| queryAttribute | Field Type  string  Description  Required. The SOQL query that is the source of the hydration. |

## CtxAttrHydrationCtx

Represents the queries that fetch data for a chosen attribute from the input schema
for context-to-context mapping.

| Field Name | Description |
| --- | --- |
| contextQueryAttribute | Field Type  string  Description  Required. Attribute in context definition that's the source of context hydration. |
| inheritedFrom | Field Type  string  Description  Name of the parent context attribute hydration detail that's used to derive the current context attribute. |

## ContextNodeAttrDictionary

Represents the relationship between a context node and the context attribute
dictionary.

| Field Name | Description |
| --- | --- |
| contextAttrDictIdentifier | Field Type  string  Description  Required. Developer name of the context attribute dictionary. |
| contextNodeTagPrefix | Field Type  string  Description  Required. Tag prefix of the context node that's used to create the unique identifier of the parent context node. |

## ContextNode

Represents details of the structure of the nodes within the context. Each node can
have other nodes related to them and attributes to describe the object. You can also
define a hierarchy for the nodes.

| Field Name | Description |
| --- | --- |
| canonicalNode | Field Type  string  Description  Canonical node that's associated with the context node. |
| contextAttributes | Field Type  [ContextAttribute[]](#ContextAttribute)  Description  Details of the attribute used to describe the context node. |
| contextNodeAttrDictionaries | Field Type  [ContextNodeAttrDictionary[]](#ContextNodeAttrDictionary)  Description  Facilitates relationships between context node and context dictionary. Additionally, it records the relationship between context node and context dictionary. |
| contextTags | Field Type  [ContextTag[]](#ContextTag)  Description  Unique identifier of the attribute or node. |
| displayName | Field Type  string  Description  Display name of the context node. |
| inheritedFrom | Field Type  string  Description  Name of the parent context node that's used to derive the current context node. |
| title | Field Type  string  Description  Required. Name of the context node. |
| transposable | Field Type  boolean  Description  Indicates whether the data in the Context Node record can be converted to field names (`true`) or not (`false`).  The default value is `false`. |

## ContextAttribute

Represents details of an attribute used to describe a context node. Each node can
have one or many associated attributes.

| Field Name | Description |
| --- | --- |
| contextTags | Field Type  [ContextTag[]](#ContextTag)  Description  Shortened name of the attribute or node. |
| dataType | Field Type  ContextAttributeDataType (enumeration of type string)  Description  Required.  Type of data that's stored in the context attribute.  Valid values are:   - `boolean` - `currency` - `date` - `datetime` - `number` - `percent` - `picklist` - `reference` - `string` - `selfreference`—Available in API   version 63.0 and later. |
| description | Field Type  string  Description  Description of the context attribute. |
| displayName | Field Type  string  Description  Display name of the context attribute. |
| domainSet | Field Type  string  Description  List of node references to show the parent-child relationship between the nodes in a definition. |
| fieldType | Field Type  ContextAttributeFieldType (enumeration of type string)  Description  Required.  List of node references to depict the parent-child relation between the nodes in a definition.  Valid values are:   - `aggregate` - `input` - `inputoutput` - `output` |
| inheritedFrom | Field Type  string  Description  Name of the parent attribute that's used to derive the current attribute. |
| key | Field Type  boolean  Description  Indicates whether the attribute is a key attribute in the node (`true`) or not (`false`).  The default value is `false`. |
| title | Field Type  string  Description  Required. Name of the context attribute. |
| transient | Field Type  boolean  Description  Indicates if an attribute is skipped in context persistence (`true`) or not (`false`). Available in API version 63.0 and later.  The default value is `false`. |
| value | Field Type  boolean  Description  Indicates whether the attribute identifies as a value in a node (`true`) or not (`false`).  The default value is `false`. |

## ContextTag

Represents a unique identifier of an attribute or node instead of a fully qualified
tag structure name.

| Field Name | Description |
| --- | --- |
| title | Field Type  string  Description  Required. Name of the context tag. |
| inheritedFrom | Field Type  string  Description  Name of the parent context tag that's used to derive the current context tag. |

## Declarative Metadata Sample Definition

The following is an example of a ContextDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<ContextDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>Test</fullName>
    <contextDefinitionVersions>
        <contextMappings>
            <contextNodeMappings>
                <contextNodeAttrDictionaries>
                    <contextAttrDictIdentifier>Context Attribute Dictionary Name</contextAttrDictIdentifier>
                    <contextNodeTagPrefix>Context Node Tag Prefix</contextNodeTagPrefix>
                </contextNodeAttrDictionaries>
                <contextAttributeMappings>
                    <contextAttrHydrationDetails>
                        <objectName>CustomAccount__c</objectName>
                        <queryAttribute>Name</queryAttribute>
                        <inheritedFrom>StandardDefinition/version/CustomAccountMapping/Praneeth/AccountName/hydrationInfo-1</inheritedFrom>
                    </contextAttrHydrationDetails>
                    <ctxAttrHydrationCtxs>
                        <contextQueryAttribute>StandardDefinition</contextQueryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/AccountName/ctxToCtxhydrationInfo-1</inheritedFrom>
                    </ctxAttrHydrationCtxs>
                    <contextAttribute>AccountName</contextAttribute>
                    <contextInputAttributeName>AccountName</contextInputAttributeName>
                    <inheritedFrom>StandardDefinition/version/CustomAccountMapping/Praneeth/AccountName</inheritedFrom>
                </contextAttributeMappings>
                <contextAttributeMappings>
                    <contextAttrHydrationDetails>
                        <objectName>CustomAccount__c</objectName>
                        <queryAttribute>CustomAccountName__c</queryAttribute>
                        <inheritedFrom>StandardDefinition/version/CustomAccountMapping/Praneeth/CustomAccountName/hydrationInfo-1</inheritedFrom>
                    </contextAttrHydrationDetails>
                    <ctxAttrHydrationCtxs>
                        <contextQueryAttribute>StandardDefinition</contextQueryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/AccountName/ctxToCtxhydrationInfo-1</inheritedFrom>
                    </ctxAttrHydrationCtxs>
                    <contextAttribute>CustomAccountName</contextAttribute>
                    <contextInputAttributeName>CustomAccountName</contextInputAttributeName>
                    <inheritedFrom>StandardDefinition/version/CustomAccountMapping/Praneeth/CustomAccountName</inheritedFrom>
                </contextAttributeMappings>
                <contextNode>Praneeth</contextNode>
                <object>CustomAccount__c</object>
                <inheritedFrom>StandardDefinition/version/CustomAccountMapping/Praneeth</inheritedFrom>
                <mappedContextDefinition>CustomContextDefinition</mappedContextDefinition>
            </contextNodeMappings>
            <contextMappingIntents>
                <mappingIntent>hydration</mappingIntent>
            </contextMappingIntents>
            <default>true</default>
            <title>CustomAccountMapping</title>
            <inheritedFrom>StandardDefinition/version/CustomAccountMapping</inheritedFrom>
        </contextMappings>
        <contextMappings>
            <contextNodeMappings>
                <contextNodeAttrDictionaries>
                    <contextAttrDictIdentifier>Context Attribute Dictionary Name</contextAttrDictIdentifier>
                    <contextNodeTagPrefix>Context Node Tag Prefix</contextNodeTagPrefix>
                </contextNodeAttrDictionaries>
                <contextAttributeMappings>
                    <contextAttrHydrationDetails>
                        <objectName>Account</objectName>
                        <queryAttribute>Name</queryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/CustomAccountName/AccountName/hydrationInfo-1</inheritedFrom>
                    </contextAttrHydrationDetails>
                    <ctxAttrHydrationCtxs>
                        <contextQueryAttribute>StandardDefinition</contextQueryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/AccountName/ctxToCtxhydrationInfo-1</inheritedFrom>
                    </ctxAttrHydrationCtxs>
                    <contextAttribute>AccountName</contextAttribute>
                    <contextInputAttributeName>AccountName</contextInputAttributeName>
                    <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/CustomAccountName/AccountName</inheritedFrom>
                </contextAttributeMappings>
                <contextAttributeMappings>
                    <contextAttrHydrationDetails>
                        <objectName>Account</objectName>
                        <queryAttribute>CustomAccountName__c</queryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/CustomAccountName/hydrationInfo-1</inheritedFrom>
                    </contextAttrHydrationDetails>
                    <ctxAttrHydrationCtxs>
                        <contextQueryAttribute>StandardDefinition</contextQueryAttribute>
                        <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/AccountName/ctxToCtxhydrationInfo-1</inheritedFrom>
                    </ctxAttrHydrationCtxs>
                    <contextAttribute>CustomAccountName</contextAttribute>
                    <contextInputAttributeName>CustomAccountName</contextInputAttributeName>
                    <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth/CustomAccountName</inheritedFrom>
                </contextAttributeMappings>
                <contextNode>Praneeth</contextNode>
                <object>Account</object>
                <inheritedFrom>StandardDefinition/version/AccountMapping/Praneeth</inheritedFrom>
                <mappedContextDefinition>CustomContextDefinition</mappedContextDefinition>
            </contextNodeMappings>
             <contextMappingIntents>
                <mappingIntent>persistence</mappingIntent>
             </contextMappingIntents>
            <description>Account Mapping</description>
            <default>false</default>
            <title>AccountMapping</title>
            <inheritedFrom>StandardDefinition/version/AccountMapping</inheritedFrom>
        </contextMappings>
        <contextNodes>
            <contextNodeAttrDictionaries>
                <contextAttrDictIdentifier>Context Attribute Dictionary Name</contextAttrDictIdentifier>
                <contextNodeTagPrefix>Context Node Tag Prefix</contextNodeTagPrefix>
            </contextNodeAttrDictionaries>
            <contextAttributes>
                <contextTags>
                    <title>AccountName</title>
                    <inheritedFrom>StandardDefinition/version/Praneeth/AccountName/AccountName</inheritedFrom>
                </contextTags>
                <dataType>string</dataType>
                <fieldType>inputoutput</fieldType>
                <key>false</key>
                <title>AccountName</title>
                <displayName>AccountName</displayName>
                <description>Test Description</description>
                <value>false</value>
                <inheritedFrom>StandardDefinition/version/Praneeth/AccountName</inheritedFrom>
            </contextAttributes>
            <contextAttributes>
                <dataType>string</dataType>
                <fieldType>inputoutput</fieldType>
                <key>false</key>
                <title>CustomAccountName</title>
                <value>false</value>
                <displayName>CustomAccountName</displayName>
                <description>Test Description</description>
                <inheritedFrom>StandardDefinition/version/Praneeth/CustomAccountName</inheritedFrom>
            </contextAttributes>
            <contextTags>
                <title>Praneeth</title>
                <inheritedFrom>StandardDefinition/version/Praneeth/Praneeth</inheritedFrom>
            </contextTags>
            <title>Praneeth</title>
            <transposable>false</transposable>
            <inheritedFrom>StandardDefinition/version/Praneeth</inheritedFrom>
            <canonicalNode></canonicalNode>
            <displayName>Praneeth</displayName>
        </contextNodes>
        <endDate>2097-05-10 00:00:00</endDate>
        <startDate>2023-05-10 00:00:00</startDate>
        <versionNumber>1</versionNumber>
        <isActive>true</isActive>
    </contextDefinitionVersions>
    <description>Test Description</description>
    <contextTtl>10</contextTtl>
    <inheritedFrom>StandardDefinition</inheritedFrom>
    <inheritedFromVersion>1.0</inheritedFromVersion>
    <clonedFrom>OriginalDefinition</clonedFrom>
    <isProtected>false</isProtected>
    <masterLabel>Test Label</masterLabel>
    <title>TestTitle</title>
    <displayName>TestTitle</displayName>
</ContextDefinition>
```

The following is an example `package.xml` that
references the previous definition.

```
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Test</members>
        <name>ContextDefinition</name>
    </types>
    <types>
        <members>Account.CustomAccountName__c</members>
        <name>CustomField</name>
    </types>
    <types>
        <members>CustomAccount__c</members>
        <name>CustomObject</name>
    </types>
    <version>64.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving
Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
