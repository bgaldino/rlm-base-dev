---
page_id: apex-class-placequote-configurationoptionsinput
title: ConfigurationOptionsInput Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-configurationoptionsinput.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_class_placequote_ConfigurationOptionsInput.htm
fetched_at: 2026-11-25
---

# ConfigurationOptionsInput Class

Contains methods and properties to set the configuration options for the input to the product configurator.

## Namespace

[PlaceQuote](./apex-namespace-placequote.md)

## Usage

This class holds the required details of the product configuration input. Set the class properties to enable default configuration, execution of configuration rules, and validation of the product catalog. Use these class properties as an input to the [PlaceQuoteRLMApexProcessor](./apex-class-placequote-placequoterlmapexprocessor.md#placequoterlmapexprocessor-class) class method.

## Example

```
PlaceQuote.GraphRequest graph = new PlaceQuote.GraphRequest('test',listOfRecords);
    PlaceQuote.PricingPreferenceEnum pricingPreference = PlaceQuote.PricingPreferenceEnum.System;
    PlaceQuote.ConfigurationInputEnum configurationPreference = PlaceQuote.ConfigurationInputEnum.RunAndAllowErrors;
    PlaceQuote.ConfigurationOptionsInput cInput = new PlaceQuote.ConfigurationOptionsInput();
    cInput.addDefaultConfiguration = true;
    cInput.executeConfigurationRules = true;
    cInput.validateAmendRenewCancel = true;
    cInput.validateProductCatalog = true;
        //Place Quote Call
     PlaceQuote.PlaceQuoteResponse resp = PlaceQuote.PlaceQuoteRLMApexProcessor.execute(pricingPreference,graph,configurationPreference,cInput);
```

- 

**[ConfigurationOptionsInput Properties](#configurationoptionsinput-properties)**

Set the `ConfigurationOptionsInput` class properties to add default configuration, execute configuration rules, and validate the product catalog.

- 

**[ConfigurationOptionsInput Methods](#configurationoptionsinput-methods)**

Learn more about the methods available with the `ConfigurationOptionsInput` class.

## ConfigurationOptionsInput Properties

Set the `ConfigurationOptionsInput` class properties to add default configuration, execute configuration rules, and validate the product catalog.

The `ConfigurationOptionsInput` class includes these properties.

- 

**[addDefaultConfiguration](#adddefaultconfiguration)**

Sets the default product configuration, such as bundle and product attributes, for a quote request.

- 

**[executeConfigurationRules](#executeconfigurationrules)**

Sets the requirement for a quote to adhere to the configuration rules.

- 

**[validateAmendRenewCancel](#validateamendrenewcancel)**

Sets the requirement to run validations related to amend, renew, or cancel processes.

- 

**[validateProductCatalog](#validateproductcatalog)**

Sets the requirement to validate a quote against the product catalog.

### addDefaultConfiguration

Sets the default product configuration, such as bundle and product attributes, for a quote request.

#### Signature

`public Boolean addDefaultConfiguration {get; set;}`

#### Property Value

Type: Boolean

Indicates whether to automatically add default configuration to the order (`true`) or not (`false`).

### executeConfigurationRules

Sets the requirement for a quote to adhere to the configuration rules.

#### Signature

`public Boolean executeConfigurationRules {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the order must adhere to configuration rules during processing (`true`) or bypass them (`false`).

### validateAmendRenewCancel

Sets the requirement to run validations related to amend, renew, or cancel processes.

#### Signature

`public Boolean validateAmendRenewCancel {get; set;}`

#### Property Value

Type: Boolean

Indicates whether to run validations related to amend, renew, or cancel processes (`true`) or not (`false`).

### validateProductCatalog

Sets the requirement to validate a quote against the product catalog.

#### Signature

`public Boolean validateProductCatalog {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the quote must be validated against the product catalog (`true`) or not (`false`).

## ConfigurationOptionsInput Methods

Learn more about the methods available with the `ConfigurationOptionsInput` class.

The `ConfigurationOptionsInput` class includes these methods.

- 

**[equals(obj)](#equalsobj)**

Determines the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.

- 

**[hashCode()](#hashcode)**

Determines the uniqueness of the external object records in a list.

- 

**[toString()](#tostring)**

Converts a value to a string.

### equals(obj)

Determines the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.

#### Signature

`public Boolean equals(Object obj)`

#### Parameters

***obj***

Type: Object

Reference object that’s used to compare with the class object.

#### Return Value

Type: Boolean

Indicates if the class object is same as the reference object (`true`) or not (`false`).

### hashCode()

Determines the uniqueness of the external object records in a list.

#### Signature

`public Integer hashCode()`

#### Return Value

Type: Integer

Integer hash code that represents the value of the object. Equal objects as per the `equals()` method must return the same hash code.

### toString()

Converts a value to a string.

#### Signature

`public String toString()`

#### Return Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-configurationoptionsinput.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
