---
page_id: apex-class-revsignaling-transactionresponse
title: TransactionResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsignaling-transactionresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: apex-namespace-revsignaling
legacy_page_id: apex_class_RevSignaling_TransactionResponse.htm
fetched_at: 2026-11-25
---

# TransactionResponse Class

Represents the transaction response from the signaling Apex processor.

## Namespace

[RevSignaling](./apex-namespace-revsignaling.md)

- 

**[TransactionResponse Properties](#transactionresponse-properties)**

Learn more about the properties that are available with the TransactionResponse class.

## TransactionResponse Properties

Learn more about the properties that are available with the TransactionResponse class.

The `TransactionResponse` class includes these properties.

- 

**[message](#message)**

Get the message from the transaction response.

- 

**[status](#status)**

Get the status of the request from the transaction response.

### message

Get the message from the transaction response.

#### Signature

`public String message {get; set;}`

#### Property Value

Type: String

### status

Get the status of the request from the transaction response.

#### Signature

`public RevSignaling.TransactionStatus status {get; set;}`

#### Property Value

Type: [RevSignaling.TransactionStatus](./apex-enum-revsignaling-transactionstatus.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsignaling-transactionresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
