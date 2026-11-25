---
page_id: apex-class-issuecreditmemo-creditlinerequestinputrepresentations
title: CreditLineRequestInputRepresentations Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditlinerequestinputrepresentations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-issuecreditmemo
legacy_page_id: apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm
fetched_at: 2026-11-25
---

# CreditLineRequestInputRepresentations Class

Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.

## Namespace

[IssueCreditMemo](./apex-namespace-issuecreditmemo.md)

- 

**[CreditLineRequestInputRepresentations Constructors](#creditlinerequestinputrepresentations-constructors)**

- 

**[CreditLineRequestInputRepresentations Properties](#creditlinerequestinputrepresentations-properties)**

## CreditLineRequestInputRepresentations Constructors

The `CreditLineRequestInputRepresentations` class includes these constructors.

- 

**[CreditLineRequestInputRepresentations(invoiceLineId, creditLineAmount, description)](#creditlinerequestinputrepresentationsinvoicelineid-creditlineamount-description)**

Creates a credit line request for the specified invoice line, amount, and description.

- 

**[CreditLineRequestInputRepresentations()](#creditlinerequestinputrepresentations)**

Creates an empty credit line request.

### CreditLineRequestInputRepresentations(invoiceLineId, creditLineAmount, description)

Creates a credit line request for the specified invoice line, amount, and description.

#### Signature

`public CreditLineRequestInputRepresentations(String invoiceLineId, Double creditLineAmount, String description)`

#### Parameters

***invoiceLineId***

Type: String

The ID of the invoice line to which the credit applies.

***creditLineAmount***

Type: Double

The monetary amount to credit for this invoice line.

***description***

Type: String

Optional description or reason for the credit line.

### CreditLineRequestInputRepresentations()

Creates an empty credit line request.

#### Signature

`public CreditLineRequestInputRepresentations()`

## CreditLineRequestInputRepresentations Properties

The `CreditLineRequestInputRepresentations` class includes these properties.

- 

**[creditLineAmount](#creditlineamount)**

The monetary amount to credit for this invoice line.

- 

**[description](#description)**

Optional description or reason for the credit line.

- 

**[invoiceLineId](#invoicelineid)**

The ID of the invoice line to which the credit applies.

### creditLineAmount

The monetary amount to credit for this invoice line.

#### Signature

`public Double creditLineAmount {get; set;}`

#### Property Value

Type: Double

### description

Optional description or reason for the credit line.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### invoiceLineId

The ID of the invoice line to which the credit applies.

#### Signature

`public String invoiceLineId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditlinerequestinputrepresentations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
