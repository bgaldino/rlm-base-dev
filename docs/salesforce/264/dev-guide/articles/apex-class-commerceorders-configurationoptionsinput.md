---
page_id: apex-class-commerceorders-configurationoptionsinput
title: ConfigurationOptionsInput Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-commerceorders-configurationoptionsinput.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-commerceorders
legacy_page_id: apex_class_commerceorders_ConfigurationOptionsInput.htm
fetched_at: 2026-11-25
---

# ConfigurationOptionsInput Class

Contains methods and properties to set the configuration options for the input to the product configurator.

## Namespace

[CommerceOrders](./apex-namespace-commerceorders.md)

## Usage

This class holds the required details of the product configuration input. Set the class properties to enable default configuration, execution of configuration rules, and validation of the product catalog. Use these class properties as an input to the [PlaceOrderExecutor Class](./apex-class-commerceorders-placeorderexecutor.md#placeorderexecutor-class) method.

## Example

```
CommerceOrders.ConfigurationOptionsInput configurationInput = new CommerceOrders.ConfigurationOptionsInput();
configurationInput.validateProductCatalog = true;
configurationInput.validateAmendRenewCancel = true;
configurationInput.executeConfigurationRules = true;
configurationInput.addDefaultConfiguration = true;

CommerceOrders.GraphRequest graph = new CommerceOrders.GraphRequest('testGraph', recordNodes);
CommerceOrders.PlaceOrderResult result = CommerceOrders.PlaceOrderExecutor.execute(graph, pricingPreference, configurationPreference, configurationInput);
```

- 

**[ConfigurationOptionsInput Properties](#configurationoptionsinput-properties)**

Set the `ConfigurationOptionsInput` class properties to add default configuration, execute configuration rules, and validate the product catalog.

- 

**[ConfigurationOptionsInput Methods](#configurationoptionsinput-methods)**

Learn more about the methods available with the `ConfigurationOptionsInput` class.

## ConfigurationOptionsInput Properties

Set the `ConfigurationOptionsInput` class properties to add default configuration, execute configuration rules, and validate the product catalog.

The `ConfigurationOptionsInput` class includes these properties.

- 

**[addDefaultConfiguration](#adddefaultconfiguration)**

Sets the default product configuration, such as bundle and product attributes, for an order request.

- 

**[executeConfigurationRules](#executeconfigurationrules)**

Sets the requirement for an order to adhere to the configuration rules.

- 

**[validateAmendRenewCancel](#validateamendrenewcancel)**

Sets the requirement to run validations related to amend, renew, or cancel processes.

- 

**[validateProductCatalog](#validateproductcatalog)**

Sets the requirement to validate an order against the product catalog.

### addDefaultConfiguration

Sets the default product configuration, such as bundle and product attributes, for an order request.

#### Signature

`public Boolean addDefaultConfiguration {get; set;}`

#### Property Value

Type: Boolean

Indicates whether to automatically add default configuration to the order (`true`) or not (`false`).

### executeConfigurationRules

Sets the requirement for an order to adhere to the configuration rules.

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

Sets the requirement to validate an order against the product catalog.

#### Signature

`public Boolean validateProductCatalog {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the order must be validated against the product catalog (`true`) or not (`false`).

## ConfigurationOptionsInput Methods

Learn more about the methods available with the `ConfigurationOptionsInput` class.

The `ConfigurationOptionsInput` class includes these methods.

- 

**[equals(obj)](#equalsobj)**

Determines the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.

- 

**[hashCode()](#hashcode)**

Determines the uniqueness of the external object records in a list.

- 

**[toString()](#tostring)**

Converts a value to a string.

### equals(obj)

Determines the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.

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

Integer hash code that represents the value of the object. Equal objects as per the `equals()` method must return the same hash code.

### toString()

Converts a value to a string.

#### Signature

`public String toString()`

#### Return Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-commerceorders-configurationoptionsinput.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
