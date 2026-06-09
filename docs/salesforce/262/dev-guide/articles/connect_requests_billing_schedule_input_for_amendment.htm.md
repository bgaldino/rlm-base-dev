---
page_id: connect_requests_billing_schedule_input_for_amendment.htm
title: Amended Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_amendment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# Amended Transaction

Learn how amendments update quantity, price, and end date in billing schedules along
with delta-only price transactions and billing-frequency changes at the billing schedule
level.

## Considerations

Keep these important considerations in mind when providing the details for amended
transactions.

- The `BillingActionType__std`  value for any amended
  transaction must be `Amend`.
- When you provide a negative quantity, make sure that it’s less than the total quantity
  of the related transaction.
- If your transaction is for an sObject record, only specify the record ID as the id value
  in the `transactionDetails` property value. All the
  other transaction details are automatically fetched from the sObject record if those
  details are mapped in the context definition.

## Amendment Payload Types

The Create Standalone Billing Schedules API
accepts two amendment payload types in the `transactionDetails` node. Use the type that matches the level of detail you want
to provide in the request.

Simplified amendment payloads support these scenarios.

- Negative amendment to reduce quantity
- Positive amendment to add quantity
- Price amendment to change net or unit price from an effective date
- End date change to extend or shorten the subscription term
- Delta price change to pass a price delta as a single adjustment
- Billing frequency update at the billing schedule group level

Detailed amendment payloads cover the same business outcomes when you specify all
transaction details and financial fields.

