---
page_id: meta.integrationprocddefinition
title: IntegrationProcdDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.integrationprocddefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
fetched_at: 2026-11-25
---

# IntegrationProcdDefinition

Represents an Integration Procedure’s header configurations, including its type and subtype. Integration Procedures bundle server-side data operations for efficiency. They act as data sources in Flexcards and as actions in Omniscripts.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

IntegrationProcdDefinition components have the suffix `.integrationProcdDefinition` and are stored in the `integrationProcdDefinitions` folder.

## Version

IntegrationProcdDefinition components are available in API version 67.0 and later.

## Special Access Rules

## Fields

### cleanResponseCacheType

- **Field Type**: CleanResponseCacheType

- **Description**: Specifies the cache type used to store response data for this definition.

### description

- **Field Type**: string

- **Description**: The user-defined description added to an Integration Procedure.

### integProcdName

- **Field Type**: string

- **Description**: The user-defined name of the Integration Procedure.

### integrationProcdDefElmnt

- **Field Type**: [IntegrationProcdDefElmnt](#integrationprocddefelmnt)

- **Description**: The Integration Procedure elements associated with this Integration Procedure definition.

### integrationProcedureDefKey

- **Field Type**: string

- **Description**: The unique identifier of an Integration Procedure.

### integrationProcedureInput

- **Field Type**: string

- **Description**: The input for the Integration Procedure in the JSON format.

### integrationProcedureOutput

- **Field Type**: string

- **Description**: The output of the Integration Procedure in the JSON format.

### integrationProcedureType

- **Field Type**: IntegrationProcedureType

- **Description**: Specifies the type of procedure configuration applied to the referenced component to indicate whether it’s an Integration Procedure or a Test Procedure.

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure is being used or is ready to be used at runtime (`true`) or not (`false`).

### isIntegProcdSignatureAvl

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure has a signature (`true`) or not (`false`).

### isManagedUsingStdDesigner

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure is created or updated using the Omnistudio standard designer (`true`) or not (`false`).

### isMetadataCacheDisabled

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure’s definition is cached (`true`) or not (`false`).

### masterLabel

- **Field Type**: string

- **Description**: The user-defined label of the component.

### overrideKey

- **Field Type**: string

- **Description**: The unique identifier of the Integration Procedure that’s being overridden.

### propertySetConfig

- **Field Type**: [IntegrationProcedurePropertySetConfig](#integrationprocedurepropertysetconfig)

- **Description**: Stores the configuration properties for this component.

### references

- **Field Type**: string

- **Description**: The list of referenced components used by this definition.

### requiredPermission

- **Field Type**: string

- **Description**: The list of custom permissions that allow a user to execute an Integration Procedure.

### subType

- **Field Type**: string

- **Description**: A user-defined value, that together with Type forms the unique identifier for an Integration Procedure.

### type

- **Field Type**: string

- **Description**: A user-defined value, that together with Subtype forms the unique identifier for an Integration Procedure.

## IntegrationProcdDefElmnt

### description

- **Field Type**: string

- **Description**: The user-defined description added to an Integration Procedure.

### integProcdDefElmntName

- **Field Type**: string

- **Description**: The name of the element in the Integration Procedure.

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure is being used or is ready to be used at runtime (`true`) or not (`false`).

### level

- **Field Type**: double

- **Description**: Defines the element’s depth in the Integration Procedure when it’s nested within other elements.

### parentElementName

- **Field Type**: string

- **Description**: The name of the parent element associated with this element.

### parentElementType

- **Field Type**: IntegProcdElementType

- **Description**: The type of the parent element associated with this element.

### propertySetConfig

- **Field Type**: [IntegrationProcedureElementPropertySetConfig](#integrationprocedureelementpropertysetconfig)

- **Description**: Stores the configuration properties for this component.

### sequenceNumber

- **Field Type**: double

- **Description**: Defines the element’s position in relation to its sibling elements in the Integration Procedure’s configuration.

### type

- **Field Type**: IntegProcdElementType

- **Description**: A user-defined value, that together with Subtype forms the unique identifier for an Integration Procedure.

## IntegrationProcedureElementPropertySetConfig

### actionMessage

- **Field Type**: string

- **Description**: Specifies the message shown or logged for this action.

### addToCacheConditionalFormula

- **Field Type**: string

- **Description**: Specifies the formula that determines whether output must be cached.

### additionalChainableResponse

- **Field Type**: string

- **Description**: Specifies additional response data returned when chainable execution is used.

### additionalInput

- **Field Type**: string

- **Description**: The input data used for additional input.

### additionalOutput

- **Field Type**: string

- **Description**: The output data used for additional output.

### assertConditionalFormula

- **Field Type**: string

- **Description**: Specifies the formula condition that’s used for assertion checks.

### assertFailureMessage

- **Field Type**: string

- **Description**: Specifies the message returned when an assertion fails.

### attachmentList

- **Field Type**: string

- **Description**: The list of values that’s used for attachment list.

### bundle

- **Field Type**: string

- **Description**: Specifies the referenced bundle or component for this action.

### cacheBlockOutput

- **Field Type**: string

- **Description**: The output data used for cache block output.

### cacheKeys

- **Field Type**: string

- **Description**: The unique key for cache keys.

### cacheType

- **Field Type**: string

- **Description**: The type value for cache type.

### chainOnStep

- **Field Type**: boolean

- **Description**: Indicates whether chain on step is enabled (`true`) or not (`false`).

### communityId

- **Field Type**: string

- **Description**: Specifies the Experience Cloud site or community identifier context.

### contentVersionList

- **Field Type**: string

- **Description**: The list of values that’s used for content version list.

### dataRaptorInputParameters

- **Field Type**: string

- **Description**: The input data used for data raptor input parameters.

### deleteSObject

- **Field Type**: string

- **Description**: Specifies the target sObject configuration for delete operations.

### disOnTplt

- **Field Type**: boolean

- **Description**: Indicates whether the element is disabled when the integration procedure is used as a template. If set to `true`, the element is not available for execution in template mode.

### disableChainable

- **Field Type**: boolean

- **Description**: Indicates whether to disable Chainable (`true`) or keep it enabled (`false`).

### dynamicProperties

- **Field Type**: string

- **Description**: Stores dynamic properties used at runtime.

### elementValueMap

- **Field Type**: string

- **Description**: The key-value mappings used for element value map.

### emailInformation

- **Field Type**: string

- **Description**: Stores email action configuration details.

### emailTemplateInformation

- **Field Type**: string

- **Description**: Stores email template configuration details.

### executionConditionalFormula

- **Field Type**: string

- **Description**: Specifies the formula that controls whether this action executes.

### failOnBlockError

- **Field Type**: boolean

- **Description**: Indicates whether execution stops when a block encounters an error (`true`) or not (`false`).

### failOnStepError

- **Field Type**: boolean

- **Description**: Indicates whether execution stops when a step encounters an error (`true`) or not (`false`).

### failureConditionalFormula

- **Field Type**: string

- **Description**: Specifies the formula that determines whether a failure response is returned.

### failureResponse

- **Field Type**: string

- **Description**: Specifies the response payload returned when this action fails.

### fileId

- **Field Type**: string

- **Description**: Specifies the file identifier used by this action.

### id

- **Field Type**: string

- **Description**: Specifies the unique identifier value for the element configuration item.

### ignoreCache

- **Field Type**: boolean

- **Description**: Indicates whether cached date is ignored during execution (`true`) or not (`false`).

### ignoreCacheConditionalFormula

- **Field Type**: string

- **Description**: Specifies the condition that determines when cache is ignored.

### imageId

- **Field Type**: string

- **Description**: Specifies the image identifier used by this action.

### inputData

- **Field Type**: string

- **Description**: Specifies the input data, typically as a JSON object or expression, that is passed to the element for processing during execution.

### integrationProcedureKey

- **Field Type**: string

- **Description**: The unique key for integration procedure key.

### integrationProcedureRootConfig

- **Field Type**: [IntegrationProcedurePropertySetConfig](#integrationprocedurepropertysetconfig)

- **Description**: Stores root-level Integration Procedure configuration properties.

### internalNotes

- **Field Type**: string

- **Description**: Stores internal notes associated with this action configuration.

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether the Integration Procedure is being used or is ready to be used at runtime (`true`) or not (`false`).

### isIfElseBlock

- **Field Type**: boolean

- **Description**: Indicates whether the element represents an If/Else block (`true`) or not (`false`).

### loopList

- **Field Type**: string

- **Description**: The collection of items to iterate over.

### loopOutput

- **Field Type**: string

- **Description**: Specifies where the output from each loop iteration is stored.

### markupType

- **Field Type**: string

- **Description**: Specifies the markup format used for the content.

### mentionedUserId

- **Field Type**: string

- **Description**: Specifies the user identifier referenced in mentions or notifications.

### namedCredential

- **Field Type**: string

- **Description**: Specifies the named credential used for authentication.

### orgWideEmailAddress

- **Field Type**: string

- **Description**: Specifies the org-wide email address used for outbound email.

### postActionLogging

- **Field Type**: string

- **Description**: Configures logging behavior after action execution.

### preActionLogging

- **Field Type**: string

- **Description**: Configures logging behavior before action execution.

### refreshCacheConditionalFormula

- **Field Type**: string

- **Description**: Specifies the formula that determines when cache is refreshed.

### remoteClass

- **Field Type**: string

- **Description**: Specifies the Apex class invoked for remote action execution.

### remoteMethod

- **Field Type**: string

- **Description**: Specifies the method invoked for remote action execution.

### remoteOptions

- **Field Type**: string

- **Description**: Specifies additional options used for remote action execution.

### responseFormat

- **Field Type**: string

- **Description**: Specifies the expected response format for this action.

### responseJSONNode

- **Field Type**: string

- **Description**: Specifies the response JSON node targeted by this action.

### responseJSONPath

- **Field Type**: string

- **Description**: Specifies the response JSON path targeted by this action.

### restMethod

- **Field Type**: string

- **Description**: Specifies the HTTP method used for REST callouts.

### restOptions

- **Field Type**: string

- **Description**: Specifies additional REST callout options.

### restPath

- **Field Type**: string

- **Description**: Specifies the REST endpoint path used for callouts.

### retryCount

- **Field Type**: string

- **Description**: Specifies how many retries are attempted when this action fails.

### returnFullDataJSON

- **Field Type**: boolean

- **Description**: Indicates whether the complete response payload is returned (`true`) or not (`false`).

### returnOnlyAdditionalOutput

- **Field Type**: boolean

- **Description**: Indicates whether only the additional output values are returned (`true`) or not (`false`).

### returnOnlyFailureResponse

- **Field Type**: boolean

- **Description**: Indicates whether only the failure response is returned when execution fails (`true`) or not (`false`).

### sendJSONNode

- **Field Type**: string

- **Description**: Specifies the JSON node extracted from input for outbound payload.

### sendJSONPath

- **Field Type**: string

- **Description**: Specifies the JSON path extracted from input for outbound payload.

### sendOnlyAdditionalInput

- **Field Type**: boolean

- **Description**: Indicates whether only the additional input values are sent in the request (`true`) or not (`false`).

### subjectId

- **Field Type**: string

- **Description**: Specifies the subject record identifier used by this action.

### text

- **Field Type**: string

- **Description**: Specifies the text content configured for this element.

### ttlMinutes

- **Field Type**: string

- **Description**: Specifies the cache time-to-live in minutes.

### useFormulas

- **Field Type**: boolean

- **Description**: Indicates whether formulas are evaluated during execution (`true`) or not (`false`).

### useTemplate

- **Field Type**: boolean

- **Description**: Indicates whether a template is used by the action (`true`) or not (`false`).

### vlcResponseHeaders

- **Field Type**: string

- **Description**: Stores response header mappings for VLC runtime responses.

## IntegrationProcedurePropertySetConfig

### additionalChainableResponse

- **Field Type**: string

- **Description**: Specifies additional response data returned when chainable execution is used.

### autoSaveOnStepNext

- **Field Type**: boolean

- **Description**: Indicates whether changes are automatically saved when moving to the next step (`true`) or not (`false`).

### chainableActualTimeLimit

- **Field Type**: int

- **Description**: Specifies the maximum execution time, in milliseconds, allowed for a chainable process.

### chainableCpuLimit

- **Field Type**: int

- **Description**: Specifies the maximum CPU time allowed for a chainable process.

### chainableDMLRowsLimit

- **Field Type**: int

- **Description**: Specifies the maximum number of DML rows that a chainable process can process.

### chainableDMLStatementsLimit

- **Field Type**: int

- **Description**: Specifies the maximum number of DML statements that a chainable process can execute.

### chainableHeapSizeLimit

- **Field Type**: int

- **Description**: Specifies the heap size limit for chainable execution.

### chainableQueriesLimit

- **Field Type**: int

- **Description**: Specifies the maximum number of SOQL queries that a chainable process can execute.

### chainableQueryRowsLimit

- **Field Type**: int

- **Description**: Specifies the maximum number of rows that SOQL queries can return in a chainable process..

### chainableSoslQueriesLimit

- **Field Type**: int

- **Description**: Specifies the SOSL query limit for chainable execution.

### columnsPropertyMap

- **Field Type**: string

- **Description**: The key-value mappings used for columns property map.

### description

- **Field Type**: string

- **Description**: The user-defined description added to an Integration Procedure.

### disableDefinitionCache

- **Field Type**: boolean

- **Description**: Indicates whether caching of the integration procedure definition is disabled (`true`) or keep it enabled (`false`).

### dynamicProperties

- **Field Type**: string

- **Description**: Stores dynamic properties used at runtime.

### includeAllActionsInResponse

- **Field Type**: boolean

- **Description**: Indicates whether responses from all actions are included in the integration procedure output (`true`) or not (`false`).

### integrationProcedureInput

- **Field Type**: string

- **Description**: The expected input schema or structure for the integration procedure.

### integrationProcedureOutput

- **Field Type**: string

- **Description**: The output of the integration procedure in the JSON format.

### isIntegProcdSignatureAvl

- **Field Type**: string

- **Description**: Indicates whether the Integration Procedure has a signature (`true`) or not (`false`).

### labelPlural

- **Field Type**: string

- **Description**: Specifies the plural label used by this configuration.

### labelSingular

- **Field Type**: string

- **Description**: Specifies the singular label used by this configuration.

### linkToExternalObject

- **Field Type**: string

- **Description**: Specifies the external object mapping used by this configuration.

### mockResponseMap

- **Field Type**: string

- **Description**: The key-value mappings used for mock response map.

### nameColumn

- **Field Type**: string

- **Description**: Specifies the field used as the primary display name.

### omniProcessId

- **Field Type**: string

- **Description**: Specifies the ID of the associated OmniStudio process.

### persistentComponent

- **Field Type**: boolean

- **Description**: Indicates whether the component remains persistent across interactions. (`true`) or not (`false`).

### queueableChainableCpuLimit

- **Field Type**: int

- **Description**: Specifies the CPU limit for queueable chainable execution.

### queueableChainableHeapSizeLimit

- **Field Type**: int

- **Description**: Specifies the heap size limit for queueable chainable execution.

### queueableChainableQueriesLimit

- **Field Type**: int

- **Description**: Specifies the SOQL query count limit for queueable chainable execution.

### relationshipFieldsMap

- **Field Type**: string

- **Description**: The key-value mappings used for relationship fields map.

### requiredPermission

- **Field Type**: string

- **Description**: The list of custom permissions that allow a user to execute an Integration Procedure.

### rollbackOnError

- **Field Type**: boolean

- **Description**: Indicates whether all changes are rolled back if an error occurs during execution (`true`) or not (`false`).

### trackingCustomData

- **Field Type**: string

- **Description**: Stores custom tracking data emitted by this component.

### transientValues

- **Field Type**: string

- **Description**: Stores transient (non-persisted) runtime values.

### ttlMinutes

- **Field Type**: int

- **Description**: Specifies the cache time-to-live in minutes.

## Declarative Metadata Sample Definition

The following is an example of a IntegrationProcdDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<IntegrationProcdDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <integProcdName>TestIntegrationProcedure</integProcdName>
    <integrationProcdDefElmnt>
        <description>First action element</description>
        <integProcdDefElmntName>Action1</integProcdDefElmntName>
        <isActive>true</isActive>
        <level>0.0</level>
        <sequenceNumber>1.0</sequenceNumber>
        <type>Set Values</type>
    </integrationProcdDefElmnt>
    <integrationProcedureDefKey>TestType_TestSubType</integrationProcedureDefKey>
    <integrationProcedureType>Integration Procedure</integrationProcedureType>
    <isActive>true</isActive>
    <isIntegProcdSignatureAvl>true</isIntegProcdSignatureAvl>
    <isManagedUsingStdDesigner>true</isManagedUsingStdDesigner>
    <isMetadataCacheDisabled>false</isMetadataCacheDisabled>
    <masterLabel>TestType_TestSubType_English</masterLabel>
    <references>[]</references>
    <subType>TestSubType</subType>
    <type>TestType</type>
</IntegrationProcdDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>IntegrationProcdDefinition</name>
    </types>
    <version>[ftest]</version>
</Package>
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.integrationprocddefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
