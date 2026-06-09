---
page_id: apex_enum_commercetax_ResultCode.htm
title: ResultCode Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_ResultCode.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# ResultCode Enum

Code that represents the results of a tax request made to the tax
engine.

## Usage

Used by the [ErrorResponse](./apex_class_commercetax_ErrorResponse.htm.md "Use to respond with an error after receiving errors from the PaymentGatewayAdapter methods of the CommercePayments namespace, such as request-forbidden responses, custom validation errors, or expired API tokens.")
class method.

## Enum Values

The `commercetax.ResultCode` enum includes these
values.

| Value | Description |
| --- | --- |
| `TaxEngineError` | Represents an error that occurred during the tax request process. |
| `ReferenceDocumentCodeMissing` | Specifies if the document mentioned as a `referenceDocumentCode` value isn't available in the tax engine. |
