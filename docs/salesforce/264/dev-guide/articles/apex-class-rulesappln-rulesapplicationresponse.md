---
page_id: apex-class-rulesappln-rulesapplicationresponse
title: RulesApplicationResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-rulesappln
legacy_page_id: apex_class_RulesAppln_RulesApplicationResponse.htm
fetched_at: 2026-11-25
---

# RulesApplicationResponse Class

Contains properties to store the response details for the rules application request.

## Namespace

[RulesAppln](./apex-namespace-rulesappln.md)

- 

**[RulesApplicationResponse Constructors](#rulesapplicationresponse-constructors)**

Learn more about the constructors available with the RulesApplicationResponse class.

- 

**[RulesApplicationResponse Properties](#rulesapplicationresponse-properties)**

Learn more about the properties available with the RulesApplicationResponse class.

## RulesApplicationResponse Constructors

Learn more about the constructors available with the RulesApplicationResponse class.

The `RulesApplicationResponse` class includes these constructors.

- 

**[RulesApplicationResponse(isSuccess, appliedRules, rulesApplicationSummary, errors)](#rulesapplicationresponseissuccess-appliedrules-rulesapplicationsummary-errors)**

Initializes the RulesApplicationResponse class that stores the response details for the rules application request.

- 

**[RulesApplicationResponse()](#rulesapplicationresponse)**

Initializes an empty instance of the RulesApplicationResponse class.

### RulesApplicationResponse(isSuccess, appliedRules, rulesApplicationSummary, errors)

Initializes the RulesApplicationResponse class that stores the response details for the rules application request.

#### Signature

`public RulesApplicationResponse(Boolean isSuccess, List<String> appliedRules, RulesAppln.RulesApplicationSummaryResponse rulesApplicationSummary, List<RulesAppln.RulesApplicationErrorResponse> errors)`

#### Parameters

***isSuccess***

Type: Boolean

Indicates whether the rules are applied (`true`) or not (`false`).

***appliedRules***

Type: List<String>

Comma-delimited list of applied rules.

***rulesApplicationSummary***

Type: [RulesAppln.RulesApplicationSummaryResponse](./apex-class-rulesappln-rulesapplicationsummaryresponse.md#rulesapplicationsummaryresponse-class)

Details of the rules application that includes these details.

- Payment and credit memo count for the account

- Payment and credit memo count that’s applied to invoices or invoice lines

- Details of rules

***errors***

Type: List<[RulesAppln.RulesApplicationErrorResponse](./apex-class-rulesappln-rulesapplicationerrorresponse.md#rulesapplicationerrorresponse-class)>

List of error responses that occurred during the rules application.

### RulesApplicationResponse()

Initializes an empty instance of the RulesApplicationResponse class.

#### Signature

`public RulesApplicationResponse()`

## RulesApplicationResponse Properties

Learn more about the properties available with the RulesApplicationResponse class.

The `RulesApplicationResponse` class includes these properties.

- 

**[appliedRules](#appliedrules)**

Get the comma-delimited list of rules that were applied.

- 

**[errors](#errors)**

Get the list of error responses that occurred during the rules application.

- 

**[isSuccess](#issuccess)**

Get the boolean value that indicates whether the rules were applied (true) or not (false).

- 

**[rulesApplicationSummary](#rulesapplicationsummary)**

Get the details of the rules application that includes payment and credit memo count for the account, payment and credit memo count that’s applied to invoices or invoice lines, and whether the exact amount rule is applied.

### appliedRules

Get the comma-delimited list of rules that were applied.

#### Signature

`public List<String> appliedRules {get; set;}`

#### Property Value

Type: List<String>

### errors

Get the list of error responses that occurred during the rules application.

#### Signature

`public List<RulesAppln.RulesApplicationErrorResponse> errors {get; set;}`

#### Property Value

Type: List<[RulesAppln.RulesApplicationErrorResponse](./apex-class-rulesappln-rulesapplicationerrorresponse.md#rulesapplicationerrorresponse-class)>

### isSuccess

Get the boolean value that indicates whether the rules were applied (true) or not (false).

#### Signature

`public Boolean isSuccess {get; set;}`

#### Property Value

Type: Boolean

### rulesApplicationSummary

Get the details of the rules application that includes payment and credit memo count for the account, payment and credit memo count that’s applied to invoices or invoice lines, and whether the exact amount rule is applied.

#### Signature

`public RulesAppln.RulesApplicationSummaryResponse rulesApplicationSummary {get; set;}`

#### Property Value

Type: [RulesAppln.RulesApplicationSummaryResponse](./apex-class-rulesappln-rulesapplicationsummaryresponse.md#rulesapplicationsummaryresponse-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
