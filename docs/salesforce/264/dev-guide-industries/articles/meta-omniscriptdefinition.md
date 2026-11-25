---
page_id: meta-omniscriptdefinition
title: OmniscriptDefinition
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omniscriptdefinition.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
legacy_page_id: meta_omniscriptdefinition.htm
fetched_at: 2026-11-25
---

# OmniscriptDefinition

Represents the header configuration of an Omniscript. Each row represents an Omniscript’s header configurations, such as its type, subtype, and name. An Omniscript helps build guided digital experiences. This object stores primary information about an Omniscript to render it at runtime.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

OmniscriptDefinition components have the suffix `.omniscriptDefinition` and are stored in the `omniscriptDefinitions` folder.

## Version

OmniscriptDefinition components are available in API version 67.0 and later.

## Special Access Rules

## Fields

### description

- **Field Type**: string

- **Description**: The user-defined text added to the description field when creating an Omniscript.

### designerCustomizationType

- **Field Type**: string

- **Description**: The name of the customization applied to an Omniscript when used with Discovery Framework.

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether the Omniscript is ready for use or in use on a Lightning or Experience Cloud page.

- **Default value**: `false`

### isManagedUsingStdDesigner

- **Field Type**: boolean

- **Description**: Indicates whether the Omniscript or Integration Procedure is created or updated using the Omnistudio standard designer.

- **Default value**: `true`

### isOmniscriptReusable

- **Field Type**: boolean

- **Description**: Indicates whether the Omniscript can be embedded in another Omniscript.

- **Default value**: `false`

### masterLabel

- **Field Type**: string

- **Description**: The user-defined name of the Omniscript.

### omniscriptDefinitionElement

