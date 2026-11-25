---
page_id: meta.flexcarddefinition
title: FlexcardDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.flexcarddefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
fetched_at: 2026-11-25
---

# FlexcardDefinition

Each row represents a Flexcard’s configuration such as its name and author. A Flexcard can display data and launch actions or Omniscripts. This object stores specific information about a Flexcard to render it at runtime.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

FlexcardDefinition components have the suffix `.flexcardDefinition` and are stored in the `flexcardDefinitions` folder.

## Version

FlexcardDefinition components are available in API version 67.0 and later.

## Special Access Rules

## Fields

### authorName

- **Field Type**: string

- **Description**: A value that identifies who created the Flexcard. This value could indicate the name of the user, team, or company of the Flexcard’s creator.

### clonedFromFlexcardKey

- **Field Type**: string

- **Description**: The Flexcard Definition Key of the Flexcard used to create this Flexcard.

### dataSourceConfiguration

- **Field Type**: string

- **Description**: A user-defined method that’s used for populating the Flexcard with data.

### description

- **Field Type**: string

- **Description**: The user-defined text added in the Description field when creating or updating a Flexcard.

### flexcardKey

- **Field Type**: string

- **Description**: The unique identifier of a Flexcard.

### flexcardType

- 

**Field Type**: FlexcardType (enumeration of type string)

- 

**Description**: The Flexcard category that defines where the Flexcard can be used, for example, inside another Flexcard, or in Salesforce Pages.

- 

**Values**: Values are:

  - `Parent`

  - `Child`

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether this Flexcard version is the currently active version (`true`) or not (`false`). The currently active version is the one that executes at runtime.

### isManagedUsingStdDesigner

- **Field Type**: boolean

- **Description**: Indicates whether the Flexcard is created or updated using the Omnistudio standard designer.

### isTrackingEnabled

- **Field Type**: boolean

- **Description**: Indicates whether the Flexcard reports to tracking services (`true`) or not (`false`).

### masterLabel

- **Field Type**: string

- **Description**: The user-defined label of the component.

### overrideKey

- **Field Type**: string

- **Description**: The unique identifier of the Flexcards that’s being overriden.

### propertySetConfig

