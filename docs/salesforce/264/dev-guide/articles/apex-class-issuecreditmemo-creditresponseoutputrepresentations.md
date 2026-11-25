---
page_id: apex-class-issuecreditmemo-creditresponseoutputrepresentations
title: CreditResponseOutputRepresentations Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditresponseoutputrepresentations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-issuecreditmemo
legacy_page_id: apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm
fetched_at: 2026-11-25
---

# CreditResponseOutputRepresentations Class

Represents the result of a credit memo operation. Indicates success or failure and any additional information or message.

## Namespace

[IssueCreditMemo](./apex-namespace-issuecreditmemo.md)

## Usage

## Example

- 

**[CreditResponseOutputRepresentations Constructors](#creditresponseoutputrepresentations-constructors)**

- 

**[CreditResponseOutputRepresentations Properties](#creditresponseoutputrepresentations-properties)**

## CreditResponseOutputRepresentations Constructors

The `CreditResponseOutputRepresentations` class includes these constructors.

- 

**[CreditResponseOutputRepresentations(success, additionalInformation)](#creditresponseoutputrepresentationssuccess-additionalinformation)**

Creates a response with the given success flag and additional information.

### CreditResponseOutputRepresentations(success, additionalInformation)

Creates a response with the given success flag and additional information.

#### Signature

`public CreditResponseOutputRepresentations(Boolean success, String additionalInformation)`

#### Parameters

***success***

Type: Boolean

Indicates whether the credit memo is issued successfully (`true`) or not (`false`).

***additionalInformation***

Type: String

Additional information or message, such as error details or confirmation.

## CreditResponseOutputRepresentations Properties

The `CreditResponseOutputRepresentations` class includes these properties.

- 

**[additionalInformation](#additionalinformation)**

Additional information or message, such as error details or confirmation.

- 

**[success](#success)**

Indicates whether the credit memo is issued successfully (true) or not (false).

### additionalInformation

Additional information or message, such as error details or confirmation.

#### Signature

`public String additionalInformation {get; set;}`

#### Property Value

Type: String

### success

Indicates whether the credit memo is issued successfully (true) or not (false).

#### Signature

`public Boolean success {get; set;}`

#### Property Value

Type: Boolean

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditresponseoutputrepresentations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
