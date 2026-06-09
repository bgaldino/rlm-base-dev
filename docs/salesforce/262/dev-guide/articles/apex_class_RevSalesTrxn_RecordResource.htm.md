---
page_id: apex_class_RevSalesTrxn_RecordResource.htm
title: RecordResource Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_RecordResource.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# RecordResource Class

Contains constructors and properties to create a record object from the field values of a
sales transaction.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.")

## Example

```
RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'POST');
```

- **[RecordResource Constructors](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_constructors)**  
  Learn more about the available constructors with the RecordResource class.
- **[RecordResource Properties](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_properties)**  
  Learn more about the available properties with the RecordResource class.

## RecordResource Constructors

Learn more about the available constructors with the RecordResource class.

The `RecordResource` class has these constructors.

- **[RecordResource(type, method, groupAction, criteria)](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_ctor)**  
  Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties. Additionally, you can group order or quote line items based on a criteria by using the groupAction and criteria properties.
- **[RecordResource(type, method, id)](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_ctor_2)**  
  Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties.
- **[RecordResource(type, method)](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_ctor_3)**  
  Creates an instance of the RecordResource class to assign the values to the fields of a sales transaction by using the sObject type and API method properties.

### RecordResource(type, method, groupAction, criteria)

Creates an instance of the RecordResource class to assign values to the fields of a
sales transaction by using the sObject type, API method, and sales transaction ID properties.
Additionally, you can group order or quote line items based on a criteria by using the
groupAction and criteria properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, String groupAction, Map<String,ANY> criteria)`

#### Parameters

type
:   Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
:   Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result
    using the `getSObjectType()`method.

method
:   Type: String
:   Method for the API request, such as POST, PATCH, or DELETE.

groupAction
:   Type: String
:   Action to group order or quote line items. Valid values are:

    - `GroupBy`
    - `Group`
    - `Ungroup`
    - `GroupAll`
    - `DeleteGroup`

criteria
:   Type: Map<String,ANY>
:   Criteria to group order or quote line items. For example, group order or quote line items based
    on a monthly billing frequency.

### RecordResource(type, method, id)

Creates an instance of the RecordResource class to assign values to the fields of a sales
transaction by using the sObject type, API method, and sales transaction ID
properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, Id id)`

#### Parameters

type
:   Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
:   Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result
    using the `getSObjectType()`method.

method
:   Type: String
:   Method for the API request, such as POST, PATCH, or DELETE.

id
:   Type: Id
:   ID of the sales transaction, such as a quote or an order.

### RecordResource(type, method)

Creates an instance of the RecordResource class to assign the values to the fields of a
sales transaction by using the sObject type and API method properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method)`

#### Parameters

type
:   Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
:   Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result
    using the `getSObjectType()`method.

method
:   Type: String
:   Method for the API request, such as POST, PATCH, or DELETE.

## RecordResource Properties

Learn more about the available properties with the RecordResource class.

The `RecordResource` class includes these properties.

- **[criteria](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_criteria)**  
  Set the criteria property to group order or quote line items. For example, group order or quote line items based on a monthly billing frequency.
- **[fieldValues](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_fieldValues)**  
  Set the fieldValues property to assign values to the fields to update the sales transaction.
- **[groupAction](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_groupAction)**  
  Set the groupAction property to group order or quote line items.
- **[id](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_id)**  
  Set the id property to assign the ID of the sales transaction record.
- **[method](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_method)**  
  Set the method property to specify the API request method, such as POST, PATCH, or DELETE.
- **[type](./apex_class_RevSalesTrxn_RecordResource.htm.md#apex_RevSalesTrxn_RecordResource_type)**  
  Set the type property to assign the object type that’s returned from the field describe result by using the getReferenceTo() method or from the sObject describe result by using the getSObjectType() method.

### criteria

Set the criteria property to group order or quote line items. For example, group order
or quote line items based on a monthly billing frequency.

#### Signature

`public Map<String,ANY> criteria {get; set;}`

#### Property Value

Type: Map<String,ANY>

### fieldValues

Set the fieldValues property to assign values to the fields to update the sales
transaction.

#### Signature

`public Map<String,ANY> fieldValues {get; set;}`

#### Property Value

Type: [List](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_methods_system_list.htm#apex_methods_system_list "HTML (New Window)")Map<String,ANY>

### groupAction

Set the groupAction property to group order or quote line items.

You can group order or quote line items based on location, work types, or departments, if
groups are enabled for your org. Groups provide a visualization of the products to view
large quotes.

#### Signature

`public String groupAction {get; set;}`

#### Property Value

Type: String

Valid values are:

- `GroupBy`
- `Group`
- `Ungroup`
- `GroupAll`
- `DeleteGroup`

### id

Set the id property to assign the ID of the sales transaction record.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### method

Set the method property to specify the API request method, such as POST, PATCH, or
DELETE.

#### Signature

`public String method {get; set;}`

#### Property Value

Type: String

### type

Set the type property to assign the object type that’s returned from the field describe
result by using the getReferenceTo() method or from the sObject describe result by using the
getSObjectType() method.

#### Signature

`public Schema.SObjectType type {get; set;}`

#### Property Value

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_class_Schema_SObjectType.htm "HTML (New Window)")
