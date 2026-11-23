---
page_id: actions_obj_deep_clone_sales_transaction.htm
title: Deep Clone Sales Transaction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_deep_clone_sales_transaction.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Deep Clone Sales Transaction

Clone a quote or an order, including full object graph with related objects, selected lines, or selected groups.

This action is available in API version 67.0 and later.

## Supported REST HTTP Methods

**URI:**`/services/data/v68.0/actions/standard/deepCloneSalesTransaction`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:**`Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| options | Apex-defined | Specifies options to clone a ramp segment within a sales transaction. You can clone only the last ramp segment. Valid values are `recordTypeId`—ID of the record type related to the record to clone. Optional; or `lineScope`—Specifies the scope for cloning a ramp segment. This property determines which line items must be cloned and added to the cloned segment. You can specify these options: `AllLines`—Specifies whether all line items in a ramped group must be cloned, or `RampedLinesOnly`—Specifies whether only the ramped line items must be cloned. A segment identifier is created for the newly cloned line items, ensuring date continuity between the existing and cloned segment. |
| recordIds | List<String> | Required. ID of the record to be cloned. You can specify a single record ID only. |
| salesTransactionId | String | Required. ID of the sales transaction related to the record IDs to clone. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| newRecordId | String | ID of the cloned sales transaction. |

## Example

**POST**

Here’s a sample request for the Deep Clone Sales Transaction action.

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

Here’s a sample response for the Deep Clone Sales Transaction action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_deep_clone_sales_transaction.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
