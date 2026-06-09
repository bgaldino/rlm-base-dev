---
page_id: connect_requests_billing_schedule_input_for_cancellation.htm
title: Canceled Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_billing_schedule_input_for_cancellation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: connect_requests_context_aware_standalone_billing_schedule_input.htm
fetched_at: 2026-06-09
---

# Canceled Transaction

Cancel an entire billing schedule from a specified date. Specify only the cancellation
date and billing schedule group identifier. The API computes the logic to split the cancellation
across overlapping billing schedules and creates one cancel transaction per segment.

## Considerations

Keep these important considerations in mind when you provide the details for canceled
transactions.

- The `BillingActionType__std` value for any amended
  transaction must be `Cancel`.
- If you provide a quantity, make sure that it matches the total quantity of the related
  transaction.
- If there are multiple canceled transactions associated with the same related
  transaction, specify the same start date for all of these transactions.
- Specify the canceled transaction details for all the billing schedules that are
  associated with the same billing schedule group.
- If your transaction is for an sObject record, only specify the record ID as the id value
  in the `transactionDetails` property value. All the
  other transaction details are automatically fetched from the sObject record if those
  details are mapped in the context definition.

## Cancellation Payload Types

The Create Standalone Billing Schedules API accepts two cancellation payload types in
`transactionDetails` node. Use the type that matches
the level of details you want to provide in the request.

Simplified cancellation payload
:   Send a single transaction in the `Transaction` array. Set `BillingActionType__std` to `Cancel` and
    `BillingSubActionType__std` to `SimplifiedCancel`. Identify the source to cancel with
    `RelatedTransactionId__std` (one billing
    schedule) or `BillingScheduleGroupId__std` (a
    billing schedule group), and include `TransactionId__std` and `StartDate__std`
    for the effective cancellation date.

    This sample shows the transaction data with
    `BillingScheduleGroupId__std` to cancel a billing
    schedule group.

    ```
    {
      "Transaction": [
        {
          "TransactionId__std": "cTer5",
          "BillingScheduleGroupId__std": "9Wsxx000000009hCAA",
          "StartDate__std": "2026-08-01",
          "BillingActionType__std": "Cancel",
          "BillingSubActionType__std": "SimplifiedCancel"
        }
      ]
    }
    ```

    This sample shows a simplified cancellation
    request.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"cTer5\",\"BillingScheduleGroupId__std\":\"9Wsxx000000009hCAA\",\"StartDate__std\":\"2026-08-01\",\"BillingActionType__std\":\"Cancel\",\"BillingSubActionType__std\":\"SimplifiedCancel\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

    This sample shows the transaction data with `RelatedTransactionId__std` to cancel a billing
    schedule.

    ```
    {
      "Transaction": [
        {
          "TransactionId__std": "ter4",
          "RelatedTransactionId__std": "evg1",
          "StartDate__std": "2026-02-01",
          "BillingActionType__std": "Cancel",
          "BillingSubActionType__std": "SimplifiedCancel"
        }
      ]
    }
    ```

    This sample shows a simplified cancellation
    request.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"TransactionId__std\":\"ter4\",\"RelatedTransactionId__std\": \"evg1\",\"StartDate__std\":\"2026-02-01\",\"BillingActionType__std\": \"Cancel\",\"BillingSubActionType__std\":\"SimplifiedCancel\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

