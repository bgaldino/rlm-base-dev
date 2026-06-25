---
page_id: meta_omniscript.htm
title: OmniScript
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniscript.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniScript

Represents an OmniScript for the Discovery Framework, which
guides users through sales, service, and other business processes. For Discovery
Framework, the customization type is `discoveryframework`.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniScript components have the suffix omniScript and are stored
in the omniScripts folder.

## Version

OmniScript components are available in API version 56.0 and later.

## Special Access Rules

To use this metadata type, you must have an Omnistudio license and the Discovery Framework
feature enabled in your Salesforce org.

## Fields

| Field Name | Description |
| --- | --- |
| assessmentDefinitionMetadata | Field Type  [AssessmentDefinitionMetadata[]](#AssessmentDefinitionMetadata)  Description  Metadata associated with an assessment definition. Available in API version 64.0 and later. |
| customHtmlTemplates | Field Type  string  Description  The angular OmniScript template definitions. |
| customJavaScript | Field Type  string  Description  The custom JavaScript used for an OmniScript. |
| designerCustomizationType | Field Type  string  Description  The Omnistudio designer customization type. |
| elementTypeComponentMapping | Field Type  string  Description  Overrides all elements of one type with a custom Lightning web component by mapping the element type to the Custom LWC. |
| isActive | Field Type  boolean  Description  Indicates whether the OmniScript is active (`true`) or not (`false`). The default value is `false`. |
| isIntegrationProcedure | Field Type  boolean  Description  Indicates whether OmniScript is an Integration Procedure (`true`) or OmniScript metadata (`false`). The default value is `false`. |
| isManagedUsingStdDesigner | Field Type  boolean  Description  Indicates whether Omniscript is managed using standard designer (`true`) or not (`false`). Available in API version 64.0 and later. |
| isMetadataCacheDisabled | Field Type  boolean  Description  Indicates whether metadata cache for the integration procedure is disabled (`true`) or not (`false`). The default value is `false`. |
| isOmniScriptEmbeddable | Field Type  boolean  Description  Indicates whether the OmniScript can be embedded in other OmniScripts (`true`) or not (`false`). The default value is `false` |
| isTestProcedure | Field Type  boolean  Description  Indicates whether OmniScript is a test procedure setting (`true`) or not (`false`). The default value is `false` |
| isWebCompEnabled | Field Type  boolean  Description  Indicates whether web component OmniScript (not Angular) is enabled (`true`) or not (`false`). The default value is `false` |
| language | Field Type  string  Description  Required.  The language of the OmniScript. |
| lastPreviewPage | Field Type  string  Description  The last page previewed in the OmniScript designer. |
| name | Field Type  string  Description  Required.  The name of the OmniScript. |
| namespace | Field Type  string  Description  The namespace associated with this OmniScript record. |
| omniAssessmentTasks | Field Type  [OmniAssessmentTaskMetadata](#subtype_OmniAssessmentTask)[]  Description  The omniAssessmentTasks associated with the OmniScript. Available in API version 63.0 and later.  This field is available only if the Dynamic Assessment Access license is enabled. |
| omniProcessElements | Field Type  [OmniProcessElement](#subtype_OmniProcessElement)[]  Description  The OmniProcessElements associated with the OmniScript. |
| omniProcessKey | Field Type  string  Description  The integration procedure `Type_SubType` value. |
| omniProcessType | Field Type  OmniProcessType (enumeration of type string)  Description  Required. Integration Procedure or OmniScript.  Possible value is:  - `OmniScript` |
| overrideKey | Field Type  string  Description  Reserved for future use. |
| propertySetConfig | Field Type  string  Description  The configuration information associated with the OmniScript. |
| uniqueIndex | Field Type  string  Description  The developer name of the assessment question in the OmniScript.  This field is relevant only for Omniscripts with designerCustomizationType as `discoveryframework`. |
| requiredPermission | Field Type  string  Description  The required permissions to execute the integration procedure. |
| responseCacheType | Field Type  string  Description  Response cache used for the integration procedure (session or Org). |
| subType | Field Type  string  Description  Required.  The OmniScript sub type value. |
| type | Field Type  string  Description  Required.  The OmniScript type value. |
| uniqueName | Field Type  string  Description  Required.  The unique name for the OmniScript as Type\_SubType\_Language\_VersionNumber. |
| versionNumber | Field Type  string  Description  Required.  The OmniScript version number. |
| webComponentKey | Field Type  string  Description  Internal unique key for the generated Lightning Web Components (LWC). |

## AssessmentDefinitionMetadata

Represents the metadata associated with the assessment definition.

| Field Name | Description |
| --- | --- |
| approvalDateTime | Field Type  dateTime  Description  The date and time when this version of the assessment definition was approved. |
| displayType | Field Type  string  Description  The way this assessment is displayed in a user interface. |
| effectiveFromDate | Field Type  dateTime  Description  The date and time from which the assessment definition becomes active and can be used. |
| effectiveToDate | Field Type  dateTime  Description  The date and time until when this assessment definition is effective. |
| lastRevisedDateTime | Field Type  dateTime  Description  The date and time when this assessment definition was last modified. |
| performerType | Field Type  string  Description  The type of user, role, or system qualified or intended to complete the assessment. |
| purpose | Field Type  string  Description  Reason for the assessment. |

## OmniAssessmentTaskMetadata

Represents the omni assessment tasks associated with the OmniScript.

| Field Name | Description |
| --- | --- |
| name | Field Type  string  Description  Required. The name of the omni assessment task. |
| status | Field Type  picklist  Description  The status of the omni assessment task.  Possible values are:  - `Completed` - `InProgress`—In Progress - `IsDefined`—Is Defined - `NotStarted`—Not Started  The default value is `IsDefined`. |
| uniqueName | Field Type  string  Description  A unique name for the omni assessment task. |

## OmniProcessElement

Represents the OmniScript element associated with the OmniScript.

| Field Name | Description |
| --- | --- |
| childElements | Field Type  [OmniProcessElement](#subtype_OmniProcessElement)[]  Description  The child elements associated with the OmniProcessElement. |
| description | Field Type  string  Description  The description of the OmniProcessElement. |
| designerCustomizationType | Field Type  string  Description  The Omnistudio designer customization type.  To create assessment questions using the Discovery Framework feature, use the customization type as `discoveryframework`. |
| discoveryFrameworkUsageType | Field Type  string  Description  The usage type for industries that use the Discovery Framework. For example, the value for Health Cloud is `HcUsageType`. The value for no specific industry is `Default`. |
| embeddedOmniScriptKey | Field Type  string  Description  The ID of the embedded OmniScript |
| isActive | Field Type  boolean  Description  Indicates whether the status of the OmniProcessElement is active (`true`) or not (`false`). |
| isOmniScriptEmbeddable | Field Type  boolean  Description  Indicates whether the OmniScript with the OmniProcessElement can be embedded in other OmniScripts (`true`) or not (`false`). |
| level | Field Type  double  Description  The vertical level in which the OmniProcessElement occurs on the OmniScript. |
| name | Field Type  string  Description  Required.  The name of the OmniProcessElement. |
| omniProcessVersionNumber | Field Type  double  Description  The related OmniProcess version. |
| parentElementName | Field Type  string  Description  The name of the parent OmniProcessElement. |
| parentElementType | Field Type  string  Description  The type of the parent OmniProcessElement. |
| propertySetConfig | Field Type  textarea  Description  The property set of the OmniProcessElement. |
| sequenceNumber | Field Type  double  Description  The horizontal level in which the OmniProcessElement occurs on the OmniScript. |
| type | Field Type  string  Description  The OmniProcessElement type. For example, `Text` and `TextArea`. |
| uniqueIndex | Field Type  string  Description  The developer name of the assessment question in the OmniScript.  This field is relevant only for Omniscripts with designerCustomizationType as `discoveryframework`. |

## Declarative Metadata Sample Definition

Here’s an
example
of
an
Omniscript component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniScript
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<designerCustomizationType>Discovery Framework</designerCustomizationType>
	<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
	<elementTypeComponentMapping>{&quot;ElementTypeToHTMLTemplateList&quot;:[]}</elementTypeComponentMapping>
	<isActive>false</isActive>
	<isIntegrationProcedure>false</isIntegrationProcedure>
	<isManagedUsingStdDesigner>false</isManagedUsingStdDesigner>
	<isMetadataCacheDisabled>false</isMetadataCacheDisabled>
	<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
	<isTestProcedure>false</isTestProcedure>
	<isWebCompEnabled>true</isWebCompEnabled>
	<language>English</language>
	<name>Base Discovery Framework</name>
	<omniProcessElements>
		<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
		<isActive>true</isActive>
		<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
		<level>0.0</level>
		<name>Save-Responses</name>
		<omniProcessVersionNumber>0.0</omniProcessVersionNumber>
		<propertySetConfig>{&quot;controlWidth&quot;:12,&quot;label&quot;:&quot;Save&quot;,&quot;remoteClass&quot;:&quot;discoveryfrmwrk.StoreResponses&quot;,&quot;remoteMethod&quot;:&quot;invokeMethod&quot;,&quot;remoteOptions&quot;:{&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;},&quot;remoteTimeout&quot;:30000,&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;,&quot;sendJSONPath&quot;:&quot;&quot;,&quot;sendJSONNode&quot;:&quot;&quot;,&quot;responseJSONPath&quot;:&quot;&quot;,&quot;responseJSONNode&quot;:&quot;&quot;,&quot;extraPayload&quot;:{},&quot;inProgressMessage&quot;:&quot;In Progress&quot;,&quot;postMessage&quot;:&quot;Submitted Successfully&quot;,&quot;failureNextLabel&quot;:&quot;Continue&quot;,&quot;failureAbortLabel&quot;:&quot;Abort&quot;,&quot;failureGoBackLabel&quot;:&quot;Go Back&quot;,&quot;failureAbortMessage&quot;:&quot;Are you sure?&quot;,&quot;validationRequired&quot;:&quot;Step&quot;,&quot;redirectPageName&quot;:&quot;&quot;,&quot;redirectTemplateUrl&quot;:&quot;vlcAcknowledge.html&quot;,&quot;redirectNextLabel&quot;:&quot;Next&quot;,&quot;redirectNextWidth&quot;:3,&quot;redirectPreviousLabel&quot;:&quot;Previous&quot;,&quot;redirectPreviousWidth&quot;:3,&quot;showPersistentComponent&quot;:[true,false],&quot;show&quot;:null,&quot;HTMLTemplateId&quot;:&quot;&quot;,&quot;wpm&quot;:false,&quot;ssm&quot;:false,&quot;message&quot;:{},&quot;pubsub&quot;:false,&quot;svgSprite&quot;:&quot;&quot;,&quot;svgIcon&quot;:&quot;&quot;,&quot;errorMessage&quot;:{&quot;custom&quot;:[],&quot;default&quot;:null},&quot;enableDefaultAbort&quot;:false,&quot;enableActionMessage&quot;:false,&quot;useContinuation&quot;:false,&quot;businessCategory&quot;:&quot;&quot;,&quot;businessEvent&quot;:&quot;&quot;}</propertySetConfig>
		<sequenceNumber>1.0</sequenceNumber>
		<type>Remote Action</type>
	</omniProcessElements>
	<omniProcessElements>
		<childElements>
			<designerCustomizationType>Discovery Framework</designerCustomizationType>
			<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
			<isActive>true</isActive>
			<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
			<level>1.0</level>
			<name>Age</name>
			<omniProcessVersionNumber>0.0</omniProcessVersionNumber>
			<propertySetConfig>{&quot;controlWidth&quot;:12.0,&quot;label&quot;:&quot;Age v5&quot;,&quot;showInputWidth&quot;:false,&quot;inputWidth&quot;:12.0,&quot;required&quot;:false,&quot;repeat&quot;:false,&quot;repeatClone&quot;:false,&quot;repeatLimit&quot;:null,&quot;readOnly&quot;:false,&quot;defaultValue&quot;:null,&quot;help&quot;:false,&quot;helpText&quot;:&quot;&quot;,&quot;pattern&quot;:&quot;&quot;,&quot;ptrnErrText&quot;:&quot;&quot;,&quot;placeholder&quot;:&quot;&quot;,&quot;mask&quot;:null,&quot;show&quot;:null,&quot;conditionType&quot;:&quot;Hide if False&quot;,&quot;accessibleInFutureSteps&quot;:false,&quot;debounceValue&quot;:0.0,&quot;HTMLTemplateId&quot;:&quot;&quot;,&quot;hide&quot;:false,&quot;disOnTplt&quot;:false}</propertySetConfig>
			<sequenceNumber>2.0</sequenceNumber>
			<type>Number</type>
			<uniqueIndex>Age</uniqueIndex>
		</childElements>
		<childElements>
			<designerCustomizationType>Discovery Framework</designerCustomizationType>
			<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
			<isActive>true</isActive>
			<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
			<level>1.0</level>
			<name>First_Name</name>
			<omniProcessVersionNumber>0.0</omniProcessVersionNumber>
			<propertySetConfig>{&quot;controlWidth&quot;:12.0,&quot;label&quot;:&quot;First Name&quot;,&quot;showInputWidth&quot;:false,&quot;inputWidth&quot;:12.0,&quot;required&quot;:false,&quot;repeat&quot;:false,&quot;repeatClone&quot;:false,&quot;repeatLimit&quot;:null,&quot;readOnly&quot;:false,&quot;defaultValue&quot;:null,&quot;help&quot;:false,&quot;helpText&quot;:&quot;&quot;,&quot;mask&quot;:&quot;&quot;,&quot;pattern&quot;:&quot;&quot;,&quot;ptrnErrText&quot;:&quot;&quot;,&quot;minLength&quot;:0.0,&quot;maxLength&quot;:255.0,&quot;placeholder&quot;:&quot;&quot;,&quot;show&quot;:null,&quot;conditionType&quot;:&quot;Hide if False&quot;,&quot;accessibleInFutureSteps&quot;:false,&quot;debounceValue&quot;:0.0,&quot;HTMLTemplateId&quot;:&quot;&quot;,&quot;hide&quot;:false,&quot;disOnTplt&quot;:false}</propertySetConfig>
			<sequenceNumber>0.0</sequenceNumber>
			<type>Text</type>
			<uniqueIndex>First_Name</uniqueIndex>
		</childElements>
		<childElements>
			<designerCustomizationType>Discovery Framework</designerCustomizationType>
			<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
			<isActive>true</isActive>
			<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
			<level>1.0</level>
			<name>Last_Name</name>
			<omniProcessVersionNumber>0.0</omniProcessVersionNumber>
			<propertySetConfig>{&quot;controlWidth&quot;:12.0,&quot;label&quot;:&quot;Last Name&quot;,&quot;showInputWidth&quot;:false,&quot;inputWidth&quot;:12.0,&quot;required&quot;:false,&quot;repeat&quot;:false,&quot;repeatClone&quot;:false,&quot;repeatLimit&quot;:null,&quot;readOnly&quot;:false,&quot;defaultValue&quot;:null,&quot;help&quot;:false,&quot;helpText&quot;:&quot;&quot;,&quot;mask&quot;:&quot;&quot;,&quot;pattern&quot;:&quot;&quot;,&quot;ptrnErrText&quot;:&quot;&quot;,&quot;minLength&quot;:0.0,&quot;maxLength&quot;:255.0,&quot;placeholder&quot;:&quot;&quot;,&quot;show&quot;:null,&quot;conditionType&quot;:&quot;Hide if False&quot;,&quot;accessibleInFutureSteps&quot;:false,&quot;debounceValue&quot;:0.0,&quot;HTMLTemplateId&quot;:&quot;&quot;,&quot;hide&quot;:false,&quot;disOnTplt&quot;:false}</propertySetConfig>
			<sequenceNumber>1.0</sequenceNumber>
			<type>Text</type>
			<uniqueIndex>Last_Name</uniqueIndex>
		</childElements>
		<designerCustomizationType>Discovery Framework</designerCustomizationType>
		<discoveryFrameworkUsageType>0</discoveryFrameworkUsageType>
		<isActive>true</isActive>
		<isOmniScriptEmbeddable>false</isOmniScriptEmbeddable>
		<level>0.0</level>
		<name>Step1</name>
		<omniProcessVersionNumber>0.0</omniProcessVersionNumber>
		<propertySetConfig>{&quot;label&quot;:&quot;Base Discovery Framework&quot;,&quot;validationRequired&quot;:true,&quot;previousLabel&quot;:&quot;Previous&quot;,&quot;previousWidth&quot;:3,&quot;nextLabel&quot;:&quot;Enter&quot;,&quot;nextWidth&quot;:3,&quot;cancelLabel&quot;:&quot;Cancel&quot;,&quot;cancelMessage&quot;:&quot;Are you sure?&quot;,&quot;saveLabel&quot;:&quot;&quot;,&quot;saveMessage&quot;:&quot;&quot;,&quot;completeLabel&quot;:&quot;Complete&quot;,&quot;completeMessage&quot;:&quot;Are you sure you want to complete the script?&quot;,&quot;instruction&quot;:&quot;&quot;,&quot;showPersistentComponent&quot;:[true,false],&quot;remoteClass&quot;:&quot;&quot;,&quot;remoteMethod&quot;:&quot;&quot;,&quot;remoteTimeout&quot;:30000,&quot;remoteOptions&quot;:{},&quot;knowledgeOptions&quot;:{&quot;language&quot;:&quot;English&quot;,&quot;publishStatus&quot;:&quot;Online&quot;,&quot;keyword&quot;:&quot;&quot;,&quot;dataCategoryCriteria&quot;:&quot;&quot;,&quot;remoteTimeout&quot;:30000,&quot;typeFilter&quot;:&quot;&quot;},&quot;show&quot;:null,&quot;conditionType&quot;:&quot;Hide if False&quot;,&quot;HTMLTemplateId&quot;:&quot;&quot;,&quot;instructionKey&quot;:&quot;&quot;,&quot;chartLabel&quot;:null,&quot;allowSaveForLater&quot;:true,&quot;errorMessage&quot;:{&quot;custom&quot;:[],&quot;default&quot;:null},&quot;wpm&quot;:false,&quot;ssm&quot;:false,&quot;message&quot;:{},&quot;pubsub&quot;:false,&quot;businessCategory&quot;:&quot;&quot;,&quot;businessEvent&quot;:&quot;&quot;}</propertySetConfig>
		<sequenceNumber>0.0</sequenceNumber>
		<type>Step</type>
	</omniProcessElements>
	<omniProcessType>OmniScript</omniProcessType>
	<propertySetConfig>{&quot;persistentComponent&quot;:[{&quot;render&quot;:false,&quot;label&quot;:&quot;&quot;,&quot;remoteClass&quot;:&quot;&quot;,&quot;remoteMethod&quot;:&quot;&quot;,&quot;remoteTimeout&quot;:30000,&quot;remoteOptions&quot;:{&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;},&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;,&quot;sendJSONPath&quot;:&quot;&quot;,&quot;sendJSONNode&quot;:&quot;&quot;,&quot;responseJSONPath&quot;:&quot;&quot;,&quot;responseJSONNode&quot;:&quot;&quot;,&quot;id&quot;:&quot;vlcCart&quot;,&quot;itemsKey&quot;:&quot;cartItems&quot;,&quot;modalConfigurationSetting&quot;:{&quot;modalHTMLTemplateId&quot;:&quot;vlcProductConfig.html&quot;,&quot;modalController&quot;:&quot;ModalProductCtrl&quot;,&quot;modalSize&quot;:&quot;lg&quot;}},{&quot;render&quot;:false,&quot;dispOutsideOmni&quot;:false,&quot;label&quot;:&quot;&quot;,&quot;remoteClass&quot;:&quot;&quot;,&quot;remoteMethod&quot;:&quot;&quot;,&quot;remoteTimeout&quot;:30000,&quot;remoteOptions&quot;:{&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;},&quot;preTransformBundle&quot;:&quot;&quot;,&quot;postTransformBundle&quot;:&quot;&quot;,&quot;id&quot;:&quot;vlcKnowledge&quot;,&quot;itemsKey&quot;:&quot;knowledgeItems&quot;,&quot;modalConfigurationSetting&quot;:{&quot;modalHTMLTemplateId&quot;:&quot;&quot;,&quot;modalController&quot;:&quot;&quot;,&quot;modalSize&quot;:&quot;lg&quot;}}],&quot;allowSaveForLater&quot;:true,&quot;saveNameTemplate&quot;:null,&quot;saveExpireInDays&quot;:null,&quot;saveForLaterRedirectPageName&quot;:&quot;sflRedirect&quot;,&quot;saveForLaterRedirectTemplateUrl&quot;:&quot;vlcSaveForLaterAcknowledge.html&quot;,&quot;saveContentEncoded&quot;:false,&quot;saveObjectId&quot;:&quot;%ContextId%&quot;,&quot;saveURLPatterns&quot;:{},&quot;autoSaveOnStepNext&quot;:false,&quot;elementTypeToHTMLTemplateMapping&quot;:{},&quot;seedDataJSON&quot;:{},&quot;trackingCustomData&quot;:{},&quot;enableKnowledge&quot;:false,&quot;bLK&quot;:false,&quot;lkObjName&quot;:null,&quot;knowledgeArticleTypeQueryFieldsMap&quot;:{},&quot;timeTracking&quot;:false,&quot;hideStepChart&quot;:false,&quot;mergeSavedData&quot;:false,&quot;visualforcePagesAvailableInPreview&quot;:{},&quot;cancelType&quot;:&quot;SObject&quot;,&quot;allowCancel&quot;:true,&quot;cancelSource&quot;:&quot;%ContextId%&quot;,&quot;cancelRedirectPageName&quot;:&quot;OmniScriptCancelled&quot;,&quot;cancelRedirectTemplateUrl&quot;:&quot;vlcCancelled.html&quot;,&quot;consoleTabLabel&quot;:&quot;New&quot;,&quot;wpm&quot;:false,&quot;ssm&quot;:false,&quot;message&quot;:{},&quot;pubsub&quot;:false,&quot;autoFocus&quot;:false,&quot;currencyCode&quot;:&quot;&quot;,&quot;showInputWidth&quot;:false,&quot;rtpSeed&quot;:false,&quot;consoleTabTitle&quot;:null,&quot;consoleTabIcon&quot;:&quot;custom:custom18&quot;,&quot;errorMessage&quot;:{&quot;custom&quot;:[]},&quot;stylesheet&quot;:{&quot;newport&quot;:&quot;&quot;,&quot;lightning&quot;:&quot;&quot;,&quot;newportRtl&quot;:&quot;&quot;,&quot;lightningRtl&quot;:&quot;&quot;},&quot;stepChartPlacement&quot;:&quot;right&quot;,&quot;disableUnloadWarn&quot;:true,&quot;scrollBehavior&quot;:&quot;auto&quot;}</propertySetConfig>
	<subType>Framework</subType>
	<type>Discovery</type>
	<uniqueName>Discovery_Framework_English_1</uniqueName>
	<versionNumber>1.0</versionNumber>
</OmniScript>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package
    xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniScript</name>
    </types>
    <version>63.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information
about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").

## Usage Type

Before you retrieve or deploy Discovery Framework OmniScripts, we recommend that you
review these considerations.

- If the DesignerCustomizationType of the OmniScript is
  `discoveryframework`, then the questions
  in the OmniScript must be within the <uniqueIndex> tag in
  the metadata definition file.
- When deploying the OmniScript of type Discovery Framework, enable Discovery
  Framework Metadata Enabled setting.
- OmniScripts of type Discovery Framework don't support IDX Workbench.
- If any question associated with the OmniScript doesn’t exist in the target org
  or, if the active version of that question doesn’t exist in the target org, then
  deploying the OmniScript fails.
