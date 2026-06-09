---
page_id: connect_requests_billing_schedule_input_for_early_renewal.htm
title: Early Renewal Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_early_renewal.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# Early Renewal Transaction

Early Renewal ends the current term at an effective date and starts a renewed term to a
new end date, creating two billing schedules in one request. The request creates a negative
segment for the remaining original term and a positive segment for the renewal term.

## Considerations

Keep these important considerations in mind when you specify the details for early renewal
transactions.

- The `BillingActionType__std` value for early renewal
  transactions must be `Renew`.
- When you're creating billing schedules for early renewal transactions, your input
  payload must have details for two transactions.

  - A transaction to cancel the existing new-sale transaction. The details of this
    transaction must include a negative quantity to cancel billing for the remaining
    period. The quantity for this transaction must be the negative equivalent of the total
    quantity of all the existing billing schedules associated with the same billing
    schedule group.
  - Another transaction that specifies the early renewal details, which must have a
    positive quantity.
  - The `BillingActionType__std` value for both these
    transactions must be `Renew`.
- The start date of the early renewal transaction must be:

  - Before the end date of the related transaction.
  - Before the maximum end date of all the existing billing schedules associated with
    the billing schedule group of the related transaction.
  - The same as the start date of all the existing billing schedules associated with the
    same billing schedule group or after it.
- The end date for the early renewal transaction must be after the maximum end date of all
  the existing transactions associated with the billing schedule group of the related
  transaction.
- For early renewal transactions, the `TaxTreatmentId__std` value, the `BillingTreatmentId__std` value, and the `LegalEntityId__std` value of the related transaction are considered.

## Early Renewal Payload Types

The Create Standalone Billing Schedules API accepts two early renewal payload types in the
`transactionDetails` node. Use the type that matches
the level of detail you want to provide in the request.

Simplified early renewal payloads support these scenarios.

- Early renewal by related transaction by using `SimplifiedRenewal` sub-action type with an effective start date before the
  current term end and a new end date.
- Early renewal by billing schedule group by using `SimplifiedRenewal` sub-action type with the same date rules at the group
  level
- Early as-is renewal by using `AsIsRenewal` sub-action
  type when each underlying billing schedule should renew at its own quantity and net unit
  price from an effective date before the group end.

For renewal that begins after the prior term or billing schedule group ends, see [Renewal Transaction](./connect_requests_billing_schedule_input_for_renewal.htm.md "Create a renewal billing schedule for termed subscriptions that continues without a gap, starting the day after the current billing schedule group ends and running for the same term length.").

Detailed early renewal payloads use separate cancel and renewal rows when you supply full
transaction and financial fields yourself.

