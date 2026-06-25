---
page_id: meta_omniintegrationprocedure.htm
title: OmniIntegrationProcedure
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniintegrationprocedure.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniIntegrationProcedure

Represents an Omnistudio Integration Procedure for the
Discovery Framework. It enables declarative, server-side processing to perform multiple
actions in a single server call, supporting sales, service, and other business
workflows. For Discovery Framework, the customization type is
`discoveryframework`.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

## File Suffix and Directory Location

OmniIntegrationProcedure components have the suffix
.omniIntegrationProcedure and are stored in the
omnistudio/<Namespace>/omniIntegrationProcedures
folder.

## Version

OmniIntegrationProcedure components are available in API version 56.0 and later.

## Special Access Rules

To use this metadata type, you must have an Omnistudio license and the Discovery
Framework feature enabled in your Salesforce org.

## Fields

| Field Name | Description |
| --- | --- |
| customHtmlTemplates | Field Type  string  Description  The angular Omniscript template definitions. |
| customJavaScript | Field Type  string  Description  The custom JavaScript used for integration procedure. |
| description | Field Type  string  Description  The description of the integration procedure. |
| designerCustomizationType | Field Type  string  Description  The Omnistudio designer customization type. |
| elementTypeComponentMapping | Field Type  string  Description  Overrides all elements of one type with a custom Lightning web component by mapping the element type to the Custom LWC. |
| integrationProcedureInput | Field Type  string  Description  The input for the integration procedure in JSON format. |
| integrationProcedureOutput | Field Type  string  Description  The output for the integration procedure in JSON format. |
| isActive | Field Type  boolean  Description  Indicates whether the integration procedure is active (`true`) or not (`false`). The default value is `false`. |
| isIntegProcdSignatureAvl | Field Type  boolean  Description  Indicates whether the integration procedure has a signature (`true`) or not (`false`). The default value is `false`. |
| isIntegrationProcedure | Field Type  boolean  Description  Indicates whether Omniscript is an Integration Procedure (`true`) or Omniscript metadata (`false`). |
| isManagedUsingStdDesigner | Field Type  boolean  Description  Indicates whether the integration procedure is managed using standard designer (`true`) or not (`false`). |
| isMetadataCacheDisabled | Field Type  boolean  Description  Indicates whether metadata cache for the integration procedure is disabled (`true`) or not (`false`). The default value is `false`. |
| isOmniScriptEmbeddable | Field Type  boolean  Description  Indicates whether the Omniscript can be embedded in other Omniscripts (`true`) or not (`false`). The default value is `false` |
| isTestProcedure | Field Type  boolean  Description  Indicates whether OmniIntegrationProcedure is a test procedure setting (`true`) or not (`false`). The default value is `false` |
| isWebCompEnabled | Field Type  boolean  Description  Indicates whether web component Omniscript (not Angular) is enabled (`true`) or not (`false`). The default value is `false` |
| language | Field Type  string  Description  Required.  The language of the integration procedure. |
| lastPreviewPage | Field Type  string  Description  The last page previewed in the Omniscript designer. |
| name | Field Type  string  Description  Required.  The name of the integration procedure. |
| nameSpace | Field Type  string  Description  The namespace associated with the integration procedure record. |
| omniProcessElements | Field Type  [OmniProcessElement[]](#OmniProcessElement)  Description  The OmniProcessElements associated with the OmniIntegrationProcedure. |
| omniProcessKey | Field Type  string  Description  The integration procedure `Type_SubType` value. |
| omniProcessType | Field Type  OmniProcessType (enumeration of type string)  Description  Required. Integration Procedure or Omniscript.  Possible value is:  - `Integration   Procedure` |
| overrideKey | Field Type  string  Description  Reserved for future use. |
| propertySetConfig | Field Type  string  Description  The configuration information associated with the OmniIntegrationProcedure. |
| requiredPermission | Field Type  string  Description  The required permissions to execute the integration procedure. |
| responseCacheType | Field Type  string  Description  Response cache used for the integration procedure (session or Org). |
| subType | Field Type  string  Description  Required.  The subtype value that's used with type and language to create a unique identifier for integration procedure. Integration Procedure subtype can contain only alphanumeric characters. |
| type | Field Type  string  Description  Required.  The type value that's used with subtype and language to create a unique identifier for integration procedure. Integration Procedure type can contain only alphanumeric characters. |
| uniqueName | Field Type  string  Description  Required.  The unique name for the integration procedure as Type\_SubType\_Language\_VersionNumber. |
| versionNumber | Field Type  string  Description  Required.  A numeric version that's used with subtype, type, and language to create a unique identifier for integration procedure. |
| webComponentKey | Field Type  string  Description  Internal unique key for the generated Lightning Web Components (LWC). |

## OmniProcessElement

Represents the Omnistudio Process Element associated with the Omnistudio Integration
Procedure.

| Field Name | Description |
| --- | --- |
| childElements | Field Type  [OmniProcessElement[]](#OmniProcessElement)  Description  The child elements associated with the OmniProcessElement. |
| description | Field Type  string  Description  The description of the OmniProcessElement. |
| designerCustomizationType | Field Type  string  Description  The Omnistudio designer customization type. |
| discoveryFrameworkUsageType | Field Type  string  Description  The usage type for industries that use the Discovery Framework. For example, the value for Health Cloud is `HcUsageType`. The value for no specific industry is `Default`. |
| embeddedOmniScriptKey | Field Type  string  Description  The ID of the embedded Omniscript. |
| isActive | Field Type  boolean  Description  Indicates whether the status of the OmniProcessElement is active (`true`) or not (`false`). |
| isOmniScriptEmbeddable | Field Type  boolean  Description  Indicates whether the Omniscript with the OmniProcessElement can be embedded in other Omniscript (`true`) or not (`false`). |
| level | Field Type  double  Description  The vertical level in which the OmniProcessElement occurs on the Omniscript. |
| name | Field Type  string  Description  Required.  The name of the OmniProcessElement. |
| omniProcessVersionNumber | Field Type  double  Description  The version number of Omnistudio process element. |
| parentElementName | Field Type  string  Description  The name of the parent OmniProcessElement. |
| parentElementType | Field Type  string  Description  The type of the parent OmniProcessElement. |
| propertySetConfig | Field Type  textarea  Description  The property set of the OmniProcessElement. |
| sequenceNumber | Field Type  double  Description  The horizontal level in which the OmniProcessElement occurs on the Omniscript. |
| type | Field Type  string  Description  The OmniProcessElement type. For example, `Text` and `TextArea`. |
| uniqueIndex | Field Type  string  Description  A unique index number for the Omniscript. |

## Declarative Metadata Sample Definition

The following is an example of an OmniIntegrationProcedure component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniIntegrationProcedure xmlns="http://soap.sforce.com/2006/04/metadata">
    <customJavaScript>{&quot;salary&quot;:332}</customJavaScript>
    <elementTypeComponentMapping>{&quot;ElementTypeToHTMLTemplateList&quot;:[]}</elementTypeComponentMapping>
    <integrationProcedureInput>{
  &quot;properties&quot;: {
    &quot;salary&quot;: {
      &quot;type&quot;: &quot;integer&quot;
    }
  },
  &quot;type&quot;: &quot;object&quot;,
  &quot;title&quot;: &quot;Data&quot;,
  &quot;$schema&quot;: &quot;https://json-schema.org/draft/2020-12/schema&quot;
}</integrationProcedureInput>
    <integrationProcedureOutput>{
  &quot;properties&quot;: {
    &quot;tax&quot;: {
      &quot;type&quot;: &quot;double&quot;
    }
  },
  &quot;type&quot;: &quot;object&quot;,
  &quot;title&quot;: &quot;Data&quot;,
  &quot;$schema&quot;: &quot;https://json-schema.org/draft/2020-12/schema&quot;
}</integrationProcedureOutput>
    <isActive>true</isActive>
    <isIntegProcdSignatureAvl>true</isIntegProcdSignatureAvl>
    <isIntegrationProcedure>true</isIntegrationProcedure>
    <isManagedUsingStdDesigner>false</isManagedUsingStdDesigner>
    <isMetadataCacheDisabled>false</isMetadataCacheDisabled>
    <isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
    <isTestProcedure>false</isTestProcedure>
    <isWebCompEnabled>false</isWebCompEnabled>
    <language>English</language>
    <name>Calc</name>
    <omniProcessElements>
        <description>Response Action</description>
        <isActive>true</isActive>
        <isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
        <level>0.0</level>
        <name>Response</name>
        <omniProcessVersionNumber>0.0</omniProcessVersionNumber>
        <propertySetConfig>{
  &quot;responseJSONPath&quot; : &quot;&quot;,
  &quot;responseJSONNode&quot; : &quot;&quot;,
  &quot;executionConditionalFormula&quot; : &quot;&quot;,
  &quot;returnFullDataJSON&quot; : false,
  &quot;additionalOutput&quot; : {
    &quot;tax&quot; : &quot;=%salary%*0.3&quot;
  },
  &quot;returnOnlyAdditionalOutput&quot; : false,
  &quot;sendJSONPath&quot; : &quot;&quot;,
  &quot;responseFormat&quot; : &quot;&quot;,
  &quot;id&quot; : &quot;&quot;,
  &quot;isActive&quot; : true,
  &quot;restOptions&quot; : { },
  &quot;sendJSONNode&quot; : &quot;&quot;
}</propertySetConfig>
        <sequenceNumber>1.0</sequenceNumber>
        <type>Response Action</type>
    </omniProcessElements>
    <omniProcessKey>calc_calc</omniProcessKey>
    <omniProcessType>Integration Procedure</omniProcessType>
    <propertySetConfig>{
  &quot;transientValues&quot; : {
    &quot;deactivateConsent&quot; : false
  }
}</propertySetConfig>
    <subType>calc</subType>
    <type>calc</type>
    <uniqueName>calc_calc_English_1</uniqueName>
    <versionNumber>1.0</versionNumber>
</OmniIntegrationProcedure>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
    xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniIntegrationProcedure</name>
    </types>
    <version>66.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information
about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").

## Usage Type

Before you retrieve or deploy Discovery Framework OmniScripts, we recommend that you review
this consideration.

- When deploying the OmniIntegrationProcedure of type Discovery Framework, enable
  Discovery Framework Metadata Enabled setting.
