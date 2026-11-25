---
page_id: apex-class-rulesappln-rulesapplicationerrorresponse
title: RulesApplicationErrorResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationerrorresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-rulesappln
legacy_page_id: apex_class_RulesAppln_RulesApplicationErrorResponse.htm
fetched_at: 2026-11-25
---

# RulesApplicationErrorResponse Class

Contains properties to store error details that occurred during the rules application.

## Namespace

[RulesAppln](./apex-namespace-rulesappln.md)

- 

**[RulesApplicationErrorResponse Constructors](#rulesapplicationerrorresponse-constructors)**

Learn more about the constructors available with the RulesApplicationErrorResponse class.

- 

**[RulesApplicationErrorResponse Properties](#rulesapplicationerrorresponse-properties)**

Learn more about the properties available with the RulesApplicationErrorResponse class.

## RulesApplicationErrorResponse Constructors

Learn more about the constructors available with the RulesApplicationErrorResponse class.

The `RulesApplicationErrorResponse` class includes these constructors.

- 

**[RulesApplicationErrorResponse(errorCode, message)](#rulesapplicationerrorresponseerrorcode-message)**

Initializes the RulesApplicationErrorResponse class that stores error details that occurred during the rules application.

- 

**[RulesApplicationErrorResponse()](#rulesapplicationerrorresponse)**

Initializes an empty instance of the RulesApplicationErrorResponse class.

### RulesApplicationErrorResponse(errorCode, message)

Initializes the RulesApplicationErrorResponse class that stores error details that occurred during the rules application.

#### Signature

`public RulesApplicationErrorResponse(String errorCode, String message)`

#### Parameters

***errorCode***

Type: String

Error code that identifies the type of error that occurred during the rules application.

***message***

Type: String

Error message that describes the error that occurred during the rules application.

### RulesApplicationErrorResponse()

Initializes an empty instance of the RulesApplicationErrorResponse class.

#### Signature

`public RulesApplicationErrorResponse()`

## RulesApplicationErrorResponse Properties

Learn more about the properties available with the RulesApplicationErrorResponse class.

The `RulesApplicationErrorResponse` class includes these properties.

- 

**[errorCode](#errorcode)**

Get the error code that identifies the type of error that occurred during the rules application.

- 

**[message](#message)**

Get the error message that describes the error that occurred during the rules application.

### errorCode

Get the error code that identifies the type of error that occurred during the rules application.

#### Signature

`public String errorCode {get; set;}`

#### Property Value

Type: String

### message

Get the error message that describes the error that occurred during the rules application.

#### Signature

`public String message {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-rulesappln-rulesapplicationerrorresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
