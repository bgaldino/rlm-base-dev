---
page_id: connect_requests_billing_schedule_input_for_renewal.htm
title: Renewal Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_renewal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# Renewal Transaction

Create a renewal billing schedule for termed subscriptions that continues without a
gap, starting the day after the current billing schedule group ends and running for the same
term length.

## Considerations

Keep these important considerations in mind when you specify the details for renewal
transactions.

- The `BillingActionType__std` value for renewal
  transactions must be `Renew`.
- The quantity for renewal transactions must be a nonzero positive number.
- The start date of the renewal transaction must be before the maximum end date of all the
  existing billing schedules associated with the billing schedule group.
- The end date of the renewal transaction must be after the maximum end date of all the
  existing transactions associated with the billing schedule group of the related
  transaction.
- Specify a `RelatedTransactionId__std` value with a
  positive quantity.
- For a particular RelatedTransactionId, you can create a billing schedule only for a
  single renewal transaction.
- For renewal transactions, the `TaxTreatmentId__std`
  value, the `BillingTreatmentId__std` value, and the
  `LegalEntityId__std` value of the related transaction
  are considered.

## Renewal Payload Types

The Create Standalone Billing Schedules API accepts two renewal payload types in the
`transactionDetails` node. Use the type that matches
the level of detail you want to provide in the request.

Simplified renewal payloads support these scenarios.

- Renewal to start a new term after the related transaction or billing schedule group
  reaches its end
- As-is renewal to renew each existing billing schedule at its own quantity and net unit
  price

Detailed renewal payloads cover the same outcomes when you specify all transaction details
and financial fields.

Simplified renewal payload
:   Set `BillingActionType__std` to `Renew`. Set `BillingSubActionType__std` to `SimplifiedRenewal` for a standard renewal, or to `AsIsRenewal` for an as-is renewal. Include `TransactionId__std`. Identify the source with either
    `RelatedTransactionId__std` (one billing
    schedule) or `BillingScheduleGroupId__std` (a
    billing schedule group). For a standard renewal, you can omit dates and pricing. The
    API can derive start date, end date, quantity, and price from the related transaction
    record or billing schedule group. You can add optional dates or pricing when you want
    to override derived values. The examples in this topic use `RelatedTransactionId__std`. For renewals with billing schedule group as
    source, use `BillingScheduleGroupId__std`
    instead.

    Renewal (SimplifiedRenewal)
    :   Use this payload structure when the new term begins after the prior term ends.
        This sample shows the minimum fields. Keep these considerations in mind when you
        specify a simplified payload.

        - If you specify a billing schedule group ID, start date is required. If you
          omit the start date and specify a related transaction ID, the API sets the
          start date to a day after the end date of the related billing schedule.
        - If you specify a billing schedule group ID, end date is required. If you
          omit the end date and specify a related transaction ID, the API sets the end
          date by adding one full billing schedule term to that billing schedule’s end
          date (plus one day).
        - If you specify a billing schedule group ID, unit price and net unit price
          are required. If you omit the unit price and net unit price, and specify a
          related transaction ID, the API sets the unit price and net unit price values
          from the related billing schedule.
        - If you specify a billing schedule group ID, quantity is required. If you
          omit the quantity and specify a related transaction ID, the API sets the
          renewal quantity from the related billing schedule.

        This sample shows the transaction data for the simplified renewal with related
        transaction ID as a reference.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ren1",
              "RelatedTransactionId__std": "ter1",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "SimplifiedRenewal"
            }
          ]
        }
        ```

        This sample shows the request payload for the simplified renewal with related
        transaction ID as a reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ren1\",\"RelatedTransactionId__std\":\"ter1\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"SimplifiedRenewal\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the transaction data for the simplified renewal with billing
        schedule group ID as a reference.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "ter3",
              "BillingScheduleGroupId__std": "9Ws00000AXB00AAI",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "SimplifiedRenewal",
              "Quantity__std": 5,
              "UnitPrice__std": 10,
              "StartDate__std": "2025-12-15",
              "EndDate__std": "2026-12-14"
            }
          ]
        }
        ```

        This sample shows the request payload for the simplified renewal with billing
        schedule group ID as a reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter3\",\"BillingScheduleGroupId__std\":\"9Ws00000AXB00AAI\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"SimplifiedRenewal\",\"Quantity__std\":5,\"UnitPrice__std\":10,\"StartDate__std\":\"2025-12-15\",\"EndDate__std\":\"2026-12-14\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    As-is renewal (AsIsRenewal)
    :   Use this payload structure when multiple billing schedules under the reference
        have different quantities or net unit prices and you want one renewal billing
        schedule per source schedule.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "asIsRen1",
              "RelatedTransactionId__std": "ter1",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "AsIsRenewal"
            }
          ]
        }
        ```

        This sample shows the request payload for the same as-is renewal.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"asIsRen1\",\"RelatedTransactionId__std\":\"ter1\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"AsIsRenewal\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

        This sample shows the request payload for the as-is renewal with billing
        schedule group ID as a reference.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "asIsRenew2",
              "BillingScheduleGroupId__std": "9Ws00000AXB00AAI",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "AsIsRenewal"
            }
          ]
        }
        ```

        This sample shows the request payload for the as-is renewal with billing
        schedule group ID as a reference.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"asIsRenew2\",\"BillingScheduleGroupId__std\":\"9Ws00000AXB00AAI\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"AsIsRenewal\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

