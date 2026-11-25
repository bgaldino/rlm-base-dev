---
page_id: apex-class-placequote-recordresource
title: RecordResource Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-recordresource.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-placequote
legacy_page_id: apex_class_placequote_RecordResource.htm
fetched_at: 2026-11-25
---

# RecordResource Class

Contains constructors and properties to create a record object from the field values of a quote.

## Namespace

[PlaceQuote](./apex-namespace-placequote.md)

## Example

```
PlaceQuote.RecordResource quoteLineRelationship1 = new PlaceQuote.RecordResource(QuoteLineRelationship.getSobjectType(),'POST');
```

See [PlaceQuoteRLMApexProcessor](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_placequote_PlaceQuoteRLMApexProcessor.htm#apex_placequote_PlaceQuoteRLMApexProcessor_example_implementation) to refer to an example implementation.

- 

**[RecordResource Constructors](#recordresource-constructors)**

Learn more about the available constructors with the `RecordResource` class.

- 

**[RecordResource Properties](#recordresource-properties)**

Learn more about the available properties with the `RecordResource` class.

## RecordResource Constructors

Learn more about the available constructors with the `RecordResource` class.

The `RecordResource` class includes these constructors.

- 

**[RecordResource(type, method, id)](#recordresourcetype-method-id)**

Creates an instance of the `RecordResource` class to assign values to the fields of a quote item by using the sObject type, API method, and quote ID properties.

- 

**[RecordResource(type, method)](#recordresourcetype-method)**

Creates an instance of the `RecordResource` class to assign the values to the fields of a quote item by using the sObject type and API method properties.

### RecordResource(type, method, id)

Creates an instance of the `RecordResource` class to assign values to the fields of a quote item by using the sObject type, API method, and quote ID properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method, Id id)`

#### Parameters

***type***

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType() `method.

***method***

Type: String

Method for the API request, such as POST or PATCH.

***id***

Type: Id

ID of the quote.

### RecordResource(type, method)

Creates an instance of the `RecordResource` class to assign the values to the fields of a quote item by using the sObject type and API method properties.

#### Signature

`public RecordResource(Schema.SObjectType type, String method)`

#### Parameters

***type***

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

Object that’s returned from the field describe result using the `getReferenceTo()` method or from the sObject describe result using the `getSObjectType() `method.

***method***

Type: String

Method for the API request, such as POST or PATCH.

## RecordResource Properties

Learn more about the available properties with the `RecordResource` class.

The `RecordResource` class includes these properties.

- 

**[fieldValues](#fieldvalues)**

Set the `fieldValues` property to assign values to the fields to update the quote record.

- 

**[id](#id)**

Set the `id` property to assign the ID of the quote record.

- 

**[method](#method)**

Set the `method` property to specify the API request method, such as POST or PATCH.

- 

**[type](#type)**

Set the type property to assign the object type that’s returned from the field describe result by using the `getReferenceTo()` method or from the sObject describe result by using the `getSObjectType()` method.

### fieldValues

Set the `fieldValues` property to assign values to the fields to update the quote record.

#### Signature

`public Map<String,ANY> fieldValues {get; set;}`

#### Property Value

Type: List <Map<String,ANY>>

### id

Set the `id` property to assign the ID of the quote record.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### method

Set the `method` property to specify the API request method, such as POST or PATCH.

#### Signature

`public String method {get; set;}`

#### Property Value

Type: String

### type

Set the type property to assign the object type that’s returned from the field describe result by using the `getReferenceTo()` method or from the sObject describe result by using the `getSObjectType()` method.

#### Signature

`public Schema.SObjectType type {get; set;}`

#### Property Value

Type: [Schema.SObjectType](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_class_Schema_SObjectType.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-placequote-recordresource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
