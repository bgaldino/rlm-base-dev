---
page_id: apex_class_runtime_industries_cpq_ProductRecommendationRule.htm
title: ProductRecommendationRule Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductRecommendationRule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductRecommendationRule Class

Represents a product recommendation rule that is evaluated during product configuration. Product recommendation rules suggest additional products to users based on configuration conditions.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductRecommendationRule Constructor](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_constructors)**  
  Learn more about the constructor that's available with the ProductRecommendationRule class.
- **[ProductRecommendationRule Properties](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_properties)**  
  Contains properties to store product recommendation rule details from configuration rule evaluation.

## ProductRecommendationRule Constructor

Learn more about the constructor that's available with the ProductRecommendationRule
class.

The `ProductRecommendationRule` class includes this
constructor.

- **[ProductRecommendationRule(referenceId, productIds, message, recordType, target, scope)](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_ctor)**  
  Constructor to create a ProductRecommendationRule instance with the specified recommendation details.

### ProductRecommendationRule(referenceId, productIds, message, recordType, target, scope)

Constructor to create a ProductRecommendationRule instance with the specified recommendation details.

#### Signature

`public ProductRecommendationRule(String referenceId, List<String> productIds, String message, String recordType, String target, String scope)`

#### Parameters

referenceId
:   Type: String
:   The reference ID of the product recommendation rule.

productIds
:   Type: List<String>
:   List of product IDs that are recommended.

message
:   Type: String
:   The message to display with the product recommendation.

recordType
:   Type: String
:   The record type associated with the recommendation.

target
:   Type: String
:   The target of the recommendation rule.

scope
:   Type: String
:   The scope of the recommendation rule.

## ProductRecommendationRule Properties

Contains properties to store product recommendation rule details from configuration rule evaluation.

The `ProductRecommendationRule` class includes these
properties.

- **[message](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_message)**  
  Get the message value.
- **[productIds](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_productIds)**  
  Get the list of productid.
- **[recordType](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_recordType)**  
  Get the recordtype value.
- **[referenceId](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_referenceId)**  
  Get the ID of the reference.
- **[scope](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_scope)**  
  Get the scope value.
- **[target](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_runtime_industries_cpq_ProductRecommendationRule_target)**  
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