Detailed renewal payload
:   Send each renewal row with `BillingActionType__std` set to `Renew`
    and include identifiers, related transaction, dates, quantity, unit price, and total
    price. Use this payload type when you already computed the renewal lines yourself.

    This sample includes the transaction data for a standard renewal after the end
    date.

    ```
    {
      "Transaction": [
        {
          "id": "temp1001",
          "TotalPrice__std": 10,
          "Quantity__std": 1,
          "UnitPrice__std": 10,
          "StartDate__std": "2026-03-01",
          "EndDate__std": "2027-12-31",
          "TransactionId__std": "temp1001",
          "BillingActionType__std": "Renew",
          "RelatedTransactionId__std": "temp1"
        }
      ]
    }
    ```

    This sample shows the request payload to create a billing schedule for a renewal.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"temp1001\",\"TotalPrice__std\":10,\"Quantity__std\":1,\"UnitPrice__std\":10,\"StartDate__std\":\"2026-03-01\",\"EndDate__std\":\"2027-12-31\",\"TransactionId__std\":\"temp1001\",\"BillingActionType__std\":\"Renew\",\"RelatedTransactionId__std\":\"temp1\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you renew a new-sale transaction after its end date, those transactions are called
renewal transactions. For example, a new-sale transaction starts on 01/01/2025 and ends on
12/31/2025, and you renew it to start on 03/01/2026 and end on 12/31/2026.

When you're creating a billing schedule for a renewal transaction, make sure that you
provide the mandatory values in the `transactionDetails`
property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `TransactionId__std` | The unique identifier reference to apply to the renewal billing schedule. The Reference and ReferenceItem field on a billing schedule has this value appended with a unique ID generated string. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Required |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `RelatedTransactionId__std` | The ID of the original transaction that's related to the renewal transaction. | This value isn't populated on any BillingSchedule or BillingScheduleGroup field. | Required |
| `BillingScheduleGroupId__std` | ID of the billing schedule group that must be referenced ‌to renew the billing schedule group. | Not applicable. | Specify either `RelatedTransactionId__std` or `BillingScheduleGroupId__std` in your request if you’re sending a simplified payload. |
| `BillingActionType__std` | The action that you want to perform for the transaction.  Specify `Renew` as the BillingActionType for renewal transactions. | Category field on the BillingSchedule object is populated as Renewal. | Required |
| `BillingSubActionType__std` | The sub-action that you want to perform for the transaction. Specify `AsIsRenewal` as the BillingActionType to specify minimal details in the payload for an as-is renewal. Specify `SimplifiedRenewal` as the BillingActionType to specify minimal details in the payload for a renewal or an early renewal. Available in API version 67.0 and later. | SubCategory field on the BillingSchedule object | Optional |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
