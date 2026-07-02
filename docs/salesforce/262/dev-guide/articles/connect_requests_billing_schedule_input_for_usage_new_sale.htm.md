---
page_id: connect_requests_billing_schedule_input_for_usage_new_sale.htm
title: New Sale Transaction With Usage Products
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_usage_new_sale.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# New Sale Transaction With Usage Products

Understand the required values and key considerations before you create a billing
schedule for a new sale transaction with usage-based products.

## Considerations

Keep these important considerations in mind when you provide the details for new sale
transactions with a usage-based product.

- The `BillingActionType__std` value for any new sale
  transaction must be `Add`.
- For new sale transactions with a usage-based product, the `ProductUsageModelType__std` and `BindingInstance__std` values are required.
- If you don't provide the `TaxTreatmentId__std` value,
  the `BillingTreatmentId__std` value, or the `LegalEntityId__std` value for the transaction, the default
  `TaxTreatmentId`, `BillingTreatmentId`, and `LegalEntityId` of
  your Salesforce org is considered. If your org doesn't have any default values, an error
  occurs.
- To understand the requirements for the various selling model types, see these resources.
  - [One-Time New Sale
    Transaction](./connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the OneTime selling model type.")
  - [Term-Defined New Sale
    Transaction](./connect_requests_billing_schedule_input_for_termed_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the TermDefined selling model type.")
  - [Evergreen New Sale
    Transaction](./connect_requests_billing_schedule_input_for_evergreen_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the Evergreen selling model type.")

JSON example
:   This sample is for a new sale transaction for a usage-based product with a `TermDefined` selling model.

    ```
    {
      "Transaction": [
        {
          "id": "termDefined",
          "SellingModelType__std": "TermDefined",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "onetimeUsage2",
          "StartDate__std": "2025-01-01",
          "EndDate__std": "2025-12-31",
          "PeriodBoundary__std": "DayOfPeriod",
          "BillingDayOfMonth__std": 1,
          "BillingTermUnit__std": "Month",
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 120,
          "AccountId__std": "001xx000003GgEJAA0",
          "BillingProfileId__std": "001LT00000dPVrlYAG",
          "BillingActionType__std": "Add",
          "CurrencyIsoCode__std": "USD",
          "BillingCity__std": "Hyderabad",
          "ShippingCity__std": "SFO",
          "ProductUsageModelType__std": "Anchor",
          "BindingInstance__std": "001xx000003GgChAAK",
          "ProductId__std": "01txx0000006i3DAAQ"
        }
      ]
    }
    ```

    This example shows the request payload to create a billing schedule for a new sale
    transaction for usage-based products with a `TermDefined` selling model.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"termDefined\",\"SellingModelType__std\":\"TermDefined\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"onetimeUsage2\",\"StartDate__std\":\"2025-01-01\",\"EndDate__std\":\"2025-12-31\",\"PeriodBoundary__std\":\"DayOfPeriod\",\"BillingDayOfMonth__std\":1,\"BillingTermUnit__std\":\"Month\",\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":120,\"AccountId__std\":\"001xx000003GgEJAA0\",\"BillingProfileId__std\":\"001LT00000dPVrlYAG\",\"BillingActionType__std\":\"Add\",\"CurrencyIsoCode__std\":\"USD\",\"BillingCity__std\":\"Hyderabad\",\"ShippingCity__std\":\"SFO\",\"ProductUsageModelType__std\":\"Anchor\",\"BindingInstance__std\":\"001xx000003GgChAAK\",\"ProductId__std\":\"01txx0000006i3DAAQ\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

Before using the Create Standalone Billing Schedules API for usage-based products, [Create a Usage Product Grant Binding
Policy record](https://help.salesforce.com/s/articleView?id=ind.um_create_a_usage_product_grant_binding_policy.htm&language=en_US "HTML (New Window)") with the grant binding type as `Target`.

When you're creating a billing schedule for a new sale transaction with a usage-based
product, make sure that you specify the mandatory values in the `transactionDetails` property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `ParentTransactionId__std` | The ID of the parent transaction record. For example, if the transaction is at a level similar to that of an Order Item record, the parent transaction will be at a level similar to that of an Order record. | If the transaction is a child Order or Quote record, the ReferenceEntityId field on the BillingScheduleobject is populated. For other sObject records or external records, the Reference field on the BillingSchedule object is populated. | Optional |
| `AccountId__std` | The ID of the Account record that's related to the transaction. | BillingAccountId field on the BillingScheduleGroup object | Required |
| `BillingProfileId__std` | The ID of the billing profile (Billing Account record) that's related to the transaction. See [Billing Profile](https://help.salesforce.com/s/articleView?id=ind.billing_billing_profiles_create.htm&language=en_US "HTML (New Window)") requirements. | BillingAccountId field on the BillingSchedule object | Optional |
| `BillingCity__std` | The city in the billing address of the transaction. | BillingCity field on the BillingScheduleGroup object | Any one of the billing address fields is required. |
| `ShippingCity__std` | The city in the shipping address of the transaction. | ShippingCity field on the BillingScheduleGroup object | Any one of the shipping address fields is required. |
| `SellingModelType__std` | The selling model type indicates whether the transaction is for a one-time product, a term-defined product, or an evergreen product. Specify `OneTime` as the SellingModelType for the transaction that's related to a product that's sold once. | BillingMethod on the BillingSchedule object is populated as OrderAmount. | Required |
| `TransactionId__std` | The ID of the transaction that you want to create a billing schedule for. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `ProductId__std` | The ID of the product that's related to the transaction that you want to create a billing schedule for. | Product2Id field on the BillingScheduleGroup object | Either the ProductName or the ProductId is required |
| `PeriodBoundary__std` | The period boundary determines the start and end date of the billing period. Valid values are:   - `AlignToCalendar` - `Anniversary` - `DayOfPeriod` - `LastDayOfPeriod` | PeriodBoundary field on the BillingScheduleGroup object | Required for products with the `TermDefined` or `Evergreen` selling model types. |
| `BillingDayOfMonth__std` | The day of the month on which a recurring billing process is scheduled to occur for the transaction. | BillDayOfMonth field on the BillingScheduleGroup object | Required for products with the `TermDefined` or `Evergreen` selling model types. |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Required for products with the `TermDefined` selling model type. |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `BillingTermUnit__std` | The unit of measurement of the billing term. Valid values are:  - `Month` - `Quarter` - `Semi-Annual` - `Year` | BillingTermUnit field on the BillingSchedule object | Required for products with the `TermDefined` or `Evergreen` selling model types. |
| `CurrencyIsoCode__std` | The currency code of the transaction amount if your Salesforce org has multi-currency enabled. | CurrencyIsoCode field on the BillingScheduleGroup object | Required for [Salesforce orgs with multiple currencies enabled](https://help.salesforce.com/s/articleView?id=sales.admin_enable_multicurrency.htm&language=en_US "HTML (New Window)"). |
| `BillingActionType__std` | The action that you want to perform for the transaction. Valid value is `Add`. | Category field on the BillingSchedule object is populated as Original. | Required |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
| `ProductUsageModelType__std` | The type of usage model for the transaction product or service. Valid values are:   - `Anchor`—Anchor is the main   subscription product or service. - `Pack`—Pack is the add-on product or   service that grants additional usage resources for consumption. | BillingMethod value field on the BillingSchedule object is populated as OrderAmount. | Required |
| `BindingInstance__std` | The ID of the Asset record or custom object record that's related to the transaction. | BindingInstanceId on the BillingScheduleGroup object | Required |
