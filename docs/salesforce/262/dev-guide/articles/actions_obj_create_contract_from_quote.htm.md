---
page_id: actions_obj_create_contract_from_quote.htm
title: Create Contract Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_create_contract_from_quote.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Create Contract Action

Create a contract from a specific quote record.

This action is available in API version 60.0 and later.

## Special Access Rules

The Create Contract action is available in Developer, Enterprise, and Unlimited Editions of
Revenue Cloud.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/createContract`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| contractPriceOption | Type  string  Description  Optional.  Determines how the contract price is set for quote line items based on the selected value. Valid values are:  - `CONTRACT_HEADER_ONLY`—Creates a   contract with only the header information, without   using net prices or discounts. - `NET_UNIT_PRICE_ONLY`—Creates a   contract specifically for quote line items with a   net unit price, saving all net unit prices of the   quote as contract prices. - `DISCOUNT_ONLY`—Creates contract   prices specifically for quote line items with   discounts, saving all discounts of the quote as   contract prices.  The default value is `CONTRACT_HEADER_ONLY`. |
| sourceId | Type  string  Description  Required.  ID of the quote or order that you want to create a contract from. |

## Outputs

| Output | Details |
| --- | --- |
| contractId | Type  string  Description  ID of the contract created for the specified order or quote. |

## Example

POST
:   This sample request is for the Create Contract action.

    ```
    {
      "inputs": [
        {
          "sourceId": "0Q0RO0000003LyU",
          "contractPriceOption": "NET_UNIT_PRICE_ONLY"
        }
      ]
    }
    ```

    This sample response is for the Create Contract action.

    ```
    [
      {
        "actionName": "createContract",
        "errors": null,
        "isSuccess": true,
        "outputValues": {
          "contractId": "800XXX123456789"
        }
      }
    ]
    ```

#### See Also

- [*Salesforce Help*: Use a Custom Flow to Create Contracts](https://help.salesforce.com/s/articleView?id=ind.qocal_create_contracts_using_a_flow.htm&type=5&language=en_US "Salesforce Help: Use a Custom Flow to Create Contracts - HTML (New Window)")