Simplified amendment payload
:   Set `BillingActionType__std` to `Amend`. Set `BillingSubActionType__std` to `QuantityAmend`, `PriceAmend`, `EndDateChange`, `DeltaPriceAmend`, or `BillingFrequencyChange` depending on the scenario. Include `TransactionId__std` and `StartDate__std`. Identify the source with either `RelatedTransactionId__std` (one billing schedule) or
    `BillingScheduleGroupId__std` (a billing schedule
    group). The examples in the scenario-specific sections in this topic use `RelatedTransactionId__std`. For amendments by using a
    billing schedule group as source, use `BillingScheduleGroupId__std` instead.

    Negative amendment (QuantityAmend)
    :   Reduce quantity from a start date by specifying the reduction quantity as a
        negative number along with the start date.

        If you specify a related
        transaction, the reduction is applied against that transaction’s billing
        schedules. If you specify a billing schedule group ID, the API applies
        reductions in Last In, First Out (LIFO) order within that billing schedule
        group.

        The API determines which billing schedules to reduce, validates
        that sufficient net quantity exists, and checks whether price can be derived
        through proration or whether `TotalPrice` can
        be accepted when specified.

        This sample includes a negative `Quantity__std` for the quantity to remove from the
        effective date.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "a2",
              "RelatedTransactionId__std": "a1",
              "StartDate__std": "2025-05-01",
              "Quantity__std": -2,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "QuantityAmend"
            }
          ]
        }
        ```

        This sample shows the request payload for the same negative
        quantity amendment.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"a2\",\"RelatedTransactionId__std\":\"a1\",\"StartDate__std\":\"2025-05-01\",\"Quantity__std\":-2,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"QuantityAmend\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the transaction data that references a billing
        schedule group.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "a2",
              "BillingScheduleGroupId__std": "9Ws00000AXB00AAI",
              "StartDate__std": "2025-05-01",
              "Quantity__std": -2,
              "BillingActionType__std": "Amend",
             "BillingSubActionType__std": "QuantityAmendment"
            }
          ]
        }
        ```

        This sample shows the request payload when billing schedule
        group is used as a
        reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"a2\",\"BillingScheduleGroupId__std\":\"9Ws00000AXB00AAI\",\"StartDate__std\":\"2025-05-01\",\"Quantity__std\":-2,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"QuantityAmendment\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Positive amendment (QuantityAmend)
    :   Add quantity from a start date. Specify minimal information in the payload.
        The API derives the billing schedule to amend and, if not specified, the unit
        price and total price. Use a positive `Quantity__std` for the quantity to add from the effective
        date.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "a2",
              "RelatedTransactionId__std": "a1",
              "StartDate__std": "2025-05-01",
              "Quantity__std": 2,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "QuantityAmend"
            }
          ]
        }
        ```

        This sample shows the request payload for the same positive
        quantity amendment.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"a2\",\"RelatedTransactionId__std\":\"a1\",\"StartDate__std\":\"2025-05-01\",\"Quantity__std\":2,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"QuantityAmend\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the transaction data that references a billing
        schedule group.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "a2",
              "BillingScheduleGroupId__std": "9Ws00000AXB00AAI",
              "StartDate__std": "2025-05-01",
              "Quantity__std": 2,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "QuantityAmendment"
            }
          ]
        }
        ```

        This sample shows the request payload when billing schedule
        group is used as a
        reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"a2\",\"BillingScheduleGroupId__std\":\"9Ws00000AXB00AAI\",\"StartDate__std\":\"2025-05-01\",\"Quantity__std\":2,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"QuantityAmendment\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Price amendment (PriceAmend)
    :   Change the price from a given start date. For example, apply a new net unit
        price or unit price. The API cancels the existing billing schedule(s) from that
        date and creates new positive amendment billing schedule with the updated price
        . Specify the new `NetUnitPrice__std` or
        `UnitPrice__std` effective on `StartDate__std`. This sample uses net unit
        price.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ter3",
              "RelatedTransactionId__std": "ter1",
              "StartDate__std": "2026-04-01",
              "NetUnitPrice__std": 20,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "PriceAmend"
            }
          ]
        }
        ```

        This sample shows the request payload for the same price
        amendment.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter3\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2026-04-01\",\"NetUnitPrice__std\":20,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"PriceAmend\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the transaction data that references a billing
        schedule group with delta quantity to amend price on an entire billing schedule
        group.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ter4",
              "BillingScheduleGroupId__std": "9Wsxx000000026fCAA",
              "StartDate__std": "2026-06-01",
              "NetUnitPrice__std": 30,
              "Quantity__std": 1,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "PriceAmend"
            }
          ]
        }
        ```

        This sample shows the request payload when billing schedule
        group is used as a
        reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter4\",\"BillingScheduleGroupId__std\":\"9Wsxx000000026fCAA\",\"StartDate__std\":\"2026-06-01\",\"NetUnitPrice__std\":30,\"Quantity__std\":1,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"PriceAmend\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    End date change (EndDateChange)
    :   Change the end date of the subscription or of a specific billing schedule
        under a billing schedule group from a specified start date. The API cancels the
        existing billing schedule(s) from that start date and creates a new positive
        amendment billing schedule from the start date to the new end
        date.

        Specify `StartDate__std` to
        specify when the change is effective and `EndDate__std` for the new end of the
        term.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ter3",
              "RelatedTransactionId__std": "ter1",
              "StartDate__std": "2026-05-01",
              "EndDate__std": "2026-09-01",
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "EndDateChange"
            }
          ]
        }
        ```

        This sample shows the request payload for the same end date
        change on one billing schedule by using related transaction
        ID.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter3\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2026-05-01\",\"EndDate__std\":\"2026-09-01\",\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"EndDateChange\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the transaction data that references a billing
        schedule group for end date change on one billing schedule
        group.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ter3",
              "BillingScheduleGroupId__std": "9Wsxx000000026fCAA",
              "StartDate__std": "2026-05-01",
              "EndDate__std": "2026-09-01",
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "ChangeEndDate"
            }
          ]
        }
        ```

        This sample shows the request payload when billing schedule
        group is used as a
        reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter3\",\"BillingScheduleGroupId__std\":\"9Wsxx000000026fCAA\",\"StartDate__std\":\"2026-05-01\",\"EndDate__std\":\"2026-09-01\",\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"ChangeEndDate\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Delta price change (DeltaPriceAmend)
    :   Change a subscription's price mid-term. For example, manage modifications
        such as add or remove features, or apply special discounts and price
        uplifts.

        Send `Quantity__std` as
        `0` with `TotalPrice__std` set to the delta amount, or send a non-zero quantity
        with `NetUnitPrice__std` as the delta net
        unit price. This sample shows the zero-quantity delta total price
        pattern.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "amendmentSampleId1",
              "RelatedTransactionId__std": "ter1",
              "StartDate__std": "2025-07-01",
              "TotalPrice__std": 600,
              "Quantity__std": 0,
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "DeltaPriceAmend"
            }
          ]
        }
        ```

        This sample shows the request payload for the same delta price
        change.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"amendmentSampleId1\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2025-07-01\",\"TotalPrice__std\":600,\"Quantity__std\":0,\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"DeltaPriceAmend\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Billing frequency update at billing schedule group (BillingFrequencyChange)
    :   Change how often the subscription bills for all billing schedules in a billing
        schedule group. Set `BillingSubActionType__std` to `BillingFrequencyChange`, identify the group with `BillingScheduleGroupId__std`, set `BillingTermUnit__std` to the new term unit (for
        example, `Quarter`), and set `StartDate__std` when the new frequency is
        effective. Include `TransactionId__std`.
        Optionally, include `BillingStartMonth__std`
        when the billing selling model requires it for that term unit.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "bfTer1",
              "BillingScheduleGroupId__std": "9Ws00000AXB00AAI",
              "StartDate__std": "2025-05-01",
              "BillingTermUnit__std": "Quarter",
              "BillingActionType__std": "Amend",
              "BillingSubActionType__std": "BillingFrequencyChange"
            }
          ]
        }
        ```

        This sample shows the request payload for the same billing frequency
        update.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"bfTer1\",\"BillingScheduleGroupId__std\":\"9Ws00000AXB00AAI\",\"StartDate__std\":\"2025-05-01\",\"BillingTermUnit__std\":\"Quarter\",\"BillingActionType__std\":\"Amend\",\"BillingSubActionType__std\":\"BillingFrequencyChange\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

