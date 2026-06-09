---
page_id: apex_enum_commercetax_CalculateTaxType.htm
title: CalculateTaxType Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_CalculateTaxType.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# CalculateTaxType Enum

Shows whether a tax calculation request is for estimated or actual
tax.

## Usage

Used by the [CalculateTaxRequest](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CalculateTaxRequest.htm "Represents a request to an external tax engine to calculate tax. Extends the TaxTransactionRequest class and is the top-level request class.") and [CalculateTaxResponse](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CalculateTaxResponse.htm "Sets the values of the tax transaction following a response from the external tax engine. Extends the AbstractTransactionResponse class and is the top-level response class.") class methods.

## Enum Values

The `commercetax.CalculateTaxType` enum includes these
values.

| Value | Description |
| --- | --- |
| `Actual` | Specifies that the tax calculation service should calculate the finalized (actual) tax for the requested line items. |
| `Estimated` | Specifies that the tax calculation service should estimate the tax for the requested line items. |
