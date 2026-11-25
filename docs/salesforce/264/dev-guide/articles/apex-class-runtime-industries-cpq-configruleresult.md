---
page_id: apex-class-runtime-industries-cpq-configruleresult
title: ConfigRuleResult Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-configruleresult.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ConfigRuleResult.htm
fetched_at: 2026-11-25
---

# ConfigRuleResult Class

Contains the results of configuration rule evaluation, including message rules, product recommendation rules, and visibility rules that are applied during product configuration.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ConfigRuleResult Constructor](#configruleresult-constructor)**

Learn more about the constructor that’s available with the ConfigRuleResult class.

- 

**[ConfigRuleResult Properties](#configruleresult-properties)**

Contains properties to store configuration rule evaluation results.

## ConfigRuleResult Constructor

Learn more about the constructor that’s available with the ConfigRuleResult class.

The `ConfigRuleResult` class includes this constructor.

- 

**[ConfigRuleResult(transactionContextId, messageRules, productRecommendationRules, visibilityRules, errors)](#configruleresulttransactioncontextid-messagerules-productrecommendationrules-visibilityrules-errors)**

Constructor to create a ConfigRuleResult instance with configuration rule evaluation results.

### ConfigRuleResult(transactionContextId, messageRules, productRecommendationRules, visibilityRules, errors)

Constructor to create a ConfigRuleResult instance with configuration rule evaluation results.

#### Signature

`public ConfigRuleResult(String transactionContextId, List<runtime_industries_cpq.MessageRule> messageRules, List<runtime_industries_cpq.ProductRecommendationRule> productRecommendationRules, List<runtime_industries_cpq.VisibilityRule> visibilityRules, List<String> errors)`

#### Parameters

***transactionContextId***

Type: String

The ID of the transaction context for this configuration rule evaluation.

***messageRules***

Type: List<runtime_industries_cpq.MessageRule>

List of message rules that were evaluated during configuration.

***productRecommendationRules***

Type: List<runtime_industries_cpq.ProductRecommendationRule>

List of product recommendation rules that were evaluated during configuration.

***visibilityRules***

Type: List<runtime_industries_cpq.VisibilityRule>

List of visibility rules that were evaluated during configuration.

***errors***

Type: List<String>

List of error messages from the configuration rule evaluation, if any.

## ConfigRuleResult Properties

Contains properties to store configuration rule evaluation results.

The `ConfigRuleResult` class includes these properties.

- 

**[errors](#errors)**

Get the list of error messages.

- 

**[messageRules](#messagerules)**

Get the list of messagerule.

- 

**[productRecommendationRules](#productrecommendationrules)**

Get the list of productrecommendationrule.

- 

**[transactionContextId](#transactioncontextid)**

Get the ID of the transactioncontext.

- 

**[visibilityRules](#visibilityrules)**

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

Type: List<[runtime_industries_cpq.MessageRule](./apex-class-runtime-industries-cpq-messagerule.md#messagerule-class)>

### productRecommendationRules

Get the list of productrecommendationrule.

#### Signature

`public List<runtime_industries_cpq.ProductRecommendationRule> productRecommendationRules {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductRecommendationRule](./apex-class-runtime-industries-cpq-productrecommendationrule.md#productrecommendationrule-class)>

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

Type: List<[runtime_industries_cpq.VisibilityRule](./apex-class-runtime-industries-cpq-visibilityrule.md#visibilityrule-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-configruleresult.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