Detailed cancellation payload
:   Send one cancel transaction for each positive billing schedule that you want to end.
    Each transaction uses `BillingActionType__std` set
    to `Cancel`. You specify `RelatedTransactionId__std` and the financial fields,
    such as quantity, unit price, and total price, for each line. Use this sample
    structure when you already computed the cancel lines and amounts yourself.

    This sample shows a detailed cancellation for a single billing schedule. It uses a
    compact set of fields and does not use `SimplifiedCancel` sub-action type. For a detailed cancellation with
    multiple transactions, see the following sample.

    This sample includes the transaction data for a cancellation.

    ```
    {
      "Transaction": [
        {
          "id": "termedCancel1",
          "ParentTransactionId__std": "sample",
          "TransactionId__std": "termedCancel1",
          "RelatedTransactionId__std": "ot1",
          "StartDate__std": "2025-03-01",
          "UnitPrice__std": 10,
          "TotalPrice__std": -50,
          "BillingActionType__std": "Cancel"
        }
      ]
    }
    ```

    This sample shows the request payload to create a billing schedule for a
    cancellation.

    ```
    {
      "transactionDetails": "{\"Transaction\":[{\"id\":\"termedCancel1\",\"ParentTransactionId__std\":\"sample\",\"TransactionId__std\":\"termedCancel1\",\"RelatedTransactionId__std\":\"ot1\",\"StartDate__std\":\"2025-03-01\",\"UnitPrice__std\":10,\"TotalPrice__std\":-50,\"BillingActionType__std\":\"Cancel\"}]}",
      "transactionContextDetails": {
        "contextDefinitionName": "StandaloneBillingContext__stdctx",
        "intraContextCustomMappingName": "CustomContextMapping",
        "readContextMappingName": "TransactionMapping",
        "saveContextMappingName": "BSGEntitiesMapping"
      }
    }
    ```

When you're creating a billing schedule for a canceled transaction, make sure that you
specify the mandatory values in the `transactionDetails`
property value.

| Context Tag in the Transaction Node of the StandaloneBillingContext Context Definition | Description | Mapped Field | Required or Optional |
| --- | --- | --- | --- |
| `ParentTransactionId__std` | The ID of the parent transaction record. For example, if the transaction is at a level similar to that of an Order Item record, the parent transaction will be at a level similar to that of an Order record. | If the transaction is a child Order or Quote record, the ReferenceEntityId field on the BillingScheduleobject is populated. For other sObject records or external records, the Reference field on the BillingSchedule object is populated. | Optional |
| `TransactionId__std` | The unique identifier reference to apply to the canceled billing schedule. The Reference and ReferenceItem field on a billing schedule has this value appended with a unique ID generated string. | If the transaction is an OrderItem, OrderItemAdjustmentLineItem, OrderItemDetail, QuoteLineDetail, or QuoteLineItem record, the ReferenceEntityItemId field on the BillingScheduleobject is populated. For other sObject records or external records, the ReferenceItem field on the BillingSchedule object is populated. | Optional if you’re sending a simplified payload. If you don’t specify this value, the API creates unique transaction IDs. |
| `StartDate__std` | The start date of the transaction. | BillingScheduleStartDate field on the BillingSchedule object | Required |
| `RelatedTransactionId__std` | The ID of the related transaction that must be referenced to cancel one billing schedule. | This value isn't populated on any BillingSchedule or BillingScheduleGroup field. | Required |
| `BillingScheduleGroupId__std` | ID of the billing schedule group that must be referenced ‌to cancel the billing schedule group. | Not applicable. | Specify either `RelatedTransactionId__std` or `BillingScheduleGroupId__std` in your request if you’re sending a simplified payload. |
| `BillingActionType__std` | The action that you want to perform for the transaction.  Specify `Cancel` as the BillingActionType for canceled transactions. | Category field on the BillingSchedule object is populated as Cancellation. | Required |
| `BillingSubActionType__std` | The sub-action that you want to perform for the transaction.  Specify `SimplifiedCancel` as the BillingActionType to specify minimal details in the payload for canceled transactions. Available in API version 67.0 and later. | SubCategory field on the BillingSchedule object | Optional |
| `UnitPrice__std` | The unit price of the transaction. | UnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
| `TotalPrice__std` | The total price of the transaction. | TotalAmount field on the BillingSchedule object | Required |
| `NetUnitPrice__std` | The net unit price of the transaction. | NetUnitPrice field on the BillingSchedule object | Either the UnitPrice or the NetUnitPrice value is required |
