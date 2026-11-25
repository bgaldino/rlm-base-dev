---
page_id: apex-class-runtime-industries-cpq-productrecommendationrule
title: ProductRecommendationRule Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productrecommendationrule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductRecommendationRule.htm
fetched_at: 2026-11-25
---

# ProductRecommendationRule Class

Represents a product recommendation rule that is evaluated during product configuration. Product recommendation rules suggest additional products to users based on configuration conditions.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductRecommendationRule Constructor](#productrecommendationrule-constructor)**

Learn more about the constructor that’s available with the ProductRecommendationRule class.

- 

**[ProductRecommendationRule Properties](#productrecommendationrule-properties)**

Contains properties to store product recommendation rule details from configuration rule evaluation.

## ProductRecommendationRule Constructor

Learn more about the constructor that’s available with the ProductRecommendationRule class.

The `ProductRecommendationRule` class includes this constructor.

- 

**[ProductRecommendationRule(referenceId, productIds, message, recordType, target, scope)](#productrecommendationrulereferenceid-productids-message-recordtype-target-scope)**

Constructor to create a ProductRecommendationRule instance with the specified recommendation details.

### ProductRecommendationRule(referenceId, productIds, message, recordType, target, scope)

Constructor to create a ProductRecommendationRule instance with the specified recommendation details.

#### Signature

`public ProductRecommendationRule(String referenceId, List<String> productIds, String message, String recordType, String target, String scope)`

#### Parameters

***referenceId***

Type: String

The reference ID of the product recommendation rule.

***productIds***

Type: List<String>

List of product IDs that are recommended.

***message***

Type: String

The message to display with the product recommendation.

***recordType***

Type: String

The record type associated with the recommendation.

***target***

Type: String

The target of the recommendation rule.

***scope***

Type: String

The scope of the recommendation rule.

## ProductRecommendationRule Properties

Contains properties to store product recommendation rule details from configuration rule evaluation.

The `ProductRecommendationRule` class includes these properties.

- 

**[message](#message)**

Get the message value.

- 

**[productIds](#productids)**

Get the list of productid.

- 

**[recordType](#recordtype)**

Get the recordtype value.

- 

**[referenceId](#referenceid)**

Get the ID of the reference.

- 

**[scope](#scope)**

Get the scope value.

- 

**[target](#target)**

Get the target value.

### message

Get the message value.

#### Signature

`public String message {get; set;}`

#### Property Value

Type: String

### productIds

Get the list of productid.

#### Signature

`public List<String> productIds {get; set;}`

#### Property Value

Type: List<String>

### recordType

Get the recordtype value.

#### Signature

`public String recordType {get; set;}`

#### Property Value

Type: String

### referenceId

Get the ID of the reference.

#### Signature

`public String referenceId {get; set;}`

#### Property Value

Type: String

### scope

Get the scope value.

#### Signature

`public String scope {get; set;}`

#### Property Value

Type: String

### target

Get the target value.

#### Signature

`public String target {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productrecommendationrule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