Detailed amendment payload
:   Send each amendment as its own transaction with `BillingActionType__std` set to `Amend`.
    Include identifiers, `RelatedTransactionId__std`,
    and the financial fields for each line. Use this payload type when you already
    computed quantities, unit prices, and total prices. This sample includes one positive
    amendment and two negative amendments for the same related transaction.

    This sample includes the transaction data for an amendment.

    ```
    {
      "Transaction": [
        {
          "id": "sampleA1",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sampleA1",
          "RelatedTransactionId__std": "ter1",
          "StartDate__std": "2025-04-01",
          "UnitPrice__std": 10,
          "Quantity__std": 1,
          "TotalPrice__std": 90,
          "BillingActionType__std": "Amend"
        },
        {
          "id": "sampleA2",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sampleA2",
          "RelatedTransactionId__std": "ter1",
          "StartDate__std": "2025-03-01",
          "UnitPrice__std": 10,
          "Quantity__std": -2,
          "TotalPrice__std": -200,
          "BillingActionType__std": "Amend"
        },
        {
          "id": "sampleA3",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "sampleA3",
          "RelatedTransactionId__std": "ter1",
          "StartDate__std": "2025-03-01",
          "UnitPrice__std": 10,
          "Quantity__std": -1,
          "TotalPrice__std": -100,
          "BillingActionType__std": "Amend"
        }
      ]
    }
    ```

    This sample shows the request payload to create a billing schedule for an
    amendment.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"sampleA1\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sampleA1\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2025-04-01\",\"UnitPrice__std\":10,\"Quantity__std\":1,\"TotalPrice__std\":90,\"BillingActionType__std\":\"Amend\"},{\"id\":\"sampleA2\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sampleA2\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2025-03-01\",\"UnitPrice__std\":10,\"Quantity__std\":-2,\"TotalPrice__std\":-200,\"BillingActionType__std\":\"Amend\"},{\"id\":\"sampleA3\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"sampleA3\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2025-03-01\",\"UnitPrice__std\":10,\"Quantity__std\":-1,\"TotalPrice__std\":-100,\"BillingActionType__std\":\"Amend\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you're creating a billing schedule for an amended transaction, make sure that you
specify the mandatory values in the transactionDetails property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `ParentTransactionId__std` | The ID of the parent transaction record. For example, if the transaction is at a level similar to that of an Order Item record, the parent transaction will be at a level similar to that of an Order record. | If the transaction is a child Order or Quote record, the ReferenceEntityId field on the BillingScheduleobject is populated. For other sObject records or external records, the Reference field on the BillingSchedule object is populated. | Optional |
| `TransactionId__std` | The unique identifier reference to apply to the billing schedule with amendment or updated billing frequency. The Reference and ReferenceItem field on a billing schedule has this value appended with a unique ID generated string. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `BillingStartMonth__std` | The month when billing begins for an annual subscription. This value can be any number from `1` through `12`. For example, if billing starts in January, the value is `1`. If billing starts in June, the value is `6`. | BillingStartMonth field on the BillingScheduleGroup object | Optional. Required if the billing term unit is Quarter, Semi-Annual, or Annual. |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Optional. Required in case of an end date change of a subscription. |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `BillingTermUnit__std` | The unit of measurement of the billing term. Valid values are:   - `Month` - `Quarter` - `Semi-Annual` - `Year` | BillingTermUnit field on the BillingSchedule object | Optional |
| `RelatedTransactionId__std` | The ID of the related transaction that must be referenced for an amendment. | This value isn't populated on any BillingSchedule or BillingScheduleGroup field. | Required |
| `BillingScheduleGroupId__std` | ID of the billing schedule group that must be referenced for an amendment. | Not applicable. | Specify either `RelatedTransactionId__std` or `BillingScheduleGroupId__std` in your request if you’re sending a simplified payload. |
| `BillingActionType__std` | The action that you want to perform for the transaction.  Specify `Amend` as the BillingActionType for amended transactions. | Category field on the BillingSchedule object is populated as AmendQuantity. | Required |
| `BillingSubActionType__std` | The sub-action that you want to perform for the transaction.  Specify `PriceAmend`, `QuantityAmend`, or `DeltaPriceAmend` as the BillingActionType to specify minimal details in the payload for a price, quantity, or delta price amendment respectively. Specify `EndDateChange` as the BillingActionType to change the end date of a subscription. Specify `BillingFrequencyChange` as the BillingActionType to update the billing frequency at the billing schedule group level. Available in API version 67.0 and later. | SubCategory field on the BillingSchedule object | Optional |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
| `NetUnitPrice__std` | The net unit price of the transaction. | NetUnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
