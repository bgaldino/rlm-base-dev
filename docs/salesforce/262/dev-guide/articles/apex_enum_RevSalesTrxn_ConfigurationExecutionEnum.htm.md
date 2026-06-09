---
page_id: apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm
title: ConfigurationExecutionEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# ConfigurationExecutionEnum Enum

Specifies the configuration method for the place sales transaction request.

## Usage

Use these enum values for the `configurationExecutionEnum` property in the [PlaceSalesTransactionExecutor](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md "Contains methods to place a sales transaction with details of the graph request, pricing preferences, and configuration options.") class.

## Enum Values

The `RevSalesTrxn.ConfigurationExecutionEnum` enum has these
values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce the predefined configuration process during the sales transaction process. |
| `Skip` | Specifies to skip the configuration process during the quote creation process. The default value is `Skip`. |
| `System` | Specifies the system to determine whether the configuration process is required. |
