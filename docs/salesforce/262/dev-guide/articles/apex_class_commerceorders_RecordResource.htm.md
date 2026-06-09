---
page_id: apex_class_commerceorders_RecordResource.htm
title: RecordResource Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_RecordResource.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# RecordResource Class

Contains constructors and properties to create a record object from field values of an
order.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Example

```
CommerceOrders.RecordResource orderRecord = new CommerceOrders.RecordResource(Order.getSobjectType(), 'POST');
orderRecord.fieldValues = orderFieldValues;
```

- **[RecordResource Constructors](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_constructors)**  
  Learn more about the available constructors with the `RecordResource` class.
- **[RecordResource Properties](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_properties)**  
  Learn more about the available properties with the `RecordResource` class.

## RecordResource Constructors

Learn more about the available constructors with the `RecordResource` class.

The `RecordResource` class includes these
constructors.

- **[RecordResource(type, method, id)](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_ctor)**  
  Creates an instance of the `RecordResource` class to assign values to the fields of an order item by using the sObject type, API method, and order ID properties.
- **[RecordResource(type, method)](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_ctor_2)**  
  Creates an instance of the `RecordResource` class to assign the values to the fields of an order item by using the sObject type and API method properties.

### RecordResource(type, method, id)

Creates an instance of the `RecordResource` class to
assign values to the fields of an order item by using the sObject type, API method, and order ID
properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, Id id)`

#### Parameters

type
:   Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
:   Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using
    the `getSObjectType()` method.

method
:   Type: String
:   Method for the API request, such as POST or PATCH.

id
:   Type: Id
:   ID of the order.

### RecordResource(type, method)

Creates an instance of the `RecordResource` class to
assign the values to the fields of an order item by using the sObject type and API method
properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method)`

#### Parameters

type
:   Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
:   Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result
    using the `getSObjectType()` method.

method
:   Type: String
:   Method for the API request, such as POST or PATCH.

## RecordResource Properties

Learn more about the available properties with the `RecordResource` class.

The `RecordResource` class includes these properties.

- **[fieldValues](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_fieldValues)**  
  Set the `fieldValues` property to assign values to the fields to update the order record.
- **[id](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_id)**  
  Set the `id` property to assign the ID of the order record.
- **[method](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_method)**  
  Set the `method` property to specify the API request method, such as POST or PATCH.
- **[type](./apex_class_commerceorders_RecordResource.htm.md#apex_commerceorders_RecordResource_type)**  
  Set the `type` property to assign the object type that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType()` method.

### fieldValues

Set the `fieldValues` property to assign values to the
fields to update the order record.

#### Signature

`public Map<String,ANY> fieldValues {get; set;}`

#### Property Value

Type: [List](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_methods_system_list.htm#apex_methods_system_list "HTML (New Window)")<Map<String,ANY>>

### id

Set the `id` property to assign the ID of the order
record.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### method

Set the `method` property to specify the API request
method, such as POST or PATCH.

#### Signature

`public String method {get; set;}`

#### Property Value

Type: String

### type

Set the `type` property to assign the object type that’s
returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType()` method.

#### Signature

`public Schema.SObjectType type {get; set;}`

#### Property Value

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
