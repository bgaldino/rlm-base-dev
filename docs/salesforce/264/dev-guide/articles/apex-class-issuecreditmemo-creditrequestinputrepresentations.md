---
page_id: apex-class-issuecreditmemo-creditrequestinputrepresentations
title: CreditRequestInputRepresentations Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditrequestinputrepresentations.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-issuecreditmemo
legacy_page_id: apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm
fetched_at: 2026-11-25
---

# CreditRequestInputRepresentations Class

Represents a credit request for an invoice. Contains invoice and dispute identifiers, total credit amount, category, and line-level credit details for issuing a credit memo.

## Namespace

[IssueCreditMemo](./apex-namespace-issuecreditmemo.md)

- 

**[CreditRequestInputRepresentations Constructors](#creditrequestinputrepresentations-constructors)**

- 

**[CreditRequestInputRepresentations Properties](#creditrequestinputrepresentations-properties)**

## CreditRequestInputRepresentations Constructors

The `CreditRequestInputRepresentations` class includes these constructors.

- 

**[CreditRequestInputRepresentations(invoiceId, creditAmount, description, disputeId, category, creditLineRequestInputRepresentations)](#creditrequestinputrepresentationsinvoiceid-creditamount-description-disputeid-category-creditlinerequestinputrepresentations)**

Creates a credit request with the given invoice, amount, description, dispute, category, and line-level credit details.

- 

**[CreditRequestInputRepresentations(invoiceId, creditAmount, description, creditLineRequestInputRepresentations)](#creditrequestinputrepresentationsinvoiceid-creditamount-description-creditlinerequestinputrepresentations)**

Creates a credit request with the given invoice, amount, description, and line-level credit details.

- 

**[CreditRequestInputRepresentations()](#creditrequestinputrepresentations)**

Creates an empty credit request.

### CreditRequestInputRepresentations(invoiceId, creditAmount, description, disputeId, category, creditLineRequestInputRepresentations)

Creates a credit request with the given invoice, amount, description, dispute, category, and line-level credit details.

#### Signature

`public CreditRequestInputRepresentations(String invoiceId, Double creditAmount, String description, String disputeId, String category, List<IssueCreditMemo.CreditLineRequestInputRepresentations> creditLineRequestInputRepresentations)`

#### Parameters

***invoiceId***

Type: String

ID of the invoice to credit.

***creditAmount***

Type: Double

Total credit amount to apply to the invoice.

***description***

Type: String

Optional description for the credit request.

***disputeId***

Type: String

ID of the billing dispute associated with this credit request.

***category***

Type: String

Category of the credit memo.

***creditLineRequestInputRepresentations***

Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex-class-issuecreditmemo-creditlinerequestinputrepresentations.md#creditlinerequestinputrepresentations-class)>

List of line-level credit requests for this invoice.

### CreditRequestInputRepresentations(invoiceId, creditAmount, description, creditLineRequestInputRepresentations)

Creates a credit request with the given invoice, amount, description, and line-level credit details.

#### Signature

`public CreditRequestInputRepresentations(String invoiceId, Double creditAmount, String description, List<IssueCreditMemo.CreditLineRequestInputRepresentations> creditLineRequestInputRepresentations)`

#### Parameters

***invoiceId***

Type: String

ID of the invoice to credit.

***creditAmount***

Type: Double

Total credit amount to apply to the invoice.

***description***

Type: String

Optional description for the credit request.

***creditLineRequestInputRepresentations***

Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex-class-issuecreditmemo-creditlinerequestinputrepresentations.md#creditlinerequestinputrepresentations-class)>

List of line-level credit requests for this invoice.

### CreditRequestInputRepresentations()

Creates an empty credit request.

#### Signature

`public CreditRequestInputRepresentations()`

## CreditRequestInputRepresentations Properties

The `CreditRequestInputRepresentations` class includes these properties.

- 

**[category](#category)**

The credit memo category.

- 

**[creditAmount](#creditamount)**

The total credit amount to apply to the invoice.

- 

**[creditLineRequestInputRepresentations](#creditlinerequestinputrepresentations)**

List of line-level credit requests for this invoice.

- 

**[description](#description)**

Optional description for the credit request.

- 

**[disputeId](#disputeid)**

The ID of the billing dispute associated with this credit request.

- 

**[invoiceId](#invoiceid)**

The ID of the invoice to credit.

### category

The credit memo category.

#### Signature

`public String category {get; set;}`

#### Property Value

Type: String

### creditAmount

The total credit amount to apply to the invoice.

#### Signature

`public Double creditAmount {get; set;}`

#### Property Value

Type: Double

### creditLineRequestInputRepresentations

List of line-level credit requests for this invoice.

#### Signature

`public List<IssueCreditMemo.CreditLineRequestInputRepresentations> creditLineRequestInputRepresentations {get; set;}`

#### Property Value

Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex-class-issuecreditmemo-creditlinerequestinputrepresentations.md#creditlinerequestinputrepresentations-class)>

### description

Optional description for the credit request.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### disputeId

The ID of the billing dispute associated with this credit request.

#### Signature

`public String disputeId {get; set;}`

#### Property Value

Type: String

### invoiceId

The ID of the invoice to credit.

#### Signature

`public String invoiceId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-issuecreditmemo-creditrequestinputrepresentations.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