- **Field Type**: [FlexcardPropertySetConfig](#flexcardpropertysetconfig)

- **Description**: Stores the configuration properties for this component.

### references

- **Field Type**: string

- **Description**: The list of referenced components used by this definition.

### sampleDataSourceResponse

- **Field Type**: string

- **Description**: The user-defined sample data used when previewing a Flexcard so the current design can be tested with this data.

### stylingConfiguration

- **Field Type**: string

- **Description**: The custom CSS classes defined for the Flexcard.

## FlexcardPropertySetConfig

### accessibilityToggle

- **Field Type**: boolean

- **Description**: Indicates whether accessibility features are enabled for the Flexcard (`true`) or not (`false`).

### dataSource

- **Field Type**: string

- **Description**: The data source used to populate the Flexcard.

### dynamicProperties

- **Field Type**: string

- **Description**: Specifies dynamically resolved property values used during rendering or execution.

### enableLwc

- **Field Type**: boolean

- **Description**: Indicates whether the Flexcard is rendered as a Lightning Web Component (`true`) or disable it (`false`).

### integrationProcedureRootConfig

- **Field Type**: [IntegrationProcedurePropertySetConfig](#integrationprocedurepropertysetconfig)

- **Description**: Specifies the root configuration of the integration procedure associated with the Flexcard.

### isFlex

- **Field Type**: boolean

- **Description**: Indicates whether the component is configured as a Flexcard (`true`) or not (`false`).

### omniScriptRootConfig

- **Field Type**: [OmniScriptPropertySetConfig](#omniscriptpropertysetconfig)

- **Description**: Specifies the root configuration of the associated Omniscript.

### selectableMode

- **Field Type**: string

- **Description**: Specifies how selection behavior is handled for this component.

### states

- **Field Type**: [FlexcardStatePropertySetConfig](#flexcardstatepropertysetconfig)

- **Description**: Stores the state configurations for this Flexcard.

### theme

- **Field Type**: string

- **Description**: Specifies the visual theme applied to this component.

### title

- **Field Type**: string

- **Description**: Specifies the display title configured for this component.

### xmlObject

- **Field Type**: string

- **Description**: Stores the generated XML configuration used by this component.

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

## OmniScriptPropertySetConfig

### accessibilityToggle

- **Field Type**: boolean

- **Description**: Indicates whether accessibility toggle is enabled for the Omniscript configuration.

### allowCancel

- **Field Type**: boolean

- **Description**: Indicates whether cancel is enabled for this Omniscript configuration.

### allowSaveChanges

- **Field Type**: boolean

- **Description**: Indicates whether users can save changes made in the Omniscript element.

### allowSaveForLater

- **Field Type**: boolean

- **Description**: Indicates whether users can save progress and resume the Omniscript later.

### autoFocus

- **Field Type**: boolean

- **Description**: Indicates whether auto focus is enabled for the Omniscript configuration.

### autoSaveChanges

- **Field Type**: boolean

- **Description**: Indicates whether auto save changes is enabled for the Omniscript configuration.

### autoSaveOnStepNext

- **Field Type**: boolean

- **Description**: Indicates whether auto save on step next is enabled for the Omniscript configuration.

### bulk

- **Field Type**: boolean

- **Description**: Indicates whether bulk is enabled for the Omniscript configuration.

### cancelRedirectPageName

- **Field Type**: string

- **Description**: The cancel redirect page name used to identify this Omniscript artifact in metadata.

### cancelRedirectTemplateUrl

- **Field Type**: string

- **Description**: The cancel redirect template url reference used by Omniscript integrations or rendering.

### cancelSource

- **Field Type**: string

- **Description**: The cancel source that identifies the data source or target used by Omniscript.

### cancelType

- **Field Type**: string

- **Description**: The cancel type value that determines how this Omniscript setting is interpreted.

### consoleTabIcon

- **Field Type**: string

- **Description**: The console tab icon value used by Omniscript at runtime.

### consoleTabLabel

- **Field Type**: string

- **Description**: The console tab label text shown in the Omniscript user interface.

### consoleTabTitle

- **Field Type**: string

- **Description**: The console tab title text shown in the Omniscript user interface.

### currencyCode

- **Field Type**: string

- **Description**: The currency code value used by Omniscript at runtime.

### currentLanguage

- **Field Type**: string

- **Description**: The current language value used by Omniscript at runtime.

### disableUnloadWarn

- **Field Type**: boolean

- **Description**: Indicates whether disable unload warn is enabled for the Omniscript configuration.

### dynamicProperties

- **Field Type**: string

- **Description**: The dynamic properties used to configure Omniscript behavior.

### elementTypeToHTMLTemplateMapping

- **Field Type**: string

- **Description**: The element type to htmltemplate mapping value that determines how this Omniscript setting is interpreted.

### enableKnowledge

- **Field Type**: boolean

- **Description**: Indicates whether knowledge is enabled for this Omniscript configuration.

### errorMessage

- **Field Type**: string

- **Description**: The error message text shown in the Omniscript user interface.

### hideStepChart

- **Field Type**: boolean

- **Description**: Indicates whether hide step chart is enabled for the Omniscript configuration.

### knowledgeArticleTypeQueryFieldsMap

- **Field Type**: string

- **Description**: The knowledge article type query fields map value that determines how this Omniscript setting is interpreted.

### lkObjName

- **Field Type**: string

- **Description**: The lk obj name used to identify this Omniscript artifact in metadata.

### mergeSavedData

- **Field Type**: boolean

- **Description**: Indicates whether merge saved data is enabled for the Omniscript configuration.

### message

- **Field Type**: string

- **Description**: The message text shown in the Omniscript user interface.

### persistentComponent

- **Field Type**: string

- **Description**: The persistent component value used by Omniscript at runtime.

### pubsub

- **Field Type**: boolean

- **Description**: Indicates whether pubsub is enabled for the Omniscript configuration.

### rtpSeed

- **Field Type**: boolean

- **Description**: Indicates whether rtp seed is enabled for the Omniscript configuration.

### saveContentEncoded

- **Field Type**: boolean

- **Description**: Indicates whether save content encoded is enabled for the Omniscript configuration.

### saveExpireInDays

- **Field Type**: int

- **Description**: The save expire in days value used by Omniscript at runtime.

### saveForLaterRedirectPageName

- **Field Type**: string

- **Description**: The save for later redirect page name used to identify this Omniscript artifact in metadata.

### saveForLaterRedirectTemplateUrl

- **Field Type**: string

- **Description**: The save for later redirect template url reference used by Omniscript integrations or rendering.

### saveNameTemplate

- **Field Type**: string

- **Description**: The save name template used to identify this Omniscript artifact in metadata.

### saveObjectId

- **Field Type**: string

- **Description**: The object ID used when saving Omniscript data.

### saveURLPatterns

- **Field Type**: string

- **Description**: The save urlpatterns value used by Omniscript at runtime.

### scrollBehavior

- **Field Type**: string

- **Description**: The scroll behavior value used by Omniscript at runtime.

### seedDataJSON

- **Field Type**: string

- **Description**: The seed data json value used by Omniscript at runtime.

### showInputWidth

- **Field Type**: boolean

- **Description**: Indicates whether show input width is enabled for the Omniscript configuration.

### ssm

- **Field Type**: boolean

- **Description**: Indicates whether ssm is enabled for the Omniscript configuration.

### stepChartPlacement

- **Field Type**: string

- **Description**: The step chart placement value used by Omniscript at runtime.

### stylesheet

- **Field Type**: string

- **Description**: The stylesheet value used by Omniscript at runtime.

### timeTracking

- **Field Type**: boolean

- **Description**: Indicates whether time tracking is enabled for the Omniscript configuration.

### trackingCustomData

- **Field Type**: string

- **Description**: The tracking custom data value used by Omniscript at runtime.

### visualforcePagesAvailableInPreview

- **Field Type**: string

- **Description**: The visualforce pages available in preview value used by Omniscript at runtime.

### wpm

- **Field Type**: boolean

- **Description**: Indicates whether wpm is enabled for the Omniscript configuration.

## FlexcardStatePropertySetConfig

### actions

- **Field Type**: string

- **Description**: Stores action definitions configured for the state.

### blankCardState

- **Field Type**: boolean

- **Description**: Indicates whether the state is displayed when no data is available (`true`) or not (`false`).

### childCards

- **Field Type**: string

- **Description**: Stores child card configurations associated with the state.

### components

- **Field Type**: string

- **Description**: Stores component definitions configured for the state.

### conditions

- **Field Type**: string

- **Description**: Stores condition rules that control the state.

### definedActions

- **Field Type**: string

- **Description**: Stores predefined actions available in the state.

### documents

- **Field Type**: string

- **Description**: Stores document-related configurations used in the state.

### dynamicProperties

- **Field Type**: string

- **Description**: Stores dynamic properties used at runtime.

### fields

- **Field Type**: string

- **Description**: Stores field configurations displayed in this state.

### isSmartAction

- **Field Type**: boolean

- **Description**: Indicates whether the state includes a smart action (`true`) or not (`false`).

### name

- **Field Type**: string

- **Description**: Specifies the configured name of this item.

### omniscripts

- **Field Type**: string

- **Description**: Stores related Omniscript references configured in this state.

### smartAction

- **Field Type**: string

- **Description**: Stores smart action configuration for the state.

### styleObject

- **Field Type**: string

- **Description**: Defines styling properties (for example, classes, spacing, and sizing) used to render this component.

## Declarative Metadata Sample Definition

The following is an example of a FlexcardDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<FlexcardDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <authorName>TestAuthor</authorName>
    <dataSourceConfiguration>{&quot;dataSource&quot;:{&quot;type&quot;:null,&quot;value&quot;:{},&quot;orderBy&quot;:{},&quot;contextVariables&quot;:[]}}</dataSourceConfiguration>
    <description>Test Flexcard Definition for Metadata Gauntlet</description>
    <flexcardKey>TestFlexcardDefinition/TestAuthor</flexcardKey>
    <flexcardType>Parent</flexcardType>
    <isActive>true</isActive>
    <isManagedUsingStdDesigner>true</isManagedUsingStdDesigner>
    <isTrackingEnabled>false</isTrackingEnabled>
    <masterLabel>TestFlexcardDefinition_TestAuthor</masterLabel>
    <propertySetConfig>
        <states>
            <fields>[]</fields>
            <conditions>{&quot;id&quot;:&quot;state-condition-object&quot;,&quot;isParent&quot;:true,&quot;group&quot;:[]}</conditions>
            <definedActions>{&quot;actions&quot;:[]}</definedActions>
            <name>Active</name>
            <isSmartAction>false</isSmartAction>
            <smartAction>{}</smartAction>
            <styleObject>{&quot;padding&quot;:[{&quot;type&quot;:&quot;around&quot;,&quot;size&quot;:&quot;x-small&quot;}],&quot;margin&quot;:[{&quot;type&quot;:&quot;bottom&quot;,&quot;size&quot;:&quot;x-small&quot;}],&quot;container&quot;:{&quot;class&quot;:&quot;slds-card&quot;},&quot;size&quot;:{&quot;isResponsive&quot;:false,&quot;default&quot;:&quot;12&quot;},&quot;sizeClass&quot;:&quot;slds-size_12-of-12&quot;,&quot;class&quot;:&quot;slds-card slds-p-around_x-small slds-m-bottom_x-small&quot;}</styleObject>
            <components>{&quot;layer-0&quot;:{&quot;children&quot;:[{&quot;name&quot;:&quot;Text&quot;,&quot;element&quot;:&quot;outputField&quot;,&quot;size&quot;:{&quot;isResponsive&quot;:false,&quot;default&quot;:&quot;12&quot;},&quot;stateIndex&quot;:0,&quot;class&quot;:&quot;slds-col &quot;,&quot;property&quot;:{&quot;record&quot;:&quot;{record}&quot;,&quot;mergeField&quot;:&quot;Test&quot;,&quot;card&quot;:&quot;{card}&quot;},&quot;type&quot;:&quot;text&quot;,&quot;styleObject&quot;:{&quot;sizeClass&quot;:&quot;slds-size_12-of-12&quot;},&quot;datasourceKey&quot;:&quot;state0element0&quot;,&quot;uKey&quot;:&quot;1767799962280-500&quot;,&quot;elementLabel&quot;:&quot;Text-0&quot;}]}}</components>
            <childCards>[]</childCards>
            <actions>[]</actions>
            <omniscripts>[]</omniscripts>
            <documents>[]</documents>
            <dynamicProperties></dynamicProperties>
            <blankCardState>false</blankCardState>
        </states>
        <dataSource>{&quot;type&quot;:null,&quot;value&quot;:{},&quot;orderBy&quot;:{},&quot;contextVariables&quot;:[]}</dataSource>
        <title>TestFlexcardDefinition</title>
        <enableLwc>true</enableLwc>
        <isFlex>true</isFlex>
        <theme>slds</theme>
        <selectableMode>Multi</selectableMode>
        <accessibilityToggle>true</accessibilityToggle>
        <xmlObject>{&quot;targetConfigs&quot;:&quot;PHRhcmdldENvbmZpZyB0YXJnZXRzPSJsaWdodG5pbmdfX0FwcFBhZ2UiPgogICAgICAgICAgICAgICAgICAgIDxwcm9wZXJ0eSBuYW1lPSJkZWJ1ZyIgdHlwZT0iQm9vbGVhbiIvPgogICAgICAgICAgICAgICAgICAgIDxwcm9wZXJ0eSBuYW1lPSJyZWNvcmRJZCIgdHlwZT0iU3RyaW5nIi8+CiAgICAgICAgICAgICAgICA8L3RhcmdldENvbmZpZz4KICAgICAgICAgICAgICAgIDx0YXJnZXRDb25maWcgdGFyZ2V0cz0ibGlnaHRuaW5nX19SZWNvcmRQYWdlIj4KICAgICAgICAgICAgICAgICAgICA8cHJvcGVydHkgbmFtZT0iZGVidWciIHR5cGU9IkJvb2xlYW4iLz4KICAgICAgICAgICAgICAgIDwvdGFyZ2V0Q29uZmlnPg==&quot;,&quot;targets&quot;:{&quot;target&quot;:[&quot;lightning__RecordPage&quot;,&quot;lightning__AppPage&quot;,&quot;lightning__HomePage&quot;]},&quot;apiVersion&quot;:61,&quot;description&quot;:&quot;&quot;}</xmlObject>
        <dynamicProperties></dynamicProperties>
        <integrationProcedureRootConfig>
            <mockResponseMap></mockResponseMap>
            <omniProcessId></omniProcessId>
            <linkToExternalObject></linkToExternalObject>
            <integrationProcedureOutput></integrationProcedureOutput>
            <additionalChainableResponse></additionalChainableResponse>
            <relationshipFieldsMap></relationshipFieldsMap>
            <integrationProcedureInput></integrationProcedureInput>
            <description></description>
            <trackingCustomData></trackingCustomData>
            <requiredPermission></requiredPermission>
            <nameColumn></nameColumn>
            <columnsPropertyMap></columnsPropertyMap>
            <isIntegProcdSignatureAvl></isIntegProcdSignatureAvl>
            <transientValues></transientValues>
            <labelSingular></labelSingular>
            <labelPlural></labelPlural>
            <dynamicProperties></dynamicProperties>
            <autoSaveOnStepNext>false</autoSaveOnStepNext>
            <persistentComponent>false</persistentComponent>
            <includeAllActionsInResponse>false</includeAllActionsInResponse>
            <rollbackOnError>false</rollbackOnError>
            <disableDefinitionCache>false</disableDefinitionCache>
            <chainableQueryRowsLimit>0</chainableQueryRowsLimit>
            <ttlMinutes>0</ttlMinutes>
            <chainableHeapSizeLimit>0</chainableHeapSizeLimit>
            <queueableChainableQueriesLimit>0</queueableChainableQueriesLimit>
            <queueableChainableHeapSizeLimit>0</queueableChainableHeapSizeLimit>
            <chainableActualTimeLimit>0</chainableActualTimeLimit>
            <chainableDMLRowsLimit>0</chainableDMLRowsLimit>
            <chainableDMLStatementsLimit>0</chainableDMLStatementsLimit>
            <chainableSoslQueriesLimit>0</chainableSoslQueriesLimit>
            <chainableQueriesLimit>0</chainableQueriesLimit>
            <queueableChainableCpuLimit>0</queueableChainableCpuLimit>
            <chainableCpuLimit>0</chainableCpuLimit>
        </integrationProcedureRootConfig>
        <omniScriptRootConfig>
            <cancelRedirectPageName></cancelRedirectPageName>
            <currencyCode></currencyCode>
            <consoleTabLabel></consoleTabLabel>
            <cancelRedirectTemplateUrl></cancelRedirectTemplateUrl>
            <lkObjName></lkObjName>
            <stylesheet></stylesheet>
            <consoleTabIcon></consoleTabIcon>
            <consoleTabTitle></consoleTabTitle>
            <saveURLPatterns></saveURLPatterns>
            <seedDataJSON></seedDataJSON>
            <cancelSource></cancelSource>
            <stepChartPlacement></stepChartPlacement>
            <currentLanguage></currentLanguage>
            <scrollBehavior></scrollBehavior>
            <message></message>
            <visualforcePagesAvailableInPreview></visualforcePagesAvailableInPreview>
            <saveForLaterRedirectTemplateUrl></saveForLaterRedirectTemplateUrl>
            <saveNameTemplate></saveNameTemplate>
            <saveForLaterRedirectPageName></saveForLaterRedirectPageName>
            <errorMessage></errorMessage>
            <dynamicProperties></dynamicProperties>
            <trackingCustomData></trackingCustomData>
            <persistentComponent></persistentComponent>
            <cancelType></cancelType>
            <elementTypeToHTMLTemplateMapping></elementTypeToHTMLTemplateMapping>
            <knowledgeArticleTypeQueryFieldsMap></knowledgeArticleTypeQueryFieldsMap>
            <saveObjectId></saveObjectId>
            <mergeSavedData>false</mergeSavedData>
            <allowSaveChanges>false</allowSaveChanges>
            <showInputWidth>false</showInputWidth>
            <allowCancel>false</allowCancel>
            <allowSaveForLater>false</allowSaveForLater>
            <hideStepChart>false</hideStepChart>
            <rtpSeed>false</rtpSeed>
            <disableUnloadWarn>false</disableUnloadWarn>
            <autoSaveChanges>false</autoSaveChanges>
            <autoFocus>false</autoFocus>
            <enableKnowledge>false</enableKnowledge>
            <autoSaveOnStepNext>false</autoSaveOnStepNext>
            <ssm>false</ssm>
            <saveContentEncoded>false</saveContentEncoded>
            <pubsub>false</pubsub>
            <bulk>false</bulk>
            <accessibilityToggle>false</accessibilityToggle>
            <timeTracking>false</timeTracking>
            <wpm>false</wpm>
            <saveExpireInDays>0</saveExpireInDays>
        </omniScriptRootConfig>
    </propertySetConfig>
    <references>[]</references>
</FlexcardDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>FlexcardDefinition</name>
    </types>
    <version>[ftest]</version>
</Package>
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta.flexcarddefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
