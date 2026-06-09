---
page_id: apex_enum_commercetax_RequestType.htm
title: RequestType Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_commercetax_RequestType.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# RequestType Enum

Shows the type of tax request made to the tax
engine.

## Usage

Used by the [TaxEngineContext](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxEngineContext.htm "Wrapper class that stores details about the type of a tax calculation request.")
class method.

## Enum Values

The `commercetax.RequestType` enum includes these
values.

| Value | Description |
| --- | --- |
| `CalculateTax` | Represents a request to calculate tax on a list of taxable line items. |
