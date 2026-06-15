---
page_id: apex_enum_commercetax_TaxTransactionStatus.htm
title: TaxTransactionStatus Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_TaxTransactionStatus.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxTransactionStatus Enum

Shows whether the tax transaction has been committed or
uncommitted.

## Usage

Used by the [CalculateTaxResponse](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_class_commercetax_CalculateTaxResponse "Sets the values of the tax transaction following a response from the external tax engine. Extends the AbstractTransactionResponse class and is the top-level response class.") class method.

## Enum Values

The `commercetax.TaxTransactionStatus` enum includes
these values.

| Value | Description |
| --- | --- |
| `Committed` | Tax has been calculated and committed. |
| `Uncommitted` | Tax has been calculated but hasn't been committed. |
