---
page_id: apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm
title: ConfigurationExecutionEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_ConfigurationExecutionEnum.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConfigurationExecutionEnum Enum

Specifies the configuration method for the place sales transaction request.

## Usage

      

Use these enum values for the `configurationExecutionEnum` property in the [PlaceSalesTransactionExecutor](./apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor.htm.md#apex_class_RevSalesTrxn_PlaceSalesTransactionExecutor) class.

## Enum Values

The `RevSalesTrxn.ConfigurationExecutionEnum` enum has these
        values.

| Value | Description |
| --- | --- |
| `Force` | Specifies to enforce the predefined configuration process during the sales transaction process. |
| `Skip` | Specifies to skip the configuration process during the quote creation process. The default value is `Skip`. |
| `System` | Specifies the system to determine whether the configuration process is required. |