- **Field Type**: [OmniscriptDefinitionElement](#omniscriptdefinitionelement)

- **Description**: The nested Omniscript definition element metadata associated with this Omniscript definition. Each row represents a configurable element of an Omniscript, such as a text block, an input field, or an action. These elements are the building blocks for creating an Omniscript.

### omniscriptLanguage

- **Field Type**: string

- **Description**: The language used in the Omniscript. Together with Type and Subtype, this forms the unique identifier of an Omniscript.

### omniscriptName

- **Field Type**: string

- **Description**: The user-defined name of the Omniscript.

### overrideKey

- **Field Type**: string

- **Description**: The unique name of the Omniscript that overrides the existing Omniscript.

### propertySetConfig

- **Field Type**: [OmniScriptPropertySetConfig](#omniscriptpropertysetconfig)

- **Description**: The properties of an Omniscript configured via the Omniscript Designer, stored as a JSON. At runtime, this JSON is read to render the Omniscript as per its configurations.

### references

- **Field Type**: string

- **Description**: The references to related Omniscript resources or records.

### subType

- **Field Type**: string

- **Description**: The user-defined value, that together with Type and Language forms the unique identifier for an Omniscript.

### type

- **Field Type**: string

- **Description**: The user-defined value, that together with Subtype and Language forms the unique identifier for an Omniscript.

## OmniscriptDefinitionElement

### description

- **Field Type**: string

- **Description**: The user-defined description added to the element.

### designerCustomizationType

- **Field Type**: string

- **Description**: The name of the customization applied to an Omniscript when used with features enabled outside of Omnistudio.

### embeddedOmniscriptKey

- **Field Type**: string

- **Description**: The key of the Omniscript embedded in the existing Omniscript.

### isActive

- **Field Type**: boolean

- **Description**: Indicates whether the element is used at runtime (`true`) or not (`false`). The default value is (`false`).

### isOmniscriptReusable

- **Field Type**: boolean

- **Description**: Indicates whether the Omniscript is reusable (`true`) or not (`false`) based on the user’s selection of the Reuse checkbox in Omniscript Setup. The default value is (`false`).

### level

- **Field Type**: double

- **Description**: The depth of an element in the Omniscript configuration when it’s nested within other elements.

### omniScriptDefElementName

- **Field Type**: string

- **Description**: The name of the element used in an Omniscript.

### parentElementName

- **Field Type**: string

- **Description**: The parent element name used to identify this Omniscript artifact in metadata.

### parentElementType

- 

**Field Type**: OmniscriptElementType (enumeration of type string)

- 

**Description**: The parent element type value that determines how this Omniscript setting is interpreted.

- 

**Values**: Values are:

  - `Aggregate`

  - `Block`

  - `Checkbox`

  - `Currency`

  - `Date`

  - `Disclosure`

  - `Email`

  - `File`

  - `Filter`

  - `Formula`

  - `Geolocation`

  - `Headline`

  - `Image`

  - `Lookup`

  - `Multi-select`

  - `Number`

  - `OmniScript`

  - `Password`

  - `Radio`

  - `Range`

  - `Select`

  - `Signature`

  - `Step`

  - `Submit`

  - `Telephone`

  - `Text`

  - `Time`

  - `URL`

  - `Validation`

### propertySetConfig

- **Field Type**: [OmniScriptElementPropertySetConfig](#omniscriptelementpropertysetconfig)

- **Description**: The properties of an element within an Omniscript configured via the Omniscript Designer, stored as a JSON. At runtime, this JSON is read to render the element as per its configurations.

### sequenceNumber

- **Field Type**: double

- **Description**: The position of the element in relation to its sibling elements in the Omniscript’s configuration.

### type

- 

**Field Type**: OmniscriptElementType (enumeration of type string)

- 

**Description**: The type of element added to the Omniscript.

- 

**Values**: Values are:

  - `Aggregate`

  - `Block`

  - `Checkbox`

  - `Currency`

  - `Date`

  - `Disclosure`

  - `Email`

  - `File`

  - `Filter`

  - `Formula`

  - `Geolocation`

  - `Headline`

  - `Image`

  - `Lookup`

  - `Multi-select`

  - `Number`

  - `OmniScript`

  - `Password`

  - `Radio`

  - `Range`

  - `Select`

  - `Signature`

  - `Step`

  - `Submit`

  - `Telephone`

  - `Text`

  - `Time`

  - `URL`

  - `Validation`

## OmniScriptElementPropertySetConfig

### BStandalone

- **Field Type**: boolean

- **Description**: Indicates whether bstandalone is enabled for the Omniscript configuration.

### accessibleInFutureSteps

- **Field Type**: boolean

- **Description**: Indicates whether accessible in future steps is enabled for the Omniscript configuration.

### allOrNone

- **Field Type**: boolean

- **Description**: Indicates whether all or none is enabled for the Omniscript configuration.

### allowClear

- **Field Type**: boolean

- **Description**: Indicates whether the Clear action is available for the Omniscript element.

### allowDelete

- **Field Type**: boolean

- **Description**: Indicates whether the Delete action is available for the Omniscript element.

### allowEdit

- **Field Type**: boolean

- **Description**: Indicates whether the Edit action is available for the Omniscript element.

### allowNegative

- **Field Type**: boolean

- **Description**: Indicates whether negative values are allowed for the Omniscript element.

### allowNew

- **Field Type**: boolean

- **Description**: Indicates whether creating new records is allowed for the Omniscript element.

### allowSaveChanges

- **Field Type**: boolean

- **Description**: Indicates whether users can save changes made in the Omniscript element.

### allowSaveForLater

- **Field Type**: boolean

- **Description**: Indicates whether users can save progress and resume the Omniscript later.

### applyIfError

- **Field Type**: boolean

- **Description**: Indicates whether apply if error is enabled for the Omniscript configuration.

### ariaLevel

- **Field Type**: int

- **Description**: The ARIA level value used for accessibility semantics in the Omniscript interface.

### attachmentList

- **Field Type**: string

- **Description**: The attachment list collection that maps or groups related Omniscript data.

### attachmentName

- **Field Type**: string

- **Description**: The attachment name used to identify this Omniscript artifact in metadata.

### attachmentParentId

- **Field Type**: string

- **Description**: The attachment parent ID used to reference related Omniscript resources or records.

### autoSaveChanges

- **Field Type**: boolean

- **Description**: Indicates whether auto save changes is enabled for the Omniscript configuration.

### autoSaveLabel

- **Field Type**: string

- **Description**: The auto save label text shown in the Omniscript user interface.

### bundle

- **Field Type**: string

- **Description**: The bundle used to configure Omniscript behavior.

### businessCategory

- **Field Type**: string

- **Description**: The business category value that determines how this Omniscript setting is interpreted.

### businessEvent

- **Field Type**: string

- **Description**: The business event value that determines how this Omniscript setting is interpreted.

### callFrequency

- **Field Type**: int

- **Description**: The call frequency setting that controls limits, layout, or processing behavior.

### cancelLabel

- **Field Type**: string

- **Description**: The cancel label text shown in the Omniscript user interface.

### cancelMessage

- **Field Type**: string

- **Description**: The cancel message text shown in the Omniscript user interface.

### chartLabel

- **Field Type**: string

- **Description**: The chart label text shown in the Omniscript user interface.

### checkLabel

- **Field Type**: string

- **Description**: The check label text shown in the Omniscript user interface.

### clearValue

- **Field Type**: boolean

- **Description**: Indicates whether clear value is enabled for the Omniscript configuration.

### collapse

- **Field Type**: boolean

- **Description**: Indicates whether collapse is enabled for the Omniscript configuration.

### completeLabel

- **Field Type**: string

- **Description**: The complete label text shown in the Omniscript user interface.

### completeMessage

- **Field Type**: string

- **Description**: The complete message text shown in the Omniscript user interface.

### conditionType

- **Field Type**: string

- **Description**: The condition type value that determines how this Omniscript setting is interpreted.

### configurationErrorMessage

- **Field Type**: string

- **Description**: The configuration error message text shown in the Omniscript user interface.

### confirm

- **Field Type**: boolean

- **Description**: Indicates whether confirm is enabled for the Omniscript configuration.

### confirmationOnDelete

- **Field Type**: boolean

- **Description**: Indicates whether confirmation on delete is enabled for the Omniscript configuration.

### contentParentId

- **Field Type**: string

- **Description**: The content parent ID used to reference related Omniscript resources or records.

### contentVersionList

- **Field Type**: string

- **Description**: The content version list collection that maps or groups related Omniscript data.

### controlWidth

- **Field Type**: int

- **Description**: The control width setting that controls layout, limits, or processing order.

### controllingField

- **Field Type**: string

- **Description**: The controlling field that identifies the data source or target used by Omniscript.

### customAttributes

- **Field Type**: string

- **Description**: The custom attributes used to configure Omniscript behavior.

### dataJSON

- **Field Type**: boolean

- **Description**: Indicates whether data json is enabled for the Omniscript configuration.

### dataJsonPath

- **Field Type**: string

- **Description**: The data json path used to read or write runtime data.

### dataProcessorFunction

- **Field Type**: string

- **Description**: The data processor function logic expression used during Omniscript processing.

### dataRaptorInputParameters

- **Field Type**: string

- **Description**: The data raptor input parameters value used by Omniscript at runtime.

### dataSource

- **Field Type**: string

- **Description**: The data source that identifies the data source or target used by Omniscript.

### dataType

- **Field Type**: string

- **Description**: The data type value that determines how this Omniscript setting is interpreted.

### dateFormat

- **Field Type**: string

- **Description**: The date format value that determines how this Omniscript setting is interpreted.

### dateTimeFormat

- **Field Type**: string

- **Description**: The date time format value that determines how this Omniscript setting is interpreted.

### dateType

- **Field Type**: string

- **Description**: The date type value that determines how this Omniscript setting is interpreted.

### debounceValue

- **Field Type**: int

- **Description**: The debounce value setting that controls limits, layout, or processing behavior.

### defaultMatrixResult

- **Field Type**: string

- **Description**: The default matrix result setting that controls limits, layout, or processing behavior.

### defaultValue

- **Field Type**: string

- **Description**: The default value setting that controls limits, layout, or processing behavior.

### deleteFailedMessage

- **Field Type**: string

- **Description**: The delete failed message text shown in the Omniscript user interface.

### deleteLabel

- **Field Type**: string

- **Description**: The delete label text shown in the Omniscript user interface.

### deleteSObject

- **Field Type**: string

- **Description**: The delete sobject value used by Omniscript at runtime.

### disOnTplt

- **Field Type**: boolean

- **Description**: Indicates whether dis on tplt is enabled for the Omniscript configuration.

### disableDataFilter

- **Field Type**: boolean

- **Description**: Indicates whether disable data filter is enabled for the Omniscript configuration.

### displayCurrencyCode

- **Field Type**: boolean

- **Description**: Indicates whether display currency code is enabled for the Omniscript configuration.

### displayHeight

- **Field Type**: int

- **Description**: The display height setting that controls limits, layout, or processing behavior.

### displayWidth

- **Field Type**: int

- **Description**: The display width setting that controls layout, limits, or processing order.

### docList

- **Field Type**: string

- **Description**: The doc list collection that maps or groups related Omniscript data.

### docuSignReturnUrl

- **Field Type**: string

- **Description**: The docu sign return url value used by Omniscript at runtime.

### docuSignTemplatesGroup

- **Field Type**: string

- **Description**: The docu sign templates group reference used by Omniscript integrations or rendering.

### docuSignTemplatesGroupSig

- **Field Type**: string

- **Description**: The docu sign templates group sig reference used by Omniscript integrations or rendering.

### dynamicProperties

- **Field Type**: string

- **Description**: The dynamic properties used to configure Omniscript behavior.

### editLabel

- **Field Type**: string

- **Description**: The edit label text shown in the Omniscript user interface.

### editMode

- **Field Type**: boolean

- **Description**: Indicates whether edit mode is enabled for the Omniscript configuration.

### elementErrorMap

- **Field Type**: string

- **Description**: The element error map collection that maps or groups related Omniscript data.

### elementName

- **Field Type**: string

- **Description**: The element name used to identify this Omniscript artifact in metadata.

### elementValueMap

- **Field Type**: string

- **Description**: The element value map collection that maps or groups related Omniscript data.

### emailBody

- **Field Type**: string

- **Description**: The email body text shown to users in the Omniscript interface.

### emailInformation

- **Field Type**: string

- **Description**: The email information value used by Omniscript at runtime.

### emailSubject

- **Field Type**: string

- **Description**: The email subject text shown to users in the Omniscript interface.

### emailTemplateInformation

- **Field Type**: string

- **Description**: The email template information reference used by Omniscript integrations or rendering.

### enableActionMessage

- **Field Type**: boolean

- **Description**: Indicates whether action message is enabled for this Omniscript configuration.

### enableCaption

- **Field Type**: boolean

- **Description**: Indicates whether caption is enabled for this Omniscript configuration.

### enableDefaultAbort

- **Field Type**: boolean

- **Description**: Indicates whether default abort is enabled for this Omniscript configuration.

### enableGoogleMapsAutocomplete

- **Field Type**: boolean

- **Description**: Indicates whether google maps autocomplete is enabled for this Omniscript configuration.

### enableLookup

- **Field Type**: boolean

- **Description**: Indicates whether lookup is enabled for this Omniscript configuration.

### entityIsDeletedMessage

- **Field Type**: string

- **Description**: The entity is deleted message text shown in the Omniscript user interface.

### errorMessage

- **Field Type**: string

- **Description**: The error message text shown in the Omniscript user interface.

### expression

- **Field Type**: string

- **Description**: The expression logic expression used during Omniscript processing.

### extraPayload

- **Field Type**: string

- **Description**: The extra payload value used by Omniscript at runtime.

### failureAbortLabel

- **Field Type**: string

- **Description**: The failure abort label text shown in the Omniscript user interface.

### failureAbortMessage

- **Field Type**: string

- **Description**: The failure abort message text shown in the Omniscript user interface.

### failureGoBackLabel

- **Field Type**: string

- **Description**: The failure go back label text shown in the Omniscript user interface.

### failureNextLabel

- **Field Type**: string

- **Description**: The failure next label text shown in the Omniscript user interface.

### fileAttachments

- **Field Type**: string

- **Description**: The file attachments collection that maps or groups related Omniscript data.

### googleAddressCountry

- **Field Type**: string

- **Description**: The google address country value used by Omniscript at runtime.

### googleMapsAPIKey

- **Field Type**: string

- **Description**: The google maps apikey value used by Omniscript at runtime.

### googleTransformation

- **Field Type**: string

- **Description**: The google transformation value used by Omniscript at runtime.

### headingLevel

- **Field Type**: int

- **Description**: The heading level setting that controls layout, limits, or processing order.

### help

- **Field Type**: boolean

- **Description**: Indicates whether help is enabled for the Omniscript configuration.

### helpText

- **Field Type**: string

- **Description**: The help text text shown in the Omniscript user interface.

### hide

- **Field Type**: boolean

- **Description**: Indicates whether hide is enabled for the Omniscript configuration.

### hideEditButton

- **Field Type**: boolean

- **Description**: Indicates whether hide edit button is enabled for the Omniscript configuration.

### hideGroupSep

- **Field Type**: boolean

- **Description**: Indicates whether hide group sep is enabled for the Omniscript configuration.

### hideLabel

- **Field Type**: boolean

- **Description**: Indicates whether hide label is enabled for the Omniscript configuration.

### hideMap

- **Field Type**: boolean

- **Description**: Indicates whether hide map is enabled for the Omniscript configuration.

### horizontalMode

- **Field Type**: boolean

- **Description**: Indicates whether horizontal mode is enabled for the Omniscript configuration.

### htmlTemplateId

- **Field Type**: string

- **Description**: The html template ID used to reference related Omniscript resources or records.

### iconName

- **Field Type**: string

- **Description**: The icon name used to identify this Omniscript artifact in metadata.

### iconPosition

- **Field Type**: string

- **Description**: The icon position value used by Omniscript at runtime.

### iconVariant

- **Field Type**: string

- **Description**: The icon variant value used by Omniscript at runtime.

### ignoreCache

- **Field Type**: boolean

- **Description**: Indicates whether ignore cache is enabled for the Omniscript configuration.

### imageCountInRow

- **Field Type**: int

- **Description**: The image count in row setting that controls layout, limits, or processing order.

### inProgressMessage

- **Field Type**: string

- **Description**: The in progress message text shown in the Omniscript user interface.

### inputWidth

- **Field Type**: int

- **Description**: The input width setting that controls layout, limits, or processing order.

### instruction

- **Field Type**: string

- **Description**: The instruction value used by Omniscript at runtime.

### instructionKey

- **Field Type**: string

- **Description**: The instruction key used to reference related Omniscript resources or records.

### integrationProcedureKey

- **Field Type**: string

- **Description**: The integration procedure key used to reference related Omniscript resources or records.

### invalidIdMessage

- **Field Type**: string

- **Description**: The invalid ID message text shown in the Omniscript user interface.

### invokeMode

- **Field Type**: string

- **Description**: The invoke mode value that determines how this Omniscript setting is interpreted.

### knowledgeOptions

- **Field Type**: string

- **Description**: The knowledge options value used by Omniscript at runtime.

### label

- **Field Type**: string

- **Description**: The label text shown in the Omniscript user interface.

### loginAction

- **Field Type**: string

- **Description**: The login action value used by Omniscript at runtime.

### lwcComponentOverride

- **Field Type**: string

- **Description**: The lwc component override value used by Omniscript at runtime.

### lwcName

- **Field Type**: string

- **Description**: The lwc name used to identify this Omniscript artifact in metadata.

### mask

- **Field Type**: string

- **Description**: The mask value used by Omniscript at runtime.

### matrixInputParameters

- **Field Type**: string

- **Description**: The matrix input parameters value used by Omniscript at runtime.

### max

- **Field Type**: string

- **Description**: The max setting that controls limits, layout, or processing behavior.

### maxDate

- **Field Type**: string

- **Description**: The max date setting that controls limits, layout, or processing behavior.

### maxDisplay

- **Field Type**: int

- **Description**: The max display setting that controls limits, layout, or processing behavior.

### maxLength

- **Field Type**: int

- **Description**: The max length setting that controls layout, limits, or processing order.

### maxTime

- **Field Type**: string

- **Description**: The max time setting that controls limits, layout, or processing behavior.

### message

- **Field Type**: string

- **Description**: The message text shown in the Omniscript user interface.

### messages

- **Field Type**: string

- **Description**: The messages value used by Omniscript at runtime.

### min

- **Field Type**: string

- **Description**: The minimum setting that controls limits, layout, or processing behavior.

### minDate

- **Field Type**: string

- **Description**: The minimum date setting that controls limits, layout, or processing behavior.

### minLength

- **Field Type**: int

- **Description**: The minimum length setting that controls layout, limits, or processing order.

### minTime

- **Field Type**: string

- **Description**: The minimum time setting that controls limits, layout, or processing behavior.

### mode

- **Field Type**: string

- **Description**: The mode value that determines how this Omniscript setting is interpreted.

### modelDateFormat

- **Field Type**: string

- **Description**: The model date format value that determines how this Omniscript setting is interpreted.

### modelTimeFormat

- **Field Type**: string

- **Description**: The model time format value that determines how this Omniscript setting is interpreted.

### multiple

- **Field Type**: boolean

- **Description**: Indicates whether multiple is enabled for the Omniscript configuration.

### namedCredential

- **Field Type**: string

- **Description**: The named credential value used by Omniscript at runtime.

### newItemLabel

- **Field Type**: string

- **Description**: The new item label text shown in the Omniscript user interface.

### newLabel

- **Field Type**: string

- **Description**: The new label text shown in the Omniscript user interface.

### nextLabel

- **Field Type**: string

- **Description**: The next label text shown in the Omniscript user interface.

### nextWidth

- **Field Type**: int

- **Description**: The next width setting that controls layout, limits, or processing order.

### objectAction

- **Field Type**: string

- **Description**: The object action that identifies the data source or target used by Omniscript.

### omniScriptRootConfig

- **Field Type**: [OmniScriptPropertySetConfig](#omniscriptpropertysetconfig)

- **Description**: The omniscript root config used to configure Omniscript behavior.

### optionHeight

- **Field Type**: int

- **Description**: The option height setting that controls limits, layout, or processing behavior.

### optionSource

- **Field Type**: string

- **Description**: The option source that identifies the data source or target used by Omniscript.

### optionWidth

- **Field Type**: int

- **Description**: The option width setting that controls layout, limits, or processing order.

### options

- **Field Type**: string

- **Description**: The options value used by Omniscript at runtime.

### orgWideEmailAddress

- **Field Type**: string

- **Description**: The org wide email address value used by Omniscript at runtime.

### padding

- **Field Type**: int

- **Description**: The padding value used by Omniscript at runtime.

### pattern

- **Field Type**: string

- **Description**: The pattern value used by Omniscript at runtime.

### placeholder

- **Field Type**: string

- **Description**: The placeholder text shown in the Omniscript user interface.

### postMessage

- **Field Type**: string

- **Description**: The post message text shown in the Omniscript user interface.

### postTransformBundle

- **Field Type**: string

- **Description**: The post transform bundle used to configure Omniscript behavior.

### preTransformBundle

- **Field Type**: string

- **Description**: The pre transform bundle used to configure Omniscript behavior.

### previousLabel

- **Field Type**: string

- **Description**: The previous label text shown in the Omniscript user interface.

### previousWidth

- **Field Type**: int

- **Description**: The previous width setting that controls layout, limits, or processing order.

### ptrnErrText

- **Field Type**: string

- **Description**: The ptrn err text text shown in the Omniscript user interface.

### pubsub

- **Field Type**: boolean

- **Description**: Indicates whether pubsub is enabled for the Omniscript configuration.

### radioLabels

- **Field Type**: string

- **Description**: The radio labels value used by Omniscript at runtime.

### radioLabelsWidth

- **Field Type**: int

- **Description**: The radio labels width setting that controls layout, limits, or processing order.

### rangeHigh

- **Field Type**: int

- **Description**: The range high value used by Omniscript at runtime.

### rangeLow

- **Field Type**: int

- **Description**: The range low value used by Omniscript at runtime.

### readOnly

- **Field Type**: boolean

- **Description**: Indicates whether read only is enabled for the Omniscript configuration.

### recordAction

- **Field Type**: string

- **Description**: The record action value used by Omniscript at runtime.

### redirectNextLabel

- **Field Type**: string

- **Description**: The redirect next label text shown in the Omniscript user interface.

### redirectNextWidth

- **Field Type**: int

- **Description**: The redirect next width setting that controls layout, limits, or processing order.

### redirectPageName

- **Field Type**: string

- **Description**: The redirect page name used to identify this Omniscript artifact in metadata.

### redirectPreviousLabel

- **Field Type**: string

- **Description**: The redirect previous label text shown in the Omniscript user interface.

### redirectPreviousWidth

- **Field Type**: int

- **Description**: The redirect previous width setting that controls layout, limits, or processing order.

### redirectTemplateUrl

- **Field Type**: string

- **Description**: The redirect template url reference used by Omniscript integrations or rendering.

### remoteClass

- **Field Type**: string

- **Description**: The remote class value used by Omniscript at runtime.

### remoteConfirmMsg

- **Field Type**: string

- **Description**: The remote confirm msg value used by Omniscript at runtime.

### remoteMethod

- **Field Type**: string

- **Description**: The remote method logic expression used during Omniscript processing.

### remoteOptions

- **Field Type**: string

- **Description**: The remote options value used by Omniscript at runtime.

### remoteTimeout

- **Field Type**: int

- **Description**: The remote timeout setting that controls limits, layout, or processing behavior.

### repeat

- **Field Type**: boolean

- **Description**: Indicates whether repeat is enabled for the Omniscript configuration.

### repeatClone

- **Field Type**: boolean

- **Description**: Indicates whether repeat clone is enabled for the Omniscript configuration.

### repeatLimit

- **Field Type**: int

- **Description**: The repeat limit value used by Omniscript at runtime.

### replace

- **Field Type**: boolean

- **Description**: Indicates whether replace is enabled for the Omniscript configuration.

### required

- **Field Type**: boolean

- **Description**: Indicates whether required is enabled for the Omniscript configuration.

### responseJSONNode

- **Field Type**: string

- **Description**: The response jsonnode value used by Omniscript at runtime.

### responseJSONPath

- **Field Type**: string

- **Description**: The response jsonpath used to read or write runtime data.

### restMethod

- **Field Type**: string

- **Description**: The rest method logic expression used during Omniscript processing.

### restOptions

- **Field Type**: string

- **Description**: The rest options value used by Omniscript at runtime.

### restPath

- **Field Type**: string

- **Description**: The rest path used to read or write runtime data.

### restoreDefaultValuesOnCancel

- **Field Type**: boolean

- **Description**: Indicates whether restore default values on cancel is enabled for the Omniscript configuration.

### sanitize

- **Field Type**: boolean

- **Description**: Indicates whether sanitize is enabled for the Omniscript configuration.

### saveChangesLabel

- **Field Type**: string

- **Description**: The save changes label text shown in the Omniscript user interface.

### saveLabel

- **Field Type**: string

- **Description**: The save label text shown in the Omniscript user interface.

### saveMessage

- **Field Type**: string

- **Description**: The save message text shown in the Omniscript user interface.

### selectCheckBox

- **Field Type**: string

- **Description**: The select check box value used by Omniscript at runtime.

### selectMode

- **Field Type**: string

- **Description**: The select mode value that determines how this Omniscript setting is interpreted.

### selectSobject

- **Field Type**: string

- **Description**: The select sobject value used by Omniscript at runtime.

### sendJSONNode

- **Field Type**: string

- **Description**: The send jsonnode value used by Omniscript at runtime.

### sendJSONPath

- **Field Type**: string

- **Description**: The send jsonpath used to read or write runtime data.

### show

- **Field Type**: string

- **Description**: The show value used by Omniscript at runtime.

### showInputWidth

- **Field Type**: boolean

- **Description**: Indicates whether show input width is enabled for the Omniscript configuration.

### showPersistentComponent

- **Field Type**: string

- **Description**: The show persistent component value used by Omniscript at runtime.

### showPopup

- **Field Type**: boolean

- **Description**: Indicates whether show popup is enabled for the Omniscript configuration.

### signerInformation

- **Field Type**: string

- **Description**: The signer information value used by Omniscript at runtime.

### sobjectMapping

- **Field Type**: string

- **Description**: The sobject mapping collection that maps or groups related Omniscript data.

### ssm

- **Field Type**: boolean

- **Description**: Indicates whether ssm is enabled for the Omniscript configuration.

### staticDocList

- **Field Type**: string

- **Description**: The static doc list collection that maps or groups related Omniscript data.

### step

- **Field Type**: int

- **Description**: The step value used by Omniscript at runtime.

### subLabel

- **Field Type**: string

- **Description**: The sub label text shown in the Omniscript user interface.

### sumElement

- **Field Type**: string

- **Description**: The sum element value used by Omniscript at runtime.

### svgIcon

- **Field Type**: string

- **Description**: The svg icon value used by Omniscript at runtime.

### svgSprite

- **Field Type**: string

- **Description**: The svg sprite value used by Omniscript at runtime.

### targetFilter

- **Field Type**: string

- **Description**: The target filter that identifies the data source or target used by Omniscript.

### targetId

- **Field Type**: string

- **Description**: The target ID used to reference related Omniscript resources or records.

### targetLWCLayout

- **Field Type**: string

- **Description**: The target lwclayout that identifies the data source or target used by Omniscript.

### targetType

- **Field Type**: string

- **Description**: The target type value that determines how this Omniscript setting is interpreted.

### templateName

- **Field Type**: string

- **Description**: The template name used to identify this Omniscript artifact in metadata.

### text

- **Field Type**: string

- **Description**: The text text shown in the Omniscript user interface.

### textKey

- **Field Type**: string

- **Description**: The text key text shown in the Omniscript user interface.

### timeFormat

- **Field Type**: string

- **Description**: The time format value that determines how this Omniscript setting is interpreted.

### timeInterval

- **Field Type**: int

- **Description**: The time interval value used by Omniscript at runtime.

### timeType

- **Field Type**: string

- **Description**: The time type value that determines how this Omniscript setting is interpreted.

### timezone

- **Field Type**: string

- **Description**: The timezone value used by Omniscript at runtime.

### type

- **Field Type**: string

- **Description**: The type value that determines how this Omniscript setting is interpreted.

### typeAheadKey

- **Field Type**: string

- **Description**: The type ahead key used to reference related Omniscript resources or records.

### uploadContDoc

- **Field Type**: boolean

- **Description**: Indicates whether upload cont doc is enabled for the Omniscript configuration.

### useContinuation

- **Field Type**: boolean

- **Description**: Indicates whether use continuation is enabled for the Omniscript configuration.

### useDataJson

- **Field Type**: boolean

- **Description**: Indicates whether use data json is enabled for the Omniscript configuration.

### useTemplate

- **Field Type**: boolean

- **Description**: Indicates whether use template is enabled for the Omniscript configuration.

### validateExpression

- **Field Type**: string

- **Description**: The validate expression logic expression used during Omniscript processing.

### validationRequired

- **Field Type**: string

- **Description**: The validation required value used by Omniscript at runtime.

### valueSvgMap

- **Field Type**: string

- **Description**: The value svg map collection that maps or groups related Omniscript data.

### variant

- **Field Type**: string

- **Description**: The variant value used by Omniscript at runtime.

### wpm

- **Field Type**: boolean

- **Description**: Indicates whether wpm is enabled for the Omniscript configuration.

### xmlPostTransformBundle

- **Field Type**: string

- **Description**: The xml post transform bundle used to configure Omniscript behavior.

### xmlPreTransformBundle

- **Field Type**: string

- **Description**: The xml pre transform bundle used to configure Omniscript behavior.

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

## Declarative Metadata Sample Definition

The following is an example of the OmniscriptDefinition component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniscriptDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
    <isActive>true</isActive>
    <isManagedUsingStdDesigner>true</isManagedUsingStdDesigner>
    <isOmniscriptReusable>false</isOmniscriptReusable>
    <masterLabel>Simple_Os_English Updated</masterLabel>
    <omniscriptDefinitionElement>
        <isActive>true</isActive>
        <isOmniscriptReusable>false</isOmniscriptReusable>
        <level>1.0</level>
        <omniScriptDefElementName>TextBlock1</omniScriptDefElementName>
        <sequenceNumber>0.0</sequenceNumber>
        <type>Text Block</type>
    </omniscriptDefinitionElement>
    <omniscriptDefinitionElement>
        <isActive>true</isActive>
        <isOmniscriptReusable>false</isOmniscriptReusable>
        <level>0.0</level>
        <omniScriptDefElementName>Step1</omniScriptDefElementName>
        <sequenceNumber>0.0</sequenceNumber>
        <type>Step</type>
    </omniscriptDefinitionElement>
    <omniscriptLanguage>English</omniscriptLanguage>
    <omniscriptName>SimpleOs</omniscriptName>
    <references>[]</references>
    <subType>Os</subType>
    <type>Simple</type>
</OmniscriptDefinition>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniscriptDefinition</name>
    </types>
    <version>68.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omniscriptdefinition.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
