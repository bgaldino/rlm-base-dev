---
page_id: actions_obj_deep_clone_sales_transaction.htm
title: Deep Clone Sales Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_deep_clone_sales_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Deep Clone Sales Transaction

Clone a quote or an order, including full object graph with related
objects, selected lines, or selected groups.

This action is available in API version 67.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/deepCloneSalesTransaction`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer token`

## Inputs

| Input | Details |
| --- | --- |
| options | Type  Apex-defined  Description  Specifies options to clone a ramp segment within a sales transaction. You can clone only the last ramp segment. Valid values are:   - `recordTypeId`—ID of the record type related to   the record to clone. Optional. - `lineScope`—Specifies the scope for cloning a   ramp segment. This property determines which line   items must be cloned and added to the cloned   segment. You can specify these options.   - `AllLines`—Specifies whether all line     items in a ramped group must be cloned.   - `RampedLinesOnly`—Specifies whether only     the ramped line items must be cloned. A segment identifier is created for the   newly cloned line items, ensuring date continuity   between the existing and cloned segment. |
| recordIds | Type  List<String>  Description  Required.  ID of the record to be cloned. You can specify a single record ID only. |
| salesTransactionId | Type  String  Description  Required.  ID of the sales transaction related to the record IDs to clone. |

## Outputs

| Output | Details |
| --- | --- |
| newRecordId | Type  String  Description  ID of the cloned sales transaction. |

## Example

POST
:   Here’s a sample request for the Deep Clone Sales Transaction action.

    ```
    {
      "inputs": [
        {
          "recordIds": ["0QLxx0000004CBYGA2"],
          "salesTransactionId": "0Q0xx0000004CE0CAM",
          "options": {
            "lineScope": "AllLines"
          }
        }
      ]
    }
    ```
:   Here’s a sample response for the Deep Clone Sales Transaction action.

    ```
    {
      "actionName": "deepCloneSalesTransaction",
      "errors": null,
      "isSuccess": true,
      "outputValues": {
        "newRecordId": "0Q0SG000000ACxf0AG"
      }
    }
    ```
