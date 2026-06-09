---
page_id: apex_enum_commercetax_TaxTransactionType.htm
title: TaxTransactionType Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_TaxTransactionType.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxTransactionType Enum

Shows whether the tax transaction is for a credit or debit
transaction.

## Usage

Used by the [CalculateTaxResponse](./apex_class_commercetax_CalculateTaxResponse.htm.md "Sets the values of the tax transaction following a response from the external tax engine. Extends the AbstractTransactionResponse class and is the top-level response class.") and [CalculateTaxRequest](./apex_class_commercetax_CalculateTaxRequest.htm.md "Represents a request to an external tax engine to calculate tax. Extends the TaxTransactionRequest class and is the top-level request class.") class
methods.

## Enum Values

The `commercetax.TaxTransactionType` enum includes
these values.

| Value | Description |
| --- | --- |
| `Credit` | Represents a credit transaction. |
| `Debit` | Represents a debit transaction. |
| `Void` | Specifies that the tax engine has voided the document that's mentioned in the `referenceDocumentCode` property value. |
