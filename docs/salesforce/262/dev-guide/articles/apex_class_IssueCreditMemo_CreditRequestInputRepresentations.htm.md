---
page_id: apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm
title: CreditRequestInputRepresentations Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_IssueCreditMemo.htm
fetched_at: 2026-06-09
---

# CreditRequestInputRepresentations Class

Represents a credit request for an invoice. Contains invoice and dispute identifiers, total credit amount, category, and line-level credit details for issuing a credit memo.

## Namespace

[IssueCreditMemo](./apex_namespace_IssueCreditMemo.htm.md "Issue credit memos from disputed invoices. Use this namespace to create and apply credit memos against invoices or invoice lines based on dispute adjustments.")

- **[CreditRequestInputRepresentations Constructors](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_constructors)**
- **[CreditRequestInputRepresentations Properties](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_properties)**

## CreditRequestInputRepresentations Constructors

The `CreditRequestInputRepresentations` class includes
these constructors.

- **[CreditRequestInputRepresentations(invoiceId, creditAmount, description, disputeId, category, creditLineRequestInputRepresentations)](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_ctor)**  
  Creates a credit request with the given invoice, amount, description, dispute, category, and line-level credit details.
- **[CreditRequestInputRepresentations(invoiceId, creditAmount, description, creditLineRequestInputRepresentations)](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_ctor_2)**  
  Creates a credit request with the given invoice, amount, description, and line-level credit details.
- **[CreditRequestInputRepresentations()](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_ctor_3)**  
  Creates an empty credit request.

### CreditRequestInputRepresentations(invoiceId, creditAmount, description, disputeId, category, creditLineRequestInputRepresentations)

Creates a credit request with the given invoice, amount, description, dispute, category, and line-level credit details.

#### Signature

`public CreditRequestInputRepresentations(String invoiceId, Double creditAmount, String description, String disputeId, String category, List<IssueCreditMemo.CreditLineRequestInputRepresentations> creditLineRequestInputRepresentations)`

#### Parameters

invoiceId
:   Type: String
:   ID of the invoice to credit.

creditAmount
:   Type: Double
:   Total credit amount to apply to the invoice.

description
:   Type: String
:   Optional description for the credit request.

disputeId
:   Type: String
:   ID of the billing dispute associated with this credit request.

category
:   Type: String
:   Category of the credit memo.

creditLineRequestInputRepresentations
:   Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations "Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.")>
:   List of line-level credit requests for this invoice.

### CreditRequestInputRepresentations(invoiceId, creditAmount, description, creditLineRequestInputRepresentations)

Creates a credit request with the given invoice, amount, description, and line-level credit details.

#### Signature

`public CreditRequestInputRepresentations(String invoiceId, Double creditAmount, String description, List<IssueCreditMemo.CreditLineRequestInputRepresentations> creditLineRequestInputRepresentations)`

#### Parameters

invoiceId
:   Type: String
:   ID of the invoice to credit.

creditAmount
:   Type: Double
:   Total credit amount to apply to the invoice.

description
:   Type: String
:   Optional description for the credit request.

creditLineRequestInputRepresentations
:   Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations "Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.")>
:   List of line-level credit requests for this invoice.

### CreditRequestInputRepresentations()

Creates an empty credit request.

#### Signature

`public CreditRequestInputRepresentations()`

## CreditRequestInputRepresentations Properties

The `CreditRequestInputRepresentations` class includes
these properties.

- **[category](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_category)**  
  The credit memo category.
- **[creditAmount](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_creditAmount)**  
  The total credit amount to apply to the invoice.
- **[creditLineRequestInputRepresentations](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_creditLineRequestInputRepresentations)**  
  List of line-level credit requests for this invoice.
- **[description](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_description)**  
  Optional description for the credit request.
- **[disputeId](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_disputeId)**  
  The ID of the billing dispute associated with this credit request.
- **[invoiceId](./apex_class_IssueCreditMemo_CreditRequestInputRepresentations.htm.md#apex_IssueCreditMemo_CreditRequestInputRepresentations_invoiceId)**  
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

Type: List<[IssueCreditMemo.CreditLineRequestInputRepresentations](./apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations.htm.md#apex_class_IssueCreditMemo_CreditLineRequestInputRepresentations "Represents a single line-level credit request. Specifies the invoice line to credit, the amount to apply, and an optional description.")>

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
