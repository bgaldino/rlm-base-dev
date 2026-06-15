---
page_id: apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm
title: CreditLineRequestInputRepresentations Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_IssueCreditMemo.htm
fetched_at: 2026-06-09
---

# CreditLineRequestInputRepresentations Class

Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.

## Namespace

[IssueCreditMemo](./apex_namespace_IssueCreditMemo.htm.md "Issue credit memos from disputed invoices. Use this namespace to create and apply credit memos against invoices or invoice lines based on dispute adjustments.")

- **[CreditLineRequestInputRepresentations Constructors](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_constructors)**
- **[CreditLineRequestInputRepresentations Properties](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_properties)**

## CreditLineRequestInputRepresentations Constructors

The `CreditLineRequestInputRepresentations` class includes
these constructors.

- **[CreditLineRequestInputRepresentations(invoiceLineId, creditLineAmount, description)](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_ctor)**  
  Creates a credit line request for the specified invoice line, amount, and description.
- **[CreditLineRequestInputRepresentations()](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_ctor_2)**  
  Creates an empty credit line request.

### CreditLineRequestInputRepresentations(invoiceLineId, creditLineAmount, description)

Creates a credit line request for the specified invoice line, amount, and description.

#### Signature

`public CreditLineRequestInputRepresentations(String invoiceLineId, Double creditLineAmount, String description)`

#### Parameters

invoiceLineId
:   Type: String
:   The ID of the invoice line to which the credit applies.

creditLineAmount
:   Type: Double
:   The monetary amount to credit for this invoice line.

description
:   Type: String
:   Optional description or reason for the credit line.

### CreditLineRequestInputRepresentations()

Creates an empty credit line request.

#### Signature

`public CreditLineRequestInputRepresentations()`

## CreditLineRequestInputRepresentations Properties

The `CreditLineRequestInputRepresentations` class includes
these properties.

- **[creditLineAmount](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_creditLineAmount)**  
  The monetary amount to credit for this invoice line.
- **[description](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_description)**  
  Optional description or reason for the credit line.
- **[invoiceLineId](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditLineRequestInputRepresentations_invoiceLineId)**  
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
