---
page_id: apex-class-runtime-industries-cpq-visibilityrule
title: VisibilityRule Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-visibilityrule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_VisibilityRule.htm
fetched_at: 2026-11-25
---

# VisibilityRule Class

Represents a visibility rule that is evaluated during product configuration. Visibility rules control the visibility of products, attributes, or other UI elements based on configuration conditions.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[VisibilityRule Constructor](#visibilityrule-constructor)**

Learn more about the constructor that’s available with the VisibilityRule class.

- 

**[VisibilityRule Properties](#visibilityrule-properties)**

Contains properties to store visibility rule details from configuration rule evaluation.

## VisibilityRule Constructor

Learn more about the constructor that’s available with the VisibilityRule class.

The `VisibilityRule` class includes this constructor.

- 

**[VisibilityRule(stiId, prcId, attributeId, attributePicklistValueId, target, scope, type, productIds, message)](#visibilityrulestiid-prcid-attributeid-attributepicklistvalueid-target-scope-type-productids-message)**

Constructor to create a VisibilityRule instance with the specified visibility rule details.

### VisibilityRule(stiId, prcId, attributeId, attributePicklistValueId, target, scope, type, productIds, message)

Constructor to create a VisibilityRule instance with the specified visibility rule details.

#### Signature

`public VisibilityRule(String stiId, String prcId, String attributeId, String attributePicklistValueId, String target, String scope, String type, List<String> productIds, String message)`

#### Parameters

***stiId***

Type: String

The ID of the Sales Transaction Item (STI) associated with this visibility rule.

***prcId***

Type: String

The ID of the Product Relationship Configuration (PRC) associated with this visibility rule.

***attributeId***

Type: String

The ID of the attribute associated with this visibility rule.

***attributePicklistValueId***

Type: String

The ID of the attribute picklist value associated with this visibility rule.

***target***

Type: String

The target of the visibility rule (for example, product, attribute, or component).

***scope***

Type: String

The scope of the visibility rule.

***type***

Type: String

The type of visibility rule (for example, Show or Hide).

***productIds***

Type: List<String>

List of product IDs affected by this visibility rule.

***message***

Type: String

The message to display when the visibility rule is applied.

## VisibilityRule Properties

Contains properties to store visibility rule details from configuration rule evaluation.

The `VisibilityRule` class includes these properties.

- 

**[attributeId](#attributeid)**

Get the ID of the attribute.

- 

**[attributePicklistValueId](#attributepicklistvalueid)**

Get the ID of the attributepicklistvalue.

- 

**[message](#message)**

Get the message value.

- 

**[prcId](#prcid)**

Get the ID of the prc.

- 

**[productId](#productid)**

Get the ID of the product.

- 

**[scope](#scope)**

Get the scope value.

- 

**[stiId](#stiid)**

Get the ID of the sti.

- 

**[target](#target)**

Get the target value.

- 

**[type](#type)**

Get the type value.

### attributeId

Get the ID of the attribute.

#### Signature

`public String attributeId {get; set;}`

#### Property Value

Type: String

### attributePicklistValueId

Get the ID of the attributepicklistvalue.

#### Signature

`public String attributePicklistValueId {get; set;}`

#### Property Value

Type: String

### message

Get the message value.

#### Signature

`public String message {get; set;}`

#### Property Value

Type: String

### prcId

Get the ID of the prc.

#### Signature

`public String prcId {get; set;}`

#### Property Value

Type: String

### productId

Get the ID of the product.

#### Signature

`public List<String> productId {get; set;}`

#### Property Value

Type: List<String>

### scope

Get the scope value.

#### Signature

`public String scope {get; set;}`

#### Property Value

Type: String

### stiId

Get the ID of the sti.

#### Signature

`public String stiId {get; set;}`

#### Property Value

Type: String

### target

Get the target value.

#### Signature

`public String target {get; set;}`

#### Property Value

Type: String

### type

Get the type value.

#### Signature

`public String type {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-visibilityrule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
