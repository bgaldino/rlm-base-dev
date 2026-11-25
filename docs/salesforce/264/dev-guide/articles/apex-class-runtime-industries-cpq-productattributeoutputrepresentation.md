---
page_id: apex-class-runtime-industries-cpq-productattributeoutputrepresentation
title: ProductAttributeOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productattributeoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductAttributeOutputRepresentation Class

Contains details about the attribute in a product configuration.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductAttributeOutputRepresentation Properties](#productattributeoutputrepresentation-properties)**

Learn more about the properties available with the ProductAttributeOutputRepresentation class.

## ProductAttributeOutputRepresentation Properties

Learn more about the properties available with the ProductAttributeOutputRepresentation class.

The `ProductAttributeOutputRepresentation` class includes these properties.

- 

**[additionalFields](#additionalfields)**

Get the key-value pairs of additional standard or custom fields and their values for the product attribute.

- 

**[attributeCategoryId](#attributecategoryid)**

Get the ID of the attribute category.

- 

**[attributeNameOverride](#attributenameoverride)**

Get the name override value of the attribute.

- 

**[attributePickList](#attributepicklist)**

Get the picklist values of the attribute.

- 

**[code](#code)**

Get the code of the attribute.

- 

**[dataType](#datatype)**

Get the data type of the attribute.

- 

**[defaultHelpText](#defaulthelptext)**

Get the default help text value of the attribute.

- 

**[defaultValue](#defaultvalue)**

Get the default value of the attribute.

- 

**[description](#description)**

Get the description of the attribute.

- 

**[developerName](#developername)**

Get the developer name of the product attribute.

- 

**[displayTypeOverride](#displaytypeoverride)**

Get the override value of the display type of the attribute.

- 

**[hidden](#hidden)**

Indicates whether the attribute is hidden (true) or not (false).

- 

**[id](#id)**

Get the ID of the attribute.

- 

**[isCloneable](#iscloneable)**

Indicates whether the attribute is cloneable (true) or not (false).

- 

**[isConfigurable](#isconfigurable)**

Indicates whether the attribute is configurable (true) or not (false).

- 

**[isEncrypted](#isencrypted)**

Indicates whether the attribute is encrypted (true) or not (false).

- 

**[isPriceImpacting](#ispriceimpacting)**

Indicates whether this is a price impacting attribute (true) or not (false).

- 

**[isReadOnly](#isreadonly)**

Indicates whether the attribute is read-only (true) or not (false).

- 

**[isRequired](#isrequired)**

Indicates whether the attribute is required (true) or not (false).

- 

**[label](#label)**

Get the label of the attribute.

- 

**[maximumValue](#maximumvalue)**

Get the maximum value for the product attribute.

- 

**[minimumValue](#minimumvalue)**

Get the minimum value for the product attribute.

- 

**[name](#name)**

Get the name of the attribute.

- 

**[sequence](#sequence)**

Get the sequence values of the attribute.

- 

**[status](#status)**

Get the status of the attribute.

- 

**[stepValue](#stepvalue)**

Get the step value for the attribute.

- 

**[unitOfMeasure](#unitofmeasure)**

Get details about the unit of measure associated with an attribute.

- 

**[userValue](#uservalue)**

Get the user value of the attribute.

- 

**[valueDescription](#valuedescription)**

Get the value description of the attribute.

### additionalFields

Get the key-value pairs of additional standard or custom fields and their values for the product attribute.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### attributeCategoryId

Get the ID of the attribute category.

#### Signature

`public String attributeCategoryId {get; set;}`

#### Property Value

Type: String

### attributeNameOverride

Get the name override value of the attribute.

#### Signature

`public String attributeNameOverride {get; set;}`

#### Property Value

Type: String

### attributePickList

Get the picklist values of the attribute.

#### Signature

`public runtime_industries_cpq.AttributePickListOutputRepresentation attributePickList {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.AttributePickListOutputRepresentation](./apex-class-runtime-industries-cpq-attributepicklistoutputrepresentation.md#attributepicklistoutputrepresentation-class)

### code

Get the code of the attribute.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### dataType

Get the data type of the attribute.

#### Signature

`public String dataType {get; set;}`

#### Property Value

Type: String

### defaultHelpText

Get the default help text value of the attribute.

#### Signature

`public String defaultHelpText {get; set;}`

#### Property Value

Type: String

### defaultValue

Get the default value of the attribute.

#### Signature

`public String defaultValue {get; set;}`

#### Property Value

Type: String

### description

Get the description of the attribute.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### developerName

Get the developer name of the product attribute.

#### Signature

`public String developerName {get; set;}`

#### Property Value

Type: String

### displayTypeOverride

Get the override value of the display type of the attribute.

#### Signature

`public String displayTypeOverride {get; set;}`

#### Property Value

Type: String

### hidden

Indicates whether the attribute is hidden (true) or not (false).

#### Signature

`public Boolean hidden {get; set;}`

#### Property Value

Type: Boolean

### id

Get the ID of the attribute.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isCloneable

Indicates whether the attribute is cloneable (true) or not (false).

#### Signature

`public Boolean isCloneable {get; set;}`

#### Property Value

Type: Boolean

### isConfigurable

Indicates whether the attribute is configurable (true) or not (false).

#### Signature

`public Boolean isConfigurable {get; set;}`

#### Property Value

Type: Boolean

### isEncrypted

Indicates whether the attribute is encrypted (true) or not (false).

#### Signature

`public Boolean isEncrypted {get; set;}`

#### Property Value

Type: Boolean

### isPriceImpacting

Indicates whether this is a price impacting attribute (true) or not (false).

#### Signature

`public Boolean isPriceImpacting {get; set;}`

#### Property Value

Type: Boolean

### isReadOnly

Indicates whether the attribute is read-only (true) or not (false).

#### Signature

`public Boolean isReadOnly {get; set;}`

#### Property Value

Type: Boolean

### isRequired

Indicates whether the attribute is required (true) or not (false).

#### Signature

`public Boolean isRequired {get; set;}`

#### Property Value

Type: Boolean

### label

Get the label of the attribute.

#### Signature

`public String label {get; set;}`

#### Property Value

Type: String

### maximumValue

Get the maximum value for the product attribute.

#### Signature

`public String maximumValue {get; set;}`

#### Property Value

Type: String

### minimumValue

Get the minimum value for the product attribute.

#### Signature

`public String minimumValue {get; set;}`

#### Property Value

Type: String

### name

Get the name of the attribute.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### sequence

Get the sequence values of the attribute.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

### status

Get the status of the attribute.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### stepValue

Get the step value for the attribute.

#### Signature

`public String stepValue {get; set;}`

#### Property Value

Type: String

### unitOfMeasure

Get details about the unit of measure associated with an attribute.

#### Signature

`public ConnectApi.UnitOfMeasureOutputRepresentation unitOfMeasure {get; set;}`

#### Property Value

Type: ConnectApi.UnitOfMeasureOutputRepresentation

### userValue

Get the user value of the attribute.

#### Signature

`public String userValue {get; set;}`

#### Property Value

Type: String

### valueDescription

Get the value description of the attribute.

#### Signature

`public String valueDescription {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productattributeoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
