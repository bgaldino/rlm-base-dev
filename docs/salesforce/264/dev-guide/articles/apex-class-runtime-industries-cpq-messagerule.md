---
page_id: apex-class-runtime-industries-cpq-messagerule
title: MessageRule Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-messagerule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_MessageRule.htm
fetched_at: 2026-11-25
---

# MessageRule Class

Represents a message rule that is evaluated during product configuration. Message rules display informational, warning, or error messages to users based on configuration conditions.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[MessageRule Constructor](#messagerule-constructor)**

Learn more about the constructor that’s available with the MessageRule class.

- 

**[MessageRule Properties](#messagerule-properties)**

Contains properties to store message rule details from configuration rule evaluation.

## MessageRule Constructor

Learn more about the constructor that’s available with the MessageRule class.

The `MessageRule` class includes this constructor.

- 

**[MessageRule(stiId, severity, messages)](#messagerulestiid-severity-messages)**

Constructor to create a MessageRule instance with the specified STI ID, severity, and messages.

### MessageRule(stiId, severity, messages)

Constructor to create a MessageRule instance with the specified STI ID, severity, and messages.

#### Signature

`public MessageRule(String stiId, String severity, List<String> messages)`

#### Parameters

***stiId***

Type: String

The ID of the Sales Transaction Item (STI) associated with this message rule.

***severity***

Type: String

The severity level of the message (for example, Error, Warning, or Info).

***messages***

Type: List<String>

List of message strings to display to the user.

## MessageRule Properties

Contains properties to store message rule details from configuration rule evaluation.

The `MessageRule` class includes these properties.

- 

**[messages](#messages)**

Get the list of messages.

- 

**[severity](#severity)**

Get the severity value.

- 

**[stiId](#stiid)**

Get the ID of the sti.

### messages

Get the list of messages.

#### Signature

`public List<String> messages {get; set;}`

#### Property Value

Type: List<String>

### severity

Get the severity value.

#### Signature

`public String severity {get; set;}`

#### Property Value

Type: String

### stiId

Get the ID of the sti.

#### Signature

`public String stiId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-messagerule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
