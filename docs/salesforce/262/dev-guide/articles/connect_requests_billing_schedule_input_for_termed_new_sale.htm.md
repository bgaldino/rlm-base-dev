---
page_id: connect_requests_billing_schedule_input_for_termed_new_sale.htm
title: Term-Defined New Sale Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_termed_new_sale.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# Term-Defined New Sale Transaction

Understand the required values and key considerations before you create a billing
schedule for a new sale transaction with the TermDefined selling model type.

## Considerations

Keep these important considerations in mind when you provide the details for new sale
transactions with the TermDefined selling model type.

- The `BillingActionType__std` value for any new sale
  transaction must be `Add`.
- When a new sale transaction is for the TermDefined selling model type, the
  SellingModelType value must be `TermDefined`.
- When a new sale transaction is for the TermDefined selling model type, the `BillingTermUnit__std` and `PeriodBoundary__std` values are required.
- If you don't provide the `TaxTreatmentId__std` value,
  the `BillingTreatmentId__std` value, or the `LegalEntityId__std` value for the transaction, the default
  `TaxTreatmentId`, `BillingTreatmentId`, and `LegalEntityId` of
  your Salesforce org is considered. If your org doesn't have any default values, an error
  occurs.
- If your transaction is for an sObject record, only specify the record ID as the id value
  in the transactionDetails property value. All the other transaction details are
  automatically fetched from the sObject record if those details are mapped in the context
  definition.

JSON example
:   This example includes the transaction data for a new sale transaction with the
    TermDefined selling model type.

    ```
    {
      "Transaction": [
        {
          "id": "ter1",
          "SellingModelType__std": "TermDefined",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "ter1",
          "ProductName__std": "TermedQuarterlyProduct",
          "StartDate__std": "2025-01-01",
          "EndDate__std": "2025-12-31",
          "PeriodBoundary__std": "DayOfPeriod",
          "BillingDayOfMonth__std": 1,
          "UnitPrice__std": 10,
          "Quantity__std": 5,
          "TotalPrice__std": 120,
          "TaxTreatmentId__std": "1ttLT000000EV7DYAW",
          "BillingTreatmentId__std": "1BTLT00000008yT4AQ",
          "AccountId__std": "001LT00000dPVrlYAG",
          "BillingProfileId__std": "001LT00000dPVrlYAG",
          "BillingCity__std": "HYD",
          "ShippingCity__std": "VSKP",
          "BillingTermUnit__std": "Month",
          "BillingActionType__std": "Add",
          "CurrencyIsoCode__std": "USD"
        }
      ]
    }
    ```

    This example shows the request payload to create a billing schedule for a new sale
    transaction with the TermDefined selling model type.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"ter1\",\"SellingModelType__std\":\"TermDefined\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"ter1\",\"ProductName__std\":\"TermedQuarterlyProduct\",\"StartDate__std\":\"2025-01-01\",\"EndDate__std\":\"2025-12-31\",\"PeriodBoundary__std\":\"DayOfPeriod\",\"BillingDayOfMonth__std\":1,\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":120,\"TaxTreatmentId__std\":\"1ttLT000000EV7DYAW\",\"BillingTreatmentId__std\":\"1BTLT00000008yT4AQ\",\"AccountId__std\":\"001LT00000dPVrlYAG\",\"BillingProfileId__std\":\"001LT00000dPVrlYAG\",\"BillingCity__std\":\"HYD\",\"ShippingCity__std\":\"VSKP\",\"BillingTermUnit__std\":\"Month\",\"BillingActionType__std\":\"Add\",\"CurrencyIsoCode__std\":\"USD\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you're creating a billing schedule for a new sale transaction with the TermDefined
selling model type, make sure that you specify the mandatory values in the `transactionDetails` property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `ParentTransactionId__std` | The ID of the parent transaction record. For example, if the transaction is at a level similar to that of an Order Item record, the parent transaction will be at a level similar to that of an Order record. | If the transaction is a child Order or Quote record, the ReferenceEntityId field on the BillingScheduleobject is populated. For other sObject records or external records, the Reference field on the BillingSchedule object is populated. | Required |
| `AccountId__std` | The ID of the Account record that's related to the transaction. | BillingAccountId field on the BillingScheduleGroup object | Required |
| `BillingProfileId__std` | The ID of the billing profile (Billing Account record) that's related to the transaction. See [Billing Profile](https://help.salesforce.com/s/articleView?id=ind.billing_billing_profiles_create.htm&language=en_US "HTML (New Window)") requirements. | BillingAccountId field on the BillingSchedule object | Optional |
| `BillingCity__std` | The city in the billing address of the transaction. | BillingCity field on the BillingScheduleGroup object | Any one of the billing address fields is required. |
| `ShippingCity__std` | The city in the shipping address of the transaction. | ShippingCity field on the BillingScheduleGroup object | Any one of the shipping address fields is required. |
| `SellingModelType__std` | The selling model type indicates whether the transaction is for a one-time product, a term-defined product, or an evergreen product. Specify `TermDefined` as the SellingModelType for the transaction that's related to a product that's sold for a specific term. | BillingMethod on the BillingSchedule object is populated as OrderAmount. | Required |
| `TransactionId__std` | The ID of the transaction that you want to create a billing schedule for. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `ProductName__std` | The name of the product that's related to the transaction that you want to create a billing schedule for. | ProductName field on the BillingScheduleGroup object | Either the ProductName or the ProductId is required |
| `PeriodBoundary__std` | The period boundary determines the start and end date of the billing period. Valid values are:   - `AlignToCalendar` - `Anniversary` - `DayOfPeriod` - `LastDayOfPeriod` | PeriodBoundary field on the BillingScheduleGroup object | Required |
| `BillingDayOfMonth__std` | The day of the month on which a recurring billing process is scheduled to occur for the transaction. | BillDayOfMonth field on the BillingScheduleGroup object | Required |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Required |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `TaxTreatmentId__std` | The ID of the tax treatment that's used to calculate tax for the transaction. If you don't specify a TaxTreatmentId, the org-default TaxTreatmentId is considered. | TaxTreatmentId field on the BillingScheduleGroup object | Required |
| `BillingTermUnit__std` | The unit of measurement of the billing term. Valid values are:   - `Month` - `Quarter` - `Semi-Annual` - `Year` | BillingTermUnit field on the BillingSchedule object | Required |
| `BillingTreatmentId__std` | The ID of the billing treatment that's used to create the billing schedule for the transaction. If you don't specify a BillingTreatmentId, the org-default BillingTreatmentId is considered. | BillingTreatmentId field on the BillingScheduleGroup object | Required |
| `CurrencyIsoCode__std` | The currency code of the transaction amount if your Salesforce org has multi-currency enabled. | CurrencyIsoCode field on the BillingScheduleGroup object | Required for [Salesforce orgs with multiple currencies enabled](https://help.salesforce.com/s/articleView?id=sales.admin_enable_multicurrency.htm&language=en_US "HTML (New Window)") |
| `BillingActionType__std` | The action that you want to perform for the transaction. Valid value is `Add`. | Category field on the BillingSchedule object is populated as Original. | Required |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total cost to the customer for the transaction, from the start date to the end date. | TotalAmount field on the BillingSchedule object | Required |

#### See Also

- [BillingSchedule](./sforce_api_objects_billingschedule.htm.md "BillingSchedule - HTML (New Window)")
- [BillingScheduleGroup](./sforce_api_objects_billingschedulegroup.htm.md "BillingScheduleGroup - HTML (New Window)")
- [BsgRelationship](./sforce_api_objects_bsgrelationship.htm.md "BsgRelationship - HTML (New Window)")
