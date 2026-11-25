---
page_id: apex-class-revsalestrxn-recordresource
title: RecordResource Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-recordresource.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_class_RevSalesTrxn_RecordResource.htm
fetched_at: 2026-11-25
---

# RecordResource Class

Contains constructors and properties to create a record object from the field values of a sales transaction.

## Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

## Example

```
RevSalesTrxn.RecordResource quoteRecord = new RevSalesTrxn.RecordResource(Quote.getSobjectType(),'POST');
```

- 

**[RecordResource Constructors](#recordresource-constructors)**

Learn more about the available constructors with the RecordResource class.

- 

**[RecordResource Properties](#recordresource-properties)**

Learn more about the available properties with the RecordResource class.

## RecordResource Constructors

Learn more about the available constructors with the RecordResource class.

The `RecordResource` class has these constructors.

- 

**[RecordResource(type, method, groupAction, criteria)](#recordresourcetype-method-groupaction-criteria)**

Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties. Additionally, you can group order or quote line items based on a criteria by using the groupAction and criteria properties.

- 

**[RecordResource(type, method, id)](#recordresourcetype-method-id)**

Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties.

- 

**[RecordResource(type, method)](#recordresourcetype-method)**

Creates an instance of the RecordResource class to assign the values to the fields of a sales transaction by using the sObject type and API method properties.

### RecordResource(type, method, groupAction, criteria)

Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties. Additionally, you can group order or quote line items based on a criteria by using the groupAction and criteria properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, String groupAction, Map<String,ANY> criteria)`

#### Parameters

***type***

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType() `method.

***method***

Type: String

Method for the API request, such as POST, PATCH, or DELETE.

***groupAction***

Type: String

Action to group order or quote line items. Valid values are:

- `GroupBy`

- `Group`

- `Ungroup`

- `GroupAll`

- `DeleteGroup`

***criteria***

Type: Map<String,ANY>

Criteria to group order or quote line items. For example, group order or quote line items based on a monthly billing frequency.

### RecordResource(type, method, id)

Creates an instance of the RecordResource class to assign values to the fields of a sales transaction by using the sObject type, API method, and sales transaction ID properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, Id id)`

#### Parameters

***type***

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType() `method.

***method***

Type: String

Method for the API request, such as POST, PATCH, or DELETE.

***id***

Type: Id

ID of the sales transaction, such as a quote or an order.

### RecordResource(type, method)

Creates an instance of the RecordResource class to assign the values to the fields of a sales transaction by using the sObject type and API method properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method)`

#### Parameters

***type***

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType()`method.

***method***

Type: String

Method for the API request, such as POST, PATCH, or DELETE.

## RecordResource Properties

Learn more about the available properties with the RecordResource class.

The `RecordResource` class includes these properties.

- 

**[criteria](#criteria)**

Set the criteria property to group order or quote line items. For example, group order or quote line items based on a monthly billing frequency.

- 

**[fieldValues](#fieldvalues)**

Set the fieldValues property to assign values to the fields to update the sales transaction.

- 

**[groupAction](#groupaction)**

Set the groupAction property to group order or quote line items.

- 

**[id](#id)**

Set the id property to assign the ID of the sales transaction record.

- 

**[method](#method)**

Set the method property to specify the API request method, such as POST, PATCH, or DELETE.

- 

**[type](#type)**

Set the type property to assign the object type that’s returned from the field describe result by using the getReferenceTo() method or from the sObject describe result by using the getSObjectType() method.

### criteria

Set the criteria property to group order or quote line items. For example, group order or quote line items based on a monthly billing frequency.

#### Signature

`public Map<String,ANY> criteria {get; set;}`

#### Property Value

Type: Map<String,ANY>

### fieldValues

Set the fieldValues property to assign values to the fields to update the sales transaction.

#### Signature

`public Map<String,ANY> fieldValues {get; set;}`

#### Property Value

Type: ListMap<String,ANY>

### groupAction

Set the groupAction property to group order or quote line items.

You can group order or quote line items based on location, work types, or departments, if groups are enabled for your org. Groups provide a visualization of the products to view large quotes.

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

Set the method property to specify the API request method, such as POST, PATCH, or DELETE.

#### Signature

`public String method {get; set;}`

#### Property Value

Type: String

### type

Set the type property to assign the object type that’s returned from the field describe result by using the getReferenceTo() method or from the sObject describe result by using the getSObjectType() method.

#### Signature

`public Schema.SObjectType type {get; set;}`

#### Property Value

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-recordresource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
