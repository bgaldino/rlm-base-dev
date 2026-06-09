---
page_id: connect_requests_billing_schedule_input_for_bundled_products_new_sale.htm
title: New Sale Transaction With Bundled Products
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_bundled_products_new_sale.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# New Sale Transaction With Bundled Products

Understand the required values and key considerations before you create a billing
schedule for a new sale transaction with bundled products.

## Considerations

Keep these important considerations in mind when you provide the details for new sale
transactions with bundled products.

- The `BillingActionType__std` value for any new sale
  transaction must be `Add`.
- For new sale transactions with bundled products, the `MainTransactionId__std` value is required for all the child transactions.
- If you don't provide the `TaxTreatmentId__std` value,
  the `BillingTreatmentId__std` value, or the `LegalEntityId__std` value for the transaction, the default
  TaxTreatmentId, BillingTreatmentId, and
  LegalEntityId of your Salesforce org is considered. If your org
  doesn't have any default values, an error occurs.
- If your transaction is for an sObject record, only specify the record ID as the id value
  in the `transactionDetails` property value. All the
  other transaction details are automatically fetched from the sObject record if those
  details are mapped in the context definition.
- To understand the requirements for the various selling model types, see these resources.
  - [One-Time New Sale
    Transaction](./connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the OneTime selling model type.")
  - [Term-Defined New Sale
    Transaction](./connect_requests_billing_schedule_input_for_termed_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the TermDefined selling model type.")
  - [Evergreen New Sale
    Transaction](./connect_requests_billing_schedule_input_for_evergreen_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the Evergreen selling model type.")

JSON example
:   This sample is for a new sale transaction for bundled products with two levels of
    nesting and with these selling model types.

    - The main root product's selling model type is `OneTime`.
    - The second root product's selling model type is `OneTime`.
    - The child products' selling model types are `TermDefined` and `Evergreen`.

    ```
    {
      "Transaction": [
        {
          "id": "sample1",
          "SellingModelType__std": "OneTime",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sample1",
          "ProductName__std": "OneTimeProduct",
          "StartDate__std": "2025-02-20",
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 10,
          "TaxTreatmentId__std": "1ttLT000000EV7DYAW",
          "BillingTreatmentId__std": "1BTLT00000008yT4AQ",
          "AccountId__std": "001LT00000dPVrlYAG",
          "BillToContactId__std": "003LT0000038bALYAY",
          "BillingCity__std": "HYD",
          "ShippingCity__std": "VSKP",
          "BillingActionType__std": "Add",
          "CurrencyIsoCode__std": "USD"
        },
        {
          "id": "sample2",
          "SellingModelType__std": "OneTime",
          "ParentTransactionId__std": "abc",
          "TransactionId__std": "sample2",
          "ProductName__std": "OneTimeProduct",
          "StartDate__std": "2025-02-20",
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 10,
          "TaxTreatmentId__std": "1ttLT000000EV7DYAW",
          "BillingTreatmentId__std": "1BTLT00000008yT4AQ",
          "AccountId__std": "001LT00000dPVrlYAG",
          "BillToContactId__std": "003LT0000038bALYAY",
          "BillingActionType__std": "Add",
          "CurrencyIsoCode__std": "USD",
          "BillingCity__std": "HYD",
          "ShippingCity__std": "VSKP",
          "AssociatedTransactionPricing__std": "IncludedInBundlePrice",
          "MainTransactionRole__std": "Bundle",
          "AssociatedTransactionRole__std": "BundleComponent",
          "MainTransactionId__std": "sample1"
        },
        {
          "id": "sample3",
          "SellingModelType__std": "TermDefined",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sample3",
          "ProductName__std": "TermedQuarterlyProduct",
          "StartDate__std": "2025-01-01",
          "EndDate__std": "2025-12-31",
          "PeriodBoundary__std": "DayOfPeriod",
          "BillingDayOfMonth__std": 1,
          "BillingStartMonth__std": 2,
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 120,
          "TaxTreatmentId__std": "1ttLT000000EV7DYAW",
          "BillingTreatmentId__std": "1BTLT00000008yT4AQ",
          "AccountId__std": "001LT00000dPVrlYAG",
          "BillToContactId__std": "003LT0000038bALYAY",
          "BillingTermUnit__std": "Quarter",
          "BillingActionType__std": "Add",
          "CurrencyIsoCode__std": "USD",
          "BillingCity__std": "HYD",
          "ShippingCity__std": "VSKP",
          "AssociatedTransactionPricing__std": "IncludedInBundlePrice",
          "MainTransactionRole__std": "Bundle",
          "AssociatedTransactionRole__std": "BundleComponent",
          "MainTransactionId__std": "sample2"
        },
        {
          "id": "sample4",
          "SellingModelType__std": "Evergreen",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sample4",
          "ProductName__std": "EvergreenSemiAnnualProduct",
          "StartDate__std": "2025-01-01",
          "PeriodBoundary__std": "DayOfPeriod",
          "BillingDayOfMonth__std": 1,
          "BillingStartMonth__std": 3,
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 10,
          "TaxTreatmentId__std": "1ttLT000000EV7DYAW",
          "BillingTreatmentId__std": "1BTLT00000008yT4AQ",
          "AccountId__std": "001LT00000dPVrlYAG",
          "BillToContactId__std": "003LT0000038bALYAY",
          "BillingTermUnit__std": "Semi-Annual",
          "BillingActionType__std": "Add",
          "BillingPostalCode__std": "94105",
          "CurrencyIsoCode__std": "USD",
          "BillingCity__std": "HYD",
          "ShippingCity__std": "VSKP",
          "AssociatedTransactionPricing__std": "IncludedInBundlePrice",
          "MainTransactionRole__std": "Bundle",
          "AssociatedTransactionRole__std": "BundleComponent",
          "MainTransactionId__std": "sample2"
        }
      ]
    }
    ```

    This example shows the request payload to create a billing schedule for a new sale
    transaction for bundled products.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"sample1\",\"SellingModelType__std\":\"OneTime\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sample1\",\"ProductName__std\":\"OneTimeProduct\",\"StartDate__std\":\"2025-02-20\",\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":10,\"TaxTreatmentId__std\":\"1ttLT000000EV7DYAW\",\"BillingTreatmentId__std\":\"1BTLT00000008yT4AQ\",\"AccountId__std\":\"001LT00000dPVrlYAG\",\"BillToContactId__std\":\"003LT0000038bALYAY\",\"BillingCity__std\":\"HYD\",\"ShippingCity__std\":\"VSKP\",\"BillingActionType__std\":\"Add\",\"CurrencyIsoCode__std\":\"USD\"},{\"id\":\"sample2\",\"SellingModelType__std\":\"OneTime\",\"ParentTransactionId__std\":\"abc\",\"TransactionId__std\":\"sample2\",\"ProductName__std\":\"OneTimeProduct\",\"StartDate__std\":\"2025-02-20\",\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":10,\"TaxTreatmentId__std\":\"1ttLT000000EV7DYAW\",\"BillingTreatmentId__std\":\"1BTLT00000008yT4AQ\",\"AccountId__std\":\"001LT00000dPVrlYAG\",\"BillToContactId__std\":\"003LT0000038bALYAY\",\"BillingActionType__std\":\"Add\",\"CurrencyIsoCode__std\":\"USD\",\"BillingCity__std\":\"HYD\",\"ShippingCity__std\":\"VSKP\",\"AssociatedTransactionPricing__std\":\"IncludedInBundlePrice\",\"MainTransactionRole__std\":\"Bundle\",\"AssociatedTransactionRole__std\":\"BundleComponent\",\"MainTransactionId__std\":\"sample1\"},{\"id\":\"sample3\",\"SellingModelType__std\":\"TermDefined\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sample3\",\"ProductName__std\":\"TermedQuarterlyProduct\",\"StartDate__std\":\"2025-01-01\",\"EndDate__std\":\"2025-12-31\",\"PeriodBoundary__std\":\"DayOfPeriod\",\"BillingDayOfMonth__std\":1,\"BillingStartMonth__std\":2,\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":120,\"TaxTreatmentId__std\":\"1ttLT000000EV7DYAW\",\"BillingTreatmentId__std\":\"1BTLT00000008yT4AQ\",\"AccountId__std\":\"001LT00000dPVrlYAG\",\"BillToContactId__std\":\"003LT0000038bALYAY\",\"BillingTermUnit__std\":\"Quarter\",\"BillingActionType__std\":\"Add\",\"CurrencyIsoCode__std\":\"USD\",\"BillingCity__std\":\"HYD\",\"ShippingCity__std\":\"VSKP\",\"AssociatedTransactionPricing__std\":\"IncludedInBundlePrice\",\"MainTransactionRole__std\":\"Bundle\",\"AssociatedTransactionRole__std\":\"BundleComponent\",\"MainTransactionId__std\":\"sample2\"},{\"id\":\"sample4\",\"SellingModelType__std\":\"Evergreen\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sample4\",\"ProductName__std\":\"EvergreenSemiAnnualProduct\",\"StartDate__std\":\"2025-01-01\",\"PeriodBoundary__std\":\"DayOfPeriod__std\",\"BillingDayOfMonth__std\":1,\"BillingStartMonth__std\":3,\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":10,\"TaxTreatmentId__std\":\"1ttLT000000EV7DYAW\",\"BillingTreatmentId__std\":\"1BTLT00000008yT4AQ\",\"AccountId__std\":\"001LT00000dPVrlYAG\",\"BillToContactId__std\":\"003LT0000038bALYAY\",\"BillingTermUnit__std\":\"Semi-Annual\",\"BillingActionType__std\":\"Add\",\"BillingPostalCode__std\":\"94105\",\"CurrencyIsoCode__std\":\"USD\",\"BillingCity__std\":\"HYD\",\"ShippingCity__std\":\"VSKP\",\"AssociatedTransactionPricing__std\":\"IncludedInBundlePrice\",\"MainTransactionRole__std\":\"Bundle\",\"AssociatedTransactionRole__std\":\"BundleComponent\",\"MainTransactionId__std\":\"sample2\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you're creating a billing schedule for a new sale transaction with bundled products,
make sure that you specify the mandatory values in the `transactionDetails` property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `BillToContactId__std` | The ID of the Contact record that's related to the transaction. | BillToContactId field on the BillingScheduleGroup object | Required |
| `ParentTransactionId__std` | The ID of the parent transaction record. For example, if the transaction is at a level similar to that of an Order Item record, the parent transaction will be at a level similar to that of an Order record. | If the transaction is a child Order or Quote record, the ReferenceEntityId field on the BillingScheduleobject is populated. For other sObject records or external records, the Reference field on the BillingSchedule object is populated. | Optional |
| `AccountId__std` | The ID of the Account record that's related to the transaction. | BillingAccountId field on the BillingScheduleGroup object | Required |
| `BillingCity__std` | The city in the billing address of the transaction. | BillingCity field on the BillingScheduleGroup object | Any one of the billing address fields is required. |
| `BillingPostalCode__std` | The postal code in the billing address of the transaction. | BillingPostalCode field on the BillingScheduleGroup object | Any one of the billing address fields is required. |
| `ShippingCity__std` | The city in the shipping address of the transaction. | ShippingCity field on the BillingScheduleGroup object | Any one of the shipping address fields is required. |
| `SellingModelType__std` | The selling model type indicates whether the transaction is for a one-time product, a term-defined product, or an evergreen product. Specify `OneTime` as the SellingModelType for the transaction that's related to a product that's sold once. | BillingMethod on the BillingSchedule object is populated as OrderAmount. | Required |
| `TransactionId__std` | The ID of the transaction that you want to create a billing schedule for. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `ProductName__std` | The name of the product that's related to the transaction that you want to create a billing schedule for. | ProductName field on the BillingScheduleGroup object | Either the ProductName or the ProductId value is required |
| `PeriodBoundary__std` | The period boundary determines the start and end date of the billing period. Valid values are:  - `AlignToCalendar` - `Anniversary` - `DayOfPeriod` - `LastDayOfPeriod` | PeriodBoundary field on the BillingScheduleGroup object | Required for child products with the `TermDefined` or `Evergreen` selling model types. |
| `BillingDayOfMonth__std` | The day of the month on which a recurring billing process is scheduled to occur for the transaction. | BillDayOfMonth field on the BillingScheduleGroup object | Required for child products with the `TermDefined` or `Evergreen` selling model types. |
| `BillingStartMonth__std` | The month when billing begins for an annual subscription. This value can be any number from `1` through `12`. For example, if billing starts in January, the value is `1`. If billing starts in June, the value is `6`. | BillingStartMonth field on the BillingScheduleGroup object | Required for child products with the `Evergreen` selling model type. |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Required for child products with the `TermDefined` selling model type. |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `TaxTreatmentId__std` | The ID of the tax treatment that's used to calculate tax for the transaction. If you don't specify a TaxTreatmentId, the org-default TaxTreatmentId is considered. | TaxTreatmentId field on the BillingScheduleGroup object | Required |
| `BillingTermUnit__std` | The unit of measurement of the billing term. Valid values are:  - `Month` - `Quarter` - `Semi-Annual` - `Year` | BillingTermUnit field on the BillingSchedule object | Required for child products with the `TermDefined` or `Evergreen` selling model types. |
| `BillingTreatmentId__std` | The ID of the billing treatment that's used to create the billing schedule for the transaction. If you don't specify a BillingTreatmentId, the org-default BillingTreatmentId is considered. | BillingTreatmentId field on the BillingScheduleGroup object | Required |
| `CurrencyIsoCode__std` | The currency code of the transaction amount if your Salesforce org has multi-currency enabled. | CurrencyIsoCode field on the BillingScheduleGroup object | Required for [Salesforce orgs with multiple currencies enabled](https://help.salesforce.com/s/articleView?id=sales.admin_enable_multicurrency.htm&language=en_US "HTML (New Window)"). |
| `BillingActionType__std` | The action that you want to perform for the transaction. Valid value is `Add`. | Category field on the BillingSchedule object is populated as Original. | Required |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
| `MainTransactionId__std` | When your transaction is part of a bundle, this value is the ID of the main transaction record for all the child transactions. | MainBsgId field on the BsgRelationship object | Required for all the child products. |
| `MainTransactionRole__std` | When your transaction is part of a bundle, this value is the role of the primary transaction in the bundle relationship. Valid values are:  - `AddOn` - `Bundle` - `Set` | MainBsgRole field on the BsgRelationship object | Required for all the child products. |
| `AssociatedTransactionRole__std` | When your transaction is part of a bundle, this value is the role of the child transaction in the bundle relationship. Valid values are:  - - `BundleComponent`   - `ClassificationComponent` | AssociatedBsgRole field on the BsgRelationship object | Required for all the child products. |
| `AssociatedTransactionPricing__std` | When your transaction is part of a bundle, this value describes how the child transaction is priced in relation to the primary transaction. Valid values are:  - `IncludedInBundlePrice` - `NotIncludedInBundlePrice` | AssociatedBsgPricing field on the BsgRelationship object | Required for all the child products. |

#### See Also

- [BillingSchedule](./sforce_api_objects_billingschedule.htm.md "BillingSchedule - HTML (New Window)")
- [BillingScheduleGroup](./sforce_api_objects_billingschedulegroup.htm.md "BillingScheduleGroup - HTML (New Window)")
- [BsgRelationship](./sforce_api_objects_bsgrelationship.htm.md "BsgRelationship - HTML (New Window)")