Simplified early renewal payload
:   Set `BillingActionType__std` to `Renew`. Set `BillingSubActionType__std` to `SimplifiedRenewal` for a blended early renewal, or to `AsIsRenewal` for an early as-is renewal. Include `TransactionId__std`, `StartDate__std` (before the related transaction or group end), and `EndDate__std` for the new term. Identify the source with
    either `RelatedTransactionId__std` (one billing
    schedule) or `BillingScheduleGroupId__std` (a
    billing schedule group). The API can derive quantity and pricing when you omit those
    fields.

    Early renewal by related transaction (SimplifiedRenewal)
    :   ```
        {
          "Transaction": [
            {
              "TransactionId__std": "earlyRen1",
              "RelatedTransactionId__std": "ter1",
              "StartDate__std": "2025-12-15",
              "EndDate__std": "2026-12-14",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "SimplifiedRenewal"
            }
          ]
        }
        ```

        This sample shows the request payload for the same simplified early renewal by
        using related transaction ID.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"earlyRen1\",\"RelatedTransactionId__std\":\"ter1\",\"StartDate__std\":\"2025-12-15\",\"EndDate__std\":\"2026-12-14\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"SimplifiedRenewal\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Early renewal by billing schedule group (SimplifiedRenewal)
    :   ```
        {
          "Transaction": [
            {
              "TransactionId__std": "earlyRen2",
              "BillingScheduleGroupId__std": "9Wsxx00000001ovCAA",
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

        This sample shows the request payload for the same simplified early renewal by
        using billing schedule group.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"earlyRen2\",\"BillingScheduleGroupId__std\":\"9Wsxx00000001ovCAA\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"SimplifiedRenewal\",\"Quantity__std\":5,\"UnitPrice__std\":10,\"StartDate__std\":\"2025-12-15\",\"EndDate__std\":\"2026-12-14\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Early as-is renewal (AsIsRenewal)
    :   Use this pattern when the billing schedule group has multiple billing schedules
        with different quantities or net unit prices and the renewal effective date is
        before the group end.

        ```
        {
          "Transaction": [
            {
              "TransactionId__std": "asIsEarly1",
              "BillingScheduleGroupId__std": "9Wsxx00000001ovCAA",
              "StartDate__std": "2025-12-15",
              "EndDate__std": "2026-12-14",
              "BillingActionType__std": "Renew",
              "BillingSubActionType__std": "AsIsRenewal"
            }
          ]
        }
        ```

        This sample shows the request payload for the same early as-is renewal.

        ```
        {
          "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"asIsEarly1\",\"BillingScheduleGroupId\":\"9Wsxx00000001ovCAA\",\"StartDate__std\":\"2025-12-15\",\"EndDate__std\":\"2026-12-14\",\"BillingActionType__std\":\"Renew\",\"BillingSubActionType__std\":\"AsIsRenewal\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext__stdctx",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "TransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

Detailed early renewal payload
:   Send two transactions with `BillingActionType__std` set to `Renew`
    for each row. The first transaction ends billing for the remainder of the current term
    with a negative quantity. The second transaction starts the new term with a positive
    quantity. Include identifiers, related transaction, dates, unit price, and total price
    for each row.

    This sample includes the transaction data for an early renewal.

    ```
    {
      "Transaction": [
        {
          "id": "temp71",
          "TotalPrice__std": -10,
          "Quantity__std": -1,
          "UnitPrice__std": 10,
          "StartDate__std": "2026-12-31",
          "EndDate__std": "2027-12-31",
          "TransactionId__std": "temp71",
          "BillingActionType__std": "Renew",
          "RelatedTransactionId__std": "test21"
        },
        {
          "id": "temp72",
          "TotalPrice__std": 10,
          "Quantity__std": 1,
          "UnitPrice__std": 10,
          "StartDate__std": "2026-12-31",
          "EndDate__std": "2027-12-31",
          "TransactionId__std": "temp72",
          "BillingActionType__std": "Renew",
          "RelatedTransactionId__std": "test21"
        }
      ]
    }
    ```

    This sample shows the request payload to create a billing schedule for an early
    renewal.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"temp71\",\"TotalPrice__std\":-10,\"Quantity__std\":-1,\"UnitPrice__std\":10,\"StartDate__std\":\"2026-12-31\",\"EndDate__std\":\"2027-12-31\",\"TransactionId__std\":\"temp71\",\"BillingActionType__std\":\"Renew\",\"RelatedTransactionId__std\":\"test21\"},{\"id\":\"temp72\",\"TotalPrice__std\":10,\"Quantity__std\":1,\"UnitPrice__std\":10,\"StartDate__std\":\"2026-12-31\",\"EndDate__std\":\"2027-12-31\",\"TransactionId__std\":\"temp72\",\"BillingActionType__std\":\"Renew\",\"RelatedTransactionId__std\":\"test21\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you renew a new-sale transaction before its end date, those transactions are called
early renewal transactions. For example, a new-sale transaction starts on 01/01/2025 and
ends on 12/31/2025, and you renew it to start on 12/01/2025 and end on 12/31/2026.

When a billing schedule is created for an early renewal transaction, it results in these
updates.

- The cancellation date on the original billing schedule is populated.
- A billing schedule with a negative quantity is created and can be used for a
  refund.
- A billing schedule with a positive quantity is created for the early renewal
  transaction.

When you're creating a billing schedule for an early renewal transaction, make sure that
you provide the mandatory values in the `transactionDetails` property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `TransactionId__std` | The unique identifier reference to apply to the renewal billing schedule. The Reference and ReferenceItem field on a billing schedule has this value appended with a unique ID generated string. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Required |
| `EndDate__std` | The end date of the transaction. | BillingScheduleEndDate field on the BillingSchedule object | Required for a positive transaction. Optional for a negative transaction. |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `Quantity__std` | The quantity of the transaction. | Quantity field on the BillingSchedule object | Required |
| `RelatedTransactionId__std` | The ID of the transaction against which you're doing an early renewal. This transaction must have a positive quantity. | This value isn't populated on any BillingSchedule or BillingScheduleGroup field. | Required |
| `BillingScheduleGroupId__std` | ID of the billing schedule group that must be referenced ‌to renew each billing schedule in the billing schedule group early. | Not applicable. | Specify either `RelatedTransactionId__std` or `BillingScheduleGroupId__std` in your request if you’re sending a simplified payload. |
| `BillingScheduleGroupId__std` | ID of the billing schedule group that must be referenced ‌to renew each billing schedule in the billing schedule group early. | Not applicable. | Specify either `RelatedTransactionId__std` or `BillingScheduleGroupId__std` in your request if you’re sending a simplified payload. |
| `BillingActionType__std` | The action that you want to perform for the transaction.  Specify `Renew` as the BillingActionType for early renewal transactions. | Category field on the BillingSchedule object is populated as Renewal. | Required |
| `BillingSubActionType__std` | The sub-action that you want to perform for the transaction.  Specify `AsIsRenewal` as the BillingActionType to specify minimal details in the payload for an as-is renewal. Specify `SimplifiedRenewal` as the BillingActionType to specify minimal details in the payload for a renewal or an early renewal. Available in API version 67.0 and later. | SubCategory field on the BillingSchedule object | Optional |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
