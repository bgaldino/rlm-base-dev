---
page_id: apex_class_runtime_industries_cpq_VisibilityRule.htm
title: VisibilityRule Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_VisibilityRule.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# VisibilityRule Class

Represents a visibility rule that is evaluated during product configuration. Visibility rules control the visibility of products, attributes, or other UI elements based on configuration conditions.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[VisibilityRule Constructor](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_constructors)**  
  Learn more about the constructor that's available with the VisibilityRule class.
- **[VisibilityRule Properties](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_properties)**  
  Contains properties to store visibility rule details from configuration rule evaluation.

## VisibilityRule Constructor

Learn more about the constructor that's available with the VisibilityRule
class.

The `VisibilityRule` class includes this
constructor.

- **[VisibilityRule(stiId, prcId, attributeId, attributePicklistValueId, target, scope, type, productIds, message)](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_ctor)**  
  Constructor to create a VisibilityRule instance with the specified visibility rule details.

### VisibilityRule(stiId, prcId, attributeId, attributePicklistValueId, target, scope, type, productIds, message)

Constructor to create a VisibilityRule instance with the specified visibility rule details.

#### Signature

`public VisibilityRule(String stiId, String prcId, String attributeId, String attributePicklistValueId, String target, String scope, String type, List<String> productIds, String message)`

#### Parameters

stiId
:   Type: String
:   The ID of the Sales Transaction Item (STI) associated with this visibility rule.

prcId
:   Type: String
:   The ID of the Product Relationship Configuration (PRC) associated with this visibility rule.

attributeId
:   Type: String
:   The ID of the attribute associated with this visibility rule.

attributePicklistValueId
:   Type: String
:   The ID of the attribute picklist value associated with this visibility rule.

target
:   Type: String
:   The target of the visibility rule (for example, product, attribute, or component).

scope
:   Type: String
:   The scope of the visibility rule.

type
:   Type: String
:   The type of visibility rule (for example, Show or Hide).

productIds
:   Type: List<String>
:   List of product IDs affected by this visibility rule.

message
:   Type: String
:   The message to display when the visibility rule is applied.

## VisibilityRule Properties

Contains properties to store visibility rule details from configuration rule evaluation.

The `VisibilityRule` class includes these
properties.

- **[attributeId](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_attributeId)**  
  Get the ID of the attribute.
- **[attributePicklistValueId](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_attributePicklistValueId)**  
  Get the ID of the attributepicklistvalue.
- **[message](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_message)**  
  Get the message value.
- **[prcId](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_prcId)**  
  Get the ID of the prc.
- **[productId](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_productId)**  
  Get the ID of the product.
- **[scope](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_scope)**  
  Get the scope value.
- **[stiId](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_stiId)**  
  Get the ID of the sti.
- **[target](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_target)**  
  Get the target value.
- **[type](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_runtime_industries_cpq_VisibilityRule_type)**  
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
