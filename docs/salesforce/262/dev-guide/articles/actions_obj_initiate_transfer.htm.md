---
page_id: actions_obj_initiate_transfer.htm
title: Initiate Transfer Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_initiate_transfer.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Initiate Transfer Action

Transfer an asset or multiple assets from one account to
another.

Keep these considerations in mind when you use this invocable action.

- This action generates 2 quotes or 2 orders.
- One transaction is considered the source, which is used to calculate the
  reduction amount of the transfer. The other transaction is the target, which is
  used to calculate the new amount on the target account.
- The quantity on the source is negative, which reduces the existing asset's
  quantity. The quantity on the target is positive, which creates a new asset on
  the target account.
- You can change the quantity on the source or the target, but the quantities must
  be equal and opposite. For example, the source quote line can have a quantity
  value as `-5`, and the target quote line can
  have a quantity value `5`. If you change the
  source value to `-10`, you must update the
  target value to `10`. You must update quotes
  or orders manually.
- The transfer is complete after the orders are assetized.

This action is available in API version 65.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/initiateTransfer`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| outputRecordType | Type  string  Description  Required. Specifies either a quote or order record type that’s being transferred. |
| shouldSkipPricing | Type  boolean  Description  Indicates whether to skip pricing at the time of asset transfer (`true`) or not (`false`). |
| targetAccountId | Type  string  Description  Required. The ID of the target account where the asset is transferred. |
| targetContractId | Type  string  Description  The ID of the target contract that’s associated with the asset that’s being transferred. |
| transferDate | Type  datetime  Description  Required. The date of the asset transfer. |
| transferRecords | Type  Apex-defined  Description  Required. A collection of Apex `connectapi__TransferRecordInputRepresentation` records that contain details about the assets to be transferred. See [ConnectApi.TransferRecordInputRepresentation](./apex_connectapi_input_transfer_record.htm.md "Input representation of the details of the assets to be transferred."). |

## Outputs

| Output | Details |
| --- | --- |
| assetTransferSourceId | Type  id  Description  The ID of the quote or order that’s related to the source account used to start the transfer. |
| assetTransferTargetId | Type  id  Description  The ID of the quote or order that’s related to the target account used to start the transfer. |
| requestIdentifier | Type  id  Description  The request ID can be used to track the async request. |

## Example

POST
:   Here's a sample input to call this invocable action.

    ```
    {
      "inputs": [
        {
          "transferRecords": [
            {
              "assetId": "02ixx0000004HZbAAM",
              "transferQuantity": 1
            }
          ],
          "transferDate": "2025-10-21T00:00:00.000Z",
          "targetAccountId": "001xx000003GbeXAAS",
          "targetContractId": "800DU0000000lZlYAI",
          "outputRecordType": "Quote"
        }
      ]
    }
    ```
:   Here's a sample input to call this invocable action from Apex code.

    ```
    ConnectApi.TransferRecordInputRepresentation transferRecord = new ConnectApi.TransferRecordInputRepresentation();
    transferRecord.assetId = '02ixx0000004HHjAAM';
    transferRecord.transferQuantity = 1;
    List<ConnectApi.TransferRecordInputRepresentation> transferRecords = new List<ConnectApi.TransferRecordInputRepresentation>();
    transferRecords.add(transferRecord);

    Invocable.Action action = Invocable.Action.createStandardAction('initiateTransfer');
    action.setInvocationParameter('transferRecords', transferRecords);
    action.setInvocationParameter('targetAccountId', '001xx000003GYiHAAW');
    action.setInvocationParameter('transferDate', '2025-03-01T00:00:00.000Z');
    action.setInvocationParameter('outputRecordType', 'Quote');
    List<Invocable.Action.Result> results = action.invoke();
    System.assertEquals(true, results[0].isSuccess());
    Assert.isNotNull(results[0].getOutputParameters().get('assetTransferSourceId'));
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "initiateTransfer",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "assetTransferSourceId": "0Q0DU0000006SYF0A2",
          "assetTransferTargetId": "0Q0DU0000006SYE0A2"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
