---
page_id: apex_class_runtime_industries_cpq_ConfigRuleResult.htm
title: ConfigRuleResult Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ConfigRuleResult.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConfigRuleResult Class

Contains the results of configuration rule evaluation, including message rules, product recommendation rules, and visibility rules that are applied during product configuration.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ConfigRuleResult Constructor](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_constructors)**  

Learn more about the constructor that's available with the ConfigRuleResult     class.

- 
**[ConfigRuleResult Properties](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_properties)**  

Contains properties to store configuration rule evaluation results.

  

## ConfigRuleResult Constructor

  
  
  
Learn more about the constructor that's available with the ConfigRuleResult
    class.

    
      

The `ConfigRuleResult` class includes this
        constructor.

    

    
  

- 
**[ConfigRuleResult(transactionContextId, messageRules, productRecommendationRules, visibilityRules, errors)](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_ctor)**  

Constructor to create a ConfigRuleResult instance with configuration rule evaluation results.

### ConfigRuleResult(transactionContextId, messageRules, productRecommendationRules, visibilityRules, errors)

Constructor to create a ConfigRuleResult instance with configuration rule evaluation results.

#### Signature

`public ConfigRuleResult(String transactionContextId, List<runtime_industries_cpq.MessageRule> messageRules, List<runtime_industries_cpq.ProductRecommendationRule> productRecommendationRules, List<runtime_industries_cpq.VisibilityRule> visibilityRules, List<String> errors)`

#### Parameters

**transactionContextId**

: Type: String

: The ID of the transaction context for this configuration rule evaluation.

**messageRules**

: Type: List<runtime_industries_cpq.MessageRule>

: List of message rules that were evaluated during configuration.

**productRecommendationRules**

: Type: List<runtime_industries_cpq.ProductRecommendationRule>

: List of product recommendation rules that were evaluated during configuration.

**visibilityRules**

: Type: List<runtime_industries_cpq.VisibilityRule>

: List of visibility rules that were evaluated during configuration.

**errors**

: Type: List<String>

: List of error messages from the configuration rule evaluation, if any.

  

## ConfigRuleResult Properties

  
  
  
Contains properties to store configuration rule evaluation results.

    
      

The `ConfigRuleResult` class includes these
        properties.

    

    
  

- 
**[errors](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_errors)**  

Get the list of error messages.

- 
**[messageRules](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_messageRules)**  

Get the list of messagerule.

- 
**[productRecommendationRules](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_productRecommendationRules)**  

Get the list of productrecommendationrule.

- 
**[transactionContextId](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_transactionContextId)**  

Get the ID of the transactioncontext.

- 
**[visibilityRules](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md#apex_runtime_industries_cpq_ConfigRuleResult_visibilityRules)**  

Get the list of visibilityrule.

### errors

Get the list of error messages.

#### Signature

`public List<String> errors {get; set;}`

#### Property Value

Type: List<String>

### messageRules

Get the list of messagerule.

#### Signature

`public List<runtime_industries_cpq.MessageRule> messageRules {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.MessageRule](./apex_class_runtime_industries_cpq_MessageRule.htm.md#apex_class_runtime_industries_cpq_MessageRule)>

### productRecommendationRules

Get the list of productrecommendationrule.

#### Signature

`public List<runtime_industries_cpq.ProductRecommendationRule> productRecommendationRules {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductRecommendationRule](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md#apex_class_runtime_industries_cpq_ProductRecommendationRule)>

### transactionContextId

Get the ID of the transactioncontext.

#### Signature

`public String transactionContextId {get; set;}`

#### Property Value

Type: String

### visibilityRules

Get the list of visibilityrule.

#### Signature

`public List<runtime_industries_cpq.VisibilityRule> visibilityRules {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.VisibilityRule](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md#apex_class_runtime_industries_cpq_VisibilityRule)>
