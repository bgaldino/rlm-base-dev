---
page_id: apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm
title: CreditResponseOutputRepresentations Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_IssueCreditMemo.htm
fetched_at: 2026-06-09
---

# CreditResponseOutputRepresentations Class

Represents the result of a credit memo operation. Indicates success or failure and any additional information or message.

## Namespace

[IssueCreditMemo](./apex_namespace_IssueCreditMemo.htm.md "Issue credit memos from disputed invoices. Use this namespace to create and apply credit memos against invoices or invoice lines based on dispute adjustments.")

## Usage

## Example

- **[CreditResponseOutputRepresentations Constructors](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_constructors)**
- **[CreditResponseOutputRepresentations Properties](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_properties)**

## CreditResponseOutputRepresentations Constructors

The `CreditResponseOutputRepresentations` class includes
these constructors.

- **[CreditResponseOutputRepresentations(success, additionalInformation)](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_ctor)**  
  Creates a response with the given success flag and additional information.

### CreditResponseOutputRepresentations(success, additionalInformation)

Creates a response with the given success flag and additional information.

#### Signature

`public CreditResponseOutputRepresentations(Boolean success, String additionalInformation)`

#### Parameters

success
:   Type: Boolean
:   Indicates whether the credit memo is issued successfully (`true`) or not (`false`).

additionalInformation
:   Type: String
:   Additional information or message, such as error details or confirmation.

## CreditResponseOutputRepresentations Properties

The `CreditResponseOutputRepresentations` class includes
these properties.

- **[additionalInformation](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_additionalInformation)**  
  Additional information or message, such as error details or confirmation.
- **[success](./apex_class_IssueCreditMemo_CreditResponseOutputRepresentations.htm.md#apex_IssueCreditMemo_CreditResponseOutputRepresentations_success)**  
  Indicates whether the credit memo is issued successfully (true) or not (false).

### additionalInformation

Additional information or message, such as error details or confirmation.

#### Signature

`public String additionalInformation {get; set;}`

#### Property Value

Type: String

### success

Indicates whether the credit memo is issued successfully (true) or not
(false).

#### Signature

`public Boolean success {get; set;}`

#### Property Value

Type: Boolean
