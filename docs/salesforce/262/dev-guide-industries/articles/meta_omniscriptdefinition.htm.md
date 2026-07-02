---
page_id: meta_omniscriptdefinition.htm
title: OmniscriptDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniscriptdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniscriptDefinition

Represents the header configuration of an
Omniscript. Each row represents an Omniscript's header configurations, such as its type,
subtype, and name. An Omniscript helps build guided digital experiences. This object stores
primary information about an Omniscript to render it at runtime.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)")
metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniscriptDefinition components have the suffix .omniscriptDefinition
and are stored in the omniscriptDefinitions folder.

## Version

OmniscriptDefinition components are available in API version 67.0 and later.

## Special Access Rules

To use this metadata type, you must have an Omnistudio license and the Discovery Framework
feature enabled in your Salesforce org.

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  The user-defined text added to the Description field when creating an Omniscript. |
| designerCustomizationType | Field Type  string  Description  The name of the customization applied to an Omniscript when used with Discovery Framework. |
| isActive | Field Type  boolean  Description  Indicates whether the Omniscript is ready for use or in use on a Lightning or Experience Cloud page. The default value is `false`. |
| isManagedUsingStdDesigner | Field Type  boolean  Description  Indicates whether the Omniscript or Integration Procedure is created or updated using the Omnistudio standard designer. The default value is `true`. |
| isOmniscriptReusable | Field Type  boolean  Description  Indicates whether the Omniscript can be embedded in another Omniscript. The default value is `false`. |
| masterLabel | Field Type  string  Description  The user-defined name of the Omniscript. |
| omniscriptDefinitionElement | Field Type  [OmniscriptDefinitionElement](#OmniscriptDefinitionElement)  Description  The nested OmniScript definition element metadata associated with this OmniScript definition. Each row represents a configurable element of an Omniscript, such as a text block, an input field, or an action. These elements are the building blocks for creating an Omniscript. |
| omniscriptLanguage | Field Type  string  Description  The language used in the Omniscript. Together with Type and Subtype, this forms the unique identifier of an Omniscript. |
| omniscriptName | Field Type  string  Description  The user-defined name of the Omniscript. |
| overrideKey | Field Type  string  Description  The unique name of the Omniscript that overrides the existing Omniscript. |
| propertySetConfig | Field Type  [OmniScriptPropertySetConfig](#OmniScriptPropertySetConfig)  Description  The properties of an Omniscript configured via the Omniscript Designer, stored as a JSON. At runtime, this JSON is read to render the Omniscript as per its configurations. |
| references | Field Type  string  Description  The references to related OmniScript resources or records. |
| subType | Field Type  string  Description  The user-defined value, that together with Type and Language forms the unique identifier for an Omniscript. |
| type | Field Type  string  Description  The user-defined value, that together with Subtype and Language forms the unique identifier for an Omniscript. |

## OmniscriptDefinitionElement

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  The user-defined description added to the element. |
| designerCustomizationType | Field Type  string  Description  The name of the customization applied to an Omniscript when used with features enabled outside of Omnistudio. |
| embeddedOmniscriptKey | Field Type  string  Description  The key of the Omniscript embedded in the existing Omniscript. |
| isActive | Field Type  boolean  Description  Indicates whether the element is used at runtime (`true`) or not (`false`). The default value is (`false`). |
| isOmniscriptReusable | Field Type  boolean  Description  Indicates whether the Omniscript is reusable (`true`) or not (`false`) based on the user's selection of the Reuse checkbox in Omniscript Setup. The default value is (`false`). |
| level | Field Type  double  Description  The depth of an element in the Omniscript configuration when it's nested within other elements. |
| omniScriptDefElementName | Field Type  string  Description  The name of the element used in an Omniscript. |
| parentElementName | Field Type  string  Description  The parent element name used to identify this OmniScript artifact in metadata. |
| parentElementType | Field Type  OmniscriptElementType (enumeration of type string)  Description  The parent element type value that determines how this OmniScript setting is interpreted.  Values  Values are:   - `Aggregate` - `Block` - `Checkbox` - `Currency` - `Date` - `Disclosure` - `Email` - `File` - `Filter` - `Formula` - `Geolocation` - `Headline` - `Image` - `Lookup` - `Multi-select` - `Number` - `OmniScript` - `Password` - `Radio` - `Range` - `Select` - `Signature` - `Step` - `Submit` - `Telephone` - `Text` - `Time` - `URL` - `Validation` |
| propertySetConfig | Field Type  [OmniScriptElementPropertySetConfig](#OmniScriptElementPropertySetConfig)  Description  The properties of an element within an Omniscript configured via the Omniscript Designer, stored as a JSON. At runtime, this JSON is read to render the element as per its configurations. |
| sequenceNumber | Field Type  double  Description  The position of the element in relation to its sibling elements in the Omniscript's configuration. |
| type | Field Type  OmniscriptElementType (enumeration of type string)  Description  The type of element added to the Omniscript.  Values  Values are:   - `Aggregate` - `Block` - `Checkbox` - `Currency` - `Date` - `Disclosure` - `Email` - `File` - `Filter` - `Formula` - `Geolocation` - `Headline` - `Image` - `Lookup` - `Multi-select` - `Number` - `OmniScript` - `Password` - `Radio` - `Range` - `Select` - `Signature` - `Step` - `Submit` - `Telephone` - `Text` - `Time` - `URL` - `Validation` |

## OmniScriptElementPropertySetConfig

| Field Name | Description |
| --- | --- |
| BStandalone | Field Type  boolean  Description  Indicates whether bstandalone is enabled for the OmniScript configuration. |
| accessibleInFutureSteps | Field Type  boolean  Description  Indicates whether accessible in future steps is enabled for the OmniScript configuration. |
| allOrNone | Field Type  boolean  Description  Indicates whether all or none is enabled for the OmniScript configuration. |
| allowClear | Field Type  boolean  Description  Indicates whether the Clear action is available for the OmniScript element. |
| allowDelete | Field Type  boolean  Description  Indicates whether the Delete action is available for the OmniScript element. |
| allowEdit | Field Type  boolean  Description  Indicates whether the Edit action is available for the OmniScript element. |
| allowNegative | Field Type  boolean  Description  Indicates whether negative values are allowed for the OmniScript element. |
| allowNew | Field Type  boolean  Description  Indicates whether creating new records is allowed for the OmniScript element. |
| allowSaveChanges | Field Type  boolean  Description  Indicates whether users can save changes made in the OmniScript element. |
| allowSaveForLater | Field Type  boolean  Description  Indicates whether users can save progress and resume the OmniScript later. |
| applyIfError | Field Type  boolean  Description  Indicates whether apply if error is enabled for the OmniScript configuration. |
| ariaLevel | Field Type  int  Description  The ARIA level value used for accessibility semantics in the OmniScript interface. |
| attachmentList | Field Type  string  Description  The attachment list collection that maps or groups related OmniScript data. |
| attachmentName | Field Type  string  Description  The attachment name used to identify this OmniScript artifact in metadata. |
| attachmentParentId | Field Type  string  Description  The attachment parent id used to reference related OmniScript resources or records. |
| autoSaveChanges | Field Type  boolean  Description  Indicates whether auto save changes is enabled for the OmniScript configuration. |
| autoSaveLabel | Field Type  string  Description  The auto save label text shown in the OmniScript user interface. |
| bundle | Field Type  string  Description  The bundle used to configure OmniScript behavior. |
| businessCategory | Field Type  string  Description  The business category value that determines how this OmniScript setting is interpreted. |
| businessEvent | Field Type  string  Description  The business event value that determines how this OmniScript setting is interpreted. |
| callFrequency | Field Type  int  Description  The call frequency setting that controls limits, layout, or processing behavior. |
| cancelLabel | Field Type  string  Description  The cancel label text shown in the OmniScript user interface. |
| cancelMessage | Field Type  string  Description  The cancel message text shown in the OmniScript user interface. |
| chartLabel | Field Type  string  Description  The chart label text shown in the OmniScript user interface. |
| checkLabel | Field Type  string  Description  The check label text shown in the OmniScript user interface. |
| clearValue | Field Type  boolean  Description  Indicates whether clear value is enabled for the OmniScript configuration. |
| collapse | Field Type  boolean  Description  Indicates whether collapse is enabled for the OmniScript configuration. |
| completeLabel | Field Type  string  Description  The complete label text shown in the OmniScript user interface. |
| completeMessage | Field Type  string  Description  The complete message text shown in the OmniScript user interface. |
| conditionType | Field Type  string  Description  The condition type value that determines how this OmniScript setting is interpreted. |
| configurationErrorMessage | Field Type  string  Description  The configuration error message text shown in the OmniScript user interface. |
| confirm | Field Type  boolean  Description  Indicates whether confirm is enabled for the OmniScript configuration. |
| confirmationOnDelete | Field Type  boolean  Description  Indicates whether confirmation on delete is enabled for the OmniScript configuration. |
| contentParentId | Field Type  string  Description  The content parent id used to reference related OmniScript resources or records. |
| contentVersionList | Field Type  string  Description  The content version list collection that maps or groups related OmniScript data. |
| controlWidth | Field Type  int  Description  The control width setting that controls layout, limits, or processing order. |
| controllingField | Field Type  string  Description  The controlling field that identifies the data source or target used by OmniScript. |
| customAttributes | Field Type  string  Description  The custom attributes used to configure OmniScript behavior. |
| dataJSON | Field Type  boolean  Description  Indicates whether data json is enabled for the OmniScript configuration. |
| dataJsonPath | Field Type  string  Description  The data json path used to read or write runtime data. |
| dataProcessorFunction | Field Type  string  Description  The data processor function logic expression used during OmniScript processing. |
| dataRaptorInputParameters | Field Type  string  Description  The data raptor input parameters value used by OmniScript at runtime. |
| dataSource | Field Type  string  Description  The data source that identifies the data source or target used by OmniScript. |
| dataType | Field Type  string  Description  The data type value that determines how this OmniScript setting is interpreted. |
| dateFormat | Field Type  string  Description  The date format value that determines how this OmniScript setting is interpreted. |
| dateTimeFormat | Field Type  string  Description  The date time format value that determines how this OmniScript setting is interpreted. |
| dateType | Field Type  string  Description  The date type value that determines how this OmniScript setting is interpreted. |
| debounceValue | Field Type  int  Description  The debounce value setting that controls limits, layout, or processing behavior. |
| defaultMatrixResult | Field Type  string  Description  The default matrix result setting that controls limits, layout, or processing behavior. |
| defaultValue | Field Type  string  Description  The default value setting that controls limits, layout, or processing behavior. |
| deleteFailedMessage | Field Type  string  Description  The delete failed message text shown in the OmniScript user interface. |
| deleteLabel | Field Type  string  Description  The delete label text shown in the OmniScript user interface. |
| deleteSObject | Field Type  string  Description  The delete sobject value used by OmniScript at runtime. |
| disOnTplt | Field Type  boolean  Description  Indicates whether dis on tplt is enabled for the OmniScript configuration. |
| disableDataFilter | Field Type  boolean  Description  Indicates whether disable data filter is enabled for the OmniScript configuration. |
| displayCurrencyCode | Field Type  boolean  Description  Indicates whether display currency code is enabled for the OmniScript configuration. |
| displayHeight | Field Type  int  Description  The display height setting that controls limits, layout, or processing behavior. |
| displayWidth | Field Type  int  Description  The display width setting that controls layout, limits, or processing order. |
| docList | Field Type  string  Description  The doc list collection that maps or groups related OmniScript data. |
| docuSignReturnUrl | Field Type  string  Description  The docu sign return url value used by OmniScript at runtime. |
| docuSignTemplatesGroup | Field Type  string  Description  The docu sign templates group reference used by OmniScript integrations or rendering. |
| docuSignTemplatesGroupSig | Field Type  string  Description  The docu sign templates group sig reference used by OmniScript integrations or rendering. |
| dynamicProperties | Field Type  string  Description  The dynamic properties used to configure OmniScript behavior. |
| editLabel | Field Type  string  Description  The edit label text shown in the OmniScript user interface. |
| editMode | Field Type  boolean  Description  Indicates whether edit mode is enabled for the OmniScript configuration. |
| elementErrorMap | Field Type  string  Description  The element error map collection that maps or groups related OmniScript data. |
| elementName | Field Type  string  Description  The element name used to identify this OmniScript artifact in metadata. |
| elementValueMap | Field Type  string  Description  The element value map collection that maps or groups related OmniScript data. |
| emailBody | Field Type  string  Description  The email body text shown to users in the OmniScript interface. |
| emailInformation | Field Type  string  Description  The email information value used by OmniScript at runtime. |
| emailSubject | Field Type  string  Description  The email subject text shown to users in the OmniScript interface. |
| emailTemplateInformation | Field Type  string  Description  The email template information reference used by OmniScript integrations or rendering. |
| enableActionMessage | Field Type  boolean  Description  Indicates whether action message is enabled for this OmniScript configuration. |
| enableCaption | Field Type  boolean  Description  Indicates whether caption is enabled for this OmniScript configuration. |
| enableDefaultAbort | Field Type  boolean  Description  Indicates whether default abort is enabled for this OmniScript configuration. |
| enableGoogleMapsAutocomplete | Field Type  boolean  Description  Indicates whether google maps autocomplete is enabled for this OmniScript configuration. |
| enableLookup | Field Type  boolean  Description  Indicates whether lookup is enabled for this OmniScript configuration. |
| entityIsDeletedMessage | Field Type  string  Description  The entity is deleted message text shown in the OmniScript user interface. |
| errorMessage | Field Type  string  Description  The error message text shown in the OmniScript user interface. |
| expression | Field Type  string  Description  The expression logic expression used during OmniScript processing. |
| extraPayload | Field Type  string  Description  The extra payload value used by OmniScript at runtime. |
| failureAbortLabel | Field Type  string  Description  The failure abort label text shown in the OmniScript user interface. |
| failureAbortMessage | Field Type  string  Description  The failure abort message text shown in the OmniScript user interface. |
| failureGoBackLabel | Field Type  string  Description  The failure go back label text shown in the OmniScript user interface. |
| failureNextLabel | Field Type  string  Description  The failure next label text shown in the OmniScript user interface. |
| fileAttachments | Field Type  string  Description  The file attachments collection that maps or groups related OmniScript data. |
| googleAddressCountry | Field Type  string  Description  The google address country value used by OmniScript at runtime. |
| googleMapsAPIKey | Field Type  string  Description  The google maps apikey value used by OmniScript at runtime. |
| googleTransformation | Field Type  string  Description  The google transformation value used by OmniScript at runtime. |
| headingLevel | Field Type  int  Description  The heading level setting that controls layout, limits, or processing order. |
| help | Field Type  boolean  Description  Indicates whether help is enabled for the OmniScript configuration. |
| helpText | Field Type  string  Description  The help text text shown in the OmniScript user interface. |
| hide | Field Type  boolean  Description  Indicates whether hide is enabled for the OmniScript configuration. |
| hideEditButton | Field Type  boolean  Description  Indicates whether hide edit button is enabled for the OmniScript configuration. |
| hideGroupSep | Field Type  boolean  Description  Indicates whether hide group sep is enabled for the OmniScript configuration. |
| hideLabel | Field Type  boolean  Description  Indicates whether hide label is enabled for the OmniScript configuration. |
| hideMap | Field Type  boolean  Description  Indicates whether hide map is enabled for the OmniScript configuration. |
| horizontalMode | Field Type  boolean  Description  Indicates whether horizontal mode is enabled for the OmniScript configuration. |
| htmlTemplateId | Field Type  string  Description  The html template id used to reference related OmniScript resources or records. |
| iconName | Field Type  string  Description  The icon name used to identify this OmniScript artifact in metadata. |
| iconPosition | Field Type  string  Description  The icon position value used by OmniScript at runtime. |
| iconVariant | Field Type  string  Description  The icon variant value used by OmniScript at runtime. |
| ignoreCache | Field Type  boolean  Description  Indicates whether ignore cache is enabled for the OmniScript configuration. |
| imageCountInRow | Field Type  int  Description  The image count in row setting that controls layout, limits, or processing order. |
| inProgressMessage | Field Type  string  Description  The in progress message text shown in the OmniScript user interface. |
| inputWidth | Field Type  int  Description  The input width setting that controls layout, limits, or processing order. |
| instruction | Field Type  string  Description  The instruction value used by OmniScript at runtime. |
| instructionKey | Field Type  string  Description  The instruction key used to reference related OmniScript resources or records. |
| integrationProcedureKey | Field Type  string  Description  The integration procedure key used to reference related OmniScript resources or records. |
| invalidIdMessage | Field Type  string  Description  The invalid id message text shown in the OmniScript user interface. |
| invokeMode | Field Type  string  Description  The invoke mode value that determines how this OmniScript setting is interpreted. |
| knowledgeOptions | Field Type  string  Description  The knowledge options value used by OmniScript at runtime. |
| label | Field Type  string  Description  The label text shown in the OmniScript user interface. |
| loginAction | Field Type  string  Description  The login action value used by OmniScript at runtime. |
| lwcComponentOverride | Field Type  string  Description  The lwc component override value used by OmniScript at runtime. |
| lwcName | Field Type  string  Description  The lwc name used to identify this OmniScript artifact in metadata. |
| mask | Field Type  string  Description  The mask value used by OmniScript at runtime. |
| matrixInputParameters | Field Type  string  Description  The matrix input parameters value used by OmniScript at runtime. |
| max | Field Type  string  Description  The max setting that controls limits, layout, or processing behavior. |
| maxDate | Field Type  string  Description  The max date setting that controls limits, layout, or processing behavior. |
| maxDisplay | Field Type  int  Description  The max display setting that controls limits, layout, or processing behavior. |
| maxLength | Field Type  int  Description  The max length setting that controls layout, limits, or processing order. |
| maxTime | Field Type  string  Description  The max time setting that controls limits, layout, or processing behavior. |
| message | Field Type  string  Description  The message text shown in the OmniScript user interface. |
| messages | Field Type  string  Description  The messages value used by OmniScript at runtime. |
| min | Field Type  string  Description  The min setting that controls limits, layout, or processing behavior. |
| minDate | Field Type  string  Description  The min date setting that controls limits, layout, or processing behavior. |
| minLength | Field Type  int  Description  The min length setting that controls layout, limits, or processing order. |
| minTime | Field Type  string  Description  The min time setting that controls limits, layout, or processing behavior. |
| mode | Field Type  string  Description  The mode value that determines how this OmniScript setting is interpreted. |
| modelDateFormat | Field Type  string  Description  The model date format value that determines how this OmniScript setting is interpreted. |
| modelTimeFormat | Field Type  string  Description  The model time format value that determines how this OmniScript setting is interpreted. |
| multiple | Field Type  boolean  Description  Indicates whether multiple is enabled for the OmniScript configuration. |
| namedCredential | Field Type  string  Description  The named credential value used by OmniScript at runtime. |
| newItemLabel | Field Type  string  Description  The new item label text shown in the OmniScript user interface. |
| newLabel | Field Type  string  Description  The new label text shown in the OmniScript user interface. |
| nextLabel | Field Type  string  Description  The next label text shown in the OmniScript user interface. |
| nextWidth | Field Type  int  Description  The next width setting that controls layout, limits, or processing order. |
| objectAction | Field Type  string  Description  The object action that identifies the data source or target used by OmniScript. |
| omniScriptRootConfig | Field Type  [OmniScriptPropertySetConfig](#OmniScriptPropertySetConfig)  Description  The omniscript root config used to configure OmniScript behavior. |
| optionHeight | Field Type  int  Description  The option height setting that controls limits, layout, or processing behavior. |
| optionSource | Field Type  string  Description  The option source that identifies the data source or target used by OmniScript. |
| optionWidth | Field Type  int  Description  The option width setting that controls layout, limits, or processing order. |
| options | Field Type  string  Description  The options value used by OmniScript at runtime. |
| orgWideEmailAddress | Field Type  string  Description  The org wide email address value used by OmniScript at runtime. |
| padding | Field Type  int  Description  The padding value used by OmniScript at runtime. |
| pattern | Field Type  string  Description  The pattern value used by OmniScript at runtime. |
| placeholder | Field Type  string  Description  The placeholder text shown in the OmniScript user interface. |
| postMessage | Field Type  string  Description  The post message text shown in the OmniScript user interface. |
| postTransformBundle | Field Type  string  Description  The post transform bundle used to configure OmniScript behavior. |
| preTransformBundle | Field Type  string  Description  The pre transform bundle used to configure OmniScript behavior. |
| previousLabel | Field Type  string  Description  The previous label text shown in the OmniScript user interface. |
| previousWidth | Field Type  int  Description  The previous width setting that controls layout, limits, or processing order. |
| ptrnErrText | Field Type  string  Description  The ptrn err text text shown in the OmniScript user interface. |
| pubsub | Field Type  boolean  Description  Indicates whether pubsub is enabled for the OmniScript configuration. |
| radioLabels | Field Type  string  Description  The radio labels value used by OmniScript at runtime. |
| radioLabelsWidth | Field Type  int  Description  The radio labels width setting that controls layout, limits, or processing order. |
| rangeHigh | Field Type  int  Description  The range high value used by OmniScript at runtime. |
| rangeLow | Field Type  int  Description  The range low value used by OmniScript at runtime. |
| readOnly | Field Type  boolean  Description  Indicates whether read only is enabled for the OmniScript configuration. |
| recordAction | Field Type  string  Description  The record action value used by OmniScript at runtime. |
| redirectNextLabel | Field Type  string  Description  The redirect next label text shown in the OmniScript user interface. |
| redirectNextWidth | Field Type  int  Description  The redirect next width setting that controls layout, limits, or processing order. |
| redirectPageName | Field Type  string  Description  The redirect page name used to identify this OmniScript artifact in metadata. |
| redirectPreviousLabel | Field Type  string  Description  The redirect previous label text shown in the OmniScript user interface. |
| redirectPreviousWidth | Field Type  int  Description  The redirect previous width setting that controls layout, limits, or processing order. |
| redirectTemplateUrl | Field Type  string  Description  The redirect template url reference used by OmniScript integrations or rendering. |
| remoteClass | Field Type  string  Description  The remote class value used by OmniScript at runtime. |
| remoteConfirmMsg | Field Type  string  Description  The remote confirm msg value used by OmniScript at runtime. |
| remoteMethod | Field Type  string  Description  The remote method logic expression used during OmniScript processing. |
| remoteOptions | Field Type  string  Description  The remote options value used by OmniScript at runtime. |
| remoteTimeout | Field Type  int  Description  The remote timeout setting that controls limits, layout, or processing behavior. |
| repeat | Field Type  boolean  Description  Indicates whether repeat is enabled for the OmniScript configuration. |
| repeatClone | Field Type  boolean  Description  Indicates whether repeat clone is enabled for the OmniScript configuration. |
| repeatLimit | Field Type  int  Description  The repeat limit value used by OmniScript at runtime. |
| replace | Field Type  boolean  Description  Indicates whether replace is enabled for the OmniScript configuration. |
| required | Field Type  boolean  Description  Indicates whether required is enabled for the OmniScript configuration. |
| responseJSONNode | Field Type  string  Description  The response jsonnode value used by OmniScript at runtime. |
| responseJSONPath | Field Type  string  Description  The response jsonpath used to read or write runtime data. |
| restMethod | Field Type  string  Description  The rest method logic expression used during OmniScript processing. |
| restOptions | Field Type  string  Description  The rest options value used by OmniScript at runtime. |
| restPath | Field Type  string  Description  The rest path used to read or write runtime data. |
| restoreDefaultValuesOnCancel | Field Type  boolean  Description  Indicates whether restore default values on cancel is enabled for the OmniScript configuration. |
| sanitize | Field Type  boolean  Description  Indicates whether sanitize is enabled for the OmniScript configuration. |
| saveChangesLabel | Field Type  string  Description  The save changes label text shown in the OmniScript user interface. |
| saveLabel | Field Type  string  Description  The save label text shown in the OmniScript user interface. |
| saveMessage | Field Type  string  Description  The save message text shown in the OmniScript user interface. |
| selectCheckBox | Field Type  string  Description  The select check box value used by OmniScript at runtime. |
| selectMode | Field Type  string  Description  The select mode value that determines how this OmniScript setting is interpreted. |
| selectSobject | Field Type  string  Description  The select sobject value used by OmniScript at runtime. |
| sendJSONNode | Field Type  string  Description  The send jsonnode value used by OmniScript at runtime. |
| sendJSONPath | Field Type  string  Description  The send jsonpath used to read or write runtime data. |
| show | Field Type  string  Description  The show value used by OmniScript at runtime. |
| showInputWidth | Field Type  boolean  Description  Indicates whether show input width is enabled for the OmniScript configuration. |
| showPersistentComponent | Field Type  string  Description  The show persistent component value used by OmniScript at runtime. |
| showPopup | Field Type  boolean  Description  Indicates whether show popup is enabled for the OmniScript configuration. |
| signerInformation | Field Type  string  Description  The signer information value used by OmniScript at runtime. |
| sobjectMapping | Field Type  string  Description  The sobject mapping collection that maps or groups related OmniScript data. |
| ssm | Field Type  boolean  Description  Indicates whether ssm is enabled for the OmniScript configuration. |
| staticDocList | Field Type  string  Description  The static doc list collection that maps or groups related OmniScript data. |
| step | Field Type  int  Description  The step value used by OmniScript at runtime. |
| subLabel | Field Type  string  Description  The sub label text shown in the OmniScript user interface. |
| sumElement | Field Type  string  Description  The sum element value used by OmniScript at runtime. |
| svgIcon | Field Type  string  Description  The svg icon value used by OmniScript at runtime. |
| svgSprite | Field Type  string  Description  The svg sprite value used by OmniScript at runtime. |
| targetFilter | Field Type  string  Description  The target filter that identifies the data source or target used by OmniScript. |
| targetId | Field Type  string  Description  The target id used to reference related OmniScript resources or records. |
| targetLWCLayout | Field Type  string  Description  The target lwclayout that identifies the data source or target used by OmniScript. |
| targetType | Field Type  string  Description  The target type value that determines how this OmniScript setting is interpreted. |
| templateName | Field Type  string  Description  The template name used to identify this OmniScript artifact in metadata. |
| text | Field Type  string  Description  The text text shown in the OmniScript user interface. |
| textKey | Field Type  string  Description  The text key text shown in the OmniScript user interface. |
| timeFormat | Field Type  string  Description  The time format value that determines how this OmniScript setting is interpreted. |
| timeInterval | Field Type  int  Description  The time interval value used by OmniScript at runtime. |
| timeType | Field Type  string  Description  The time type value that determines how this OmniScript setting is interpreted. |
| timezone | Field Type  string  Description  The timezone value used by OmniScript at runtime. |
| type | Field Type  string  Description  The type value that determines how this OmniScript setting is interpreted. |
| typeAheadKey | Field Type  string  Description  The type ahead key used to reference related OmniScript resources or records. |
| uploadContDoc | Field Type  boolean  Description  Indicates whether upload cont doc is enabled for the OmniScript configuration. |
| useContinuation | Field Type  boolean  Description  Indicates whether use continuation is enabled for the OmniScript configuration. |
| useDataJson | Field Type  boolean  Description  Indicates whether use data json is enabled for the OmniScript configuration. |
| useTemplate | Field Type  boolean  Description  Indicates whether use template is enabled for the OmniScript configuration. |
| validateExpression | Field Type  string  Description  The validate expression logic expression used during OmniScript processing. |
| validationRequired | Field Type  string  Description  The validation required value used by OmniScript at runtime. |
| valueSvgMap | Field Type  string  Description  The value svg map collection that maps or groups related OmniScript data. |
| variant | Field Type  string  Description  The variant value used by OmniScript at runtime. |
| wpm | Field Type  boolean  Description  Indicates whether wpm is enabled for the OmniScript configuration. |
| xmlPostTransformBundle | Field Type  string  Description  The xml post transform bundle used to configure OmniScript behavior. |
| xmlPreTransformBundle | Field Type  string  Description  The xml pre transform bundle used to configure OmniScript behavior. |

## OmniScriptPropertySetConfig

| Field Name | Description |
| --- | --- |
| accessibilityToggle | Field Type  boolean  Description  Indicates whether accessibility toggle is enabled for the OmniScript configuration. |
| allowCancel | Field Type  boolean  Description  Indicates whether cancel is enabled for this OmniScript configuration. |
| allowSaveChanges | Field Type  boolean  Description  Indicates whether users can save changes made in the OmniScript element. |
| allowSaveForLater | Field Type  boolean  Description  Indicates whether users can save progress and resume the OmniScript later. |
| autoFocus | Field Type  boolean  Description  Indicates whether auto focus is enabled for the OmniScript configuration. |
| autoSaveChanges | Field Type  boolean  Description  Indicates whether auto save changes is enabled for the OmniScript configuration. |
| autoSaveOnStepNext | Field Type  boolean  Description  Indicates whether auto save on step next is enabled for the OmniScript configuration. |
| bulk | Field Type  boolean  Description  Indicates whether bulk is enabled for the OmniScript configuration. |
| cancelRedirectPageName | Field Type  string  Description  The cancel redirect page name used to identify this OmniScript artifact in metadata. |
| cancelRedirectTemplateUrl | Field Type  string  Description  The cancel redirect template url reference used by OmniScript integrations or rendering. |
| cancelSource | Field Type  string  Description  The cancel source that identifies the data source or target used by OmniScript. |
| cancelType | Field Type  string  Description  The cancel type value that determines how this OmniScript setting is interpreted. |
| consoleTabIcon | Field Type  string  Description  The console tab icon value used by OmniScript at runtime. |
| consoleTabLabel | Field Type  string  Description  The console tab label text shown in the OmniScript user interface. |
| consoleTabTitle | Field Type  string  Description  The console tab title text shown in the OmniScript user interface. |
| currencyCode | Field Type  string  Description  The currency code value used by OmniScript at runtime. |
| currentLanguage | Field Type  string  Description  The current language value used by OmniScript at runtime. |
| disableUnloadWarn | Field Type  boolean  Description  Indicates whether disable unload warn is enabled for the OmniScript configuration. |
| dynamicProperties | Field Type  string  Description  The dynamic properties used to configure OmniScript behavior. |
| elementTypeToHTMLTemplateMapping | Field Type  string  Description  The element type to htmltemplate mapping value that determines how this OmniScript setting is interpreted. |
| enableKnowledge | Field Type  boolean  Description  Indicates whether knowledge is enabled for this OmniScript configuration. |
| errorMessage | Field Type  string  Description  The error message text shown in the OmniScript user interface. |
| hideStepChart | Field Type  boolean  Description  Indicates whether hide step chart is enabled for the OmniScript configuration. |
| knowledgeArticleTypeQueryFieldsMap | Field Type  string  Description  The knowledge article type query fields map value that determines how this OmniScript setting is interpreted. |
| lkObjName | Field Type  string  Description  The lk obj name used to identify this OmniScript artifact in metadata. |
| mergeSavedData | Field Type  boolean  Description  Indicates whether merge saved data is enabled for the OmniScript configuration. |
| message | Field Type  string  Description  The message text shown in the OmniScript user interface. |
| persistentComponent | Field Type  string  Description  The persistent component value used by OmniScript at runtime. |
| pubsub | Field Type  boolean  Description  Indicates whether pubsub is enabled for the OmniScript configuration. |
| rtpSeed | Field Type  boolean  Description  Indicates whether rtp seed is enabled for the OmniScript configuration. |
| saveContentEncoded | Field Type  boolean  Description  Indicates whether save content encoded is enabled for the OmniScript configuration. |
| saveExpireInDays | Field Type  int  Description  The save expire in days value used by OmniScript at runtime. |
| saveForLaterRedirectPageName | Field Type  string  Description  The save for later redirect page name used to identify this OmniScript artifact in metadata. |
| saveForLaterRedirectTemplateUrl | Field Type  string  Description  The save for later redirect template url reference used by OmniScript integrations or rendering. |
| saveNameTemplate | Field Type  string  Description  The save name template used to identify this OmniScript artifact in metadata. |
| saveObjectId | Field Type  string  Description  The object ID used when saving OmniScript data. |
| saveURLPatterns | Field Type  string  Description  The save urlpatterns value used by OmniScript at runtime. |
| scrollBehavior | Field Type  string  Description  The scroll behavior value used by OmniScript at runtime. |
| seedDataJSON | Field Type  string  Description  The seed data json value used by OmniScript at runtime. |
| showInputWidth | Field Type  boolean  Description  Indicates whether show input width is enabled for the OmniScript configuration. |
| ssm | Field Type  boolean  Description  Indicates whether ssm is enabled for the OmniScript configuration. |
| stepChartPlacement | Field Type  string  Description  The step chart placement value used by OmniScript at runtime. |
| stylesheet | Field Type  string  Description  The stylesheet value used by OmniScript at runtime. |
| timeTracking | Field Type  boolean  Description  Indicates whether time tracking is enabled for the OmniScript configuration. |
| trackingCustomData | Field Type  string  Description  The tracking custom data value used by OmniScript at runtime. |
| visualforcePagesAvailableInPreview | Field Type  string  Description  The visualforce pages available in preview value used by OmniScript at runtime. |
| wpm | Field Type  boolean  Description  Indicates whether wpm is enabled for the OmniScript configuration. |

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
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information about
using the manifest file, see [Deploying and
Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
