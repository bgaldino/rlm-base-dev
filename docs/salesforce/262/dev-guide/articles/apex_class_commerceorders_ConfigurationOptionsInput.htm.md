---
page_id: apex_class_commerceorders_ConfigurationOptionsInput.htm
title: ConfigurationOptionsInput Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_ConfigurationOptionsInput.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# ConfigurationOptionsInput Class

Contains methods and properties to set the configuration options for the input to the
product configurator.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Usage

This class holds the required details of the product configuration input. Set the
class properties to enable default configuration, execution of configuration rules,
and validation of the product catalog. Use these class properties as an input to the
[PlaceOrderExecutor Class](./apex_class_commerceorders_PlaceOrderExecutor.htm.md#apex_class_commerceorders_PlaceOrderExecutor "Contains methods to place an order with details of the graph request, pricing preferences, and configuration options.") method.

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

- **[ConfigurationOptionsInput Properties](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_properties)**  
  Set the `ConfigurationOptionsInput` class properties to add default configuration, execute configuration rules, and validate the product catalog.
- **[ConfigurationOptionsInput Methods](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_methods)**  
  Learn more about the methods available with the `ConfigurationOptionsInput` class.

## ConfigurationOptionsInput Properties

Set the `ConfigurationOptionsInput` class properties
to add default configuration, execute configuration rules, and validate the product
catalog.

The `ConfigurationOptionsInput` class includes these
properties.

- **[addDefaultConfiguration](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_addDefaultConfiguration)**  
  Sets the default product configuration, such as bundle and product attributes, for an order request.
- **[executeConfigurationRules](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_executeConfigurationRules)**  
  Sets the requirement for an order to adhere to the configuration rules.
- **[validateAmendRenewCancel](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_validateAmendRenewCancel)**  
  Sets the requirement to run validations related to amend, renew, or cancel processes.
- **[validateProductCatalog](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_validateProductCatalog)**  
  Sets the requirement to validate an order against the product catalog.

### addDefaultConfiguration

Sets the default product configuration, such as bundle and product attributes, for an
order request.

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

Indicates whether the order must
adhere to configuration rules during processing (`true`)
or bypass them (`false`).

### validateAmendRenewCancel

Sets the requirement to run validations related to amend, renew, or cancel
processes.

#### Signature

`public Boolean validateAmendRenewCancel {get; set;}`

#### Property Value

Type: Boolean

Indicates whether to run validations
related to amend, renew, or cancel processes (`true`) or
not (`false`).

### validateProductCatalog

Sets the requirement to validate an order against the product catalog.

#### Signature

`public Boolean validateProductCatalog {get; set;}`

#### Property Value

Type: Boolean

Indicates whether the order must be validated against the product catalog (`true`) or not (`false`).

## ConfigurationOptionsInput Methods

Learn more about the methods available with the `ConfigurationOptionsInput` class.

The `ConfigurationOptionsInput` class includes these
methods.

- **[equals(obj)](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_equals)**  
  Determines the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_hashCode)**  
  Determines the uniqueness of the external object records in a list.
- **[toString()](./apex_class_commerceorders_ConfigurationOptionsInput.htm.md#apex_commerceorders_ConfigurationOptionsInput_toString)**  
  Converts a value to a string.

### equals(obj)

Determines the equality of external objects in a list. This method is dynamic and is
based on the `equals()` method in Java.

#### Signature

`public Boolean equals(Object obj)`

#### Parameters

obj
:   Type: Object
:   Reference object that’s used to compare with the class object.

#### Return Value

Type: Boolean

Indicates if the class object is same as the reference object (`true`) or not (`false`).

### hashCode()

Determines the uniqueness of the external object records in a list.

#### Signature

`public Integer hashCode()`

#### Return Value

Type: Integer

Integer hash code that represents the
value of the object. Equal objects as per the `equals()` method must return the same hash code.

### toString()

Converts a value to a string.

#### Signature

`public String toString()`

#### Return Value

Type: String
