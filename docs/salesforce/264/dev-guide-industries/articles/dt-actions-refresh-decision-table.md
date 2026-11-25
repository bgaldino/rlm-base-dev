---
page_id: dt-actions-refresh-decision-table
title: Decision Table Refresh Action
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/dt-actions-refresh-decision-table.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: dt-actions-parent
legacy_page_id: dt_actions_refresh_decision_table.htm
fetched_at: 2026-11-25
---

# Decision Table Refresh Action

Refresh business rules for an active decision table.

For more information about refreshing an active decision table, see [Refresh Decision Tables in Flows](https://help.salesforce.com/articleView?id=task_refresh_decision_table_flow.htm) in Salesforce Help. This object is available in API version 51.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/standard/refreshDecisionTable`

Where `XX.X` is the latest API version.

**Formats:** JSON

**HTTP Methods:** GET, POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `decisionTable​ApiName` | string | Required. API name of an active decision table that you want to refresh. |
| `isDecisionTable​Incremental` | boolean | Specifies whether to trigger an incremental refresh (`true`) or not (`false`). If set to true, this field triggers an update only on changes made to the recent sObject data instead of performing a full refresh. The default value is `false`. This feature requires a full refresh to be performed initially. After a full refresh is done, you can proceed with incremental refreshes. However, if the changes exceed 2,000 records, the incremental refresh fails. In such cases, a full refresh is necessary to update the Decision Table with the latest sObject data. An incremental refresh updates `LastIncrementalSyncDate` only. A full refresh updates `LastRefreshedDate` and `LastSyncDate`. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `errorMessage` | string | Error message to indicate why the request wasn’t successful. |
| `status` | string | Indicates whether the decision table is queued for refresh. Valid values are `Queued` or `Failed`. |

## Usage

**Sample Request**

```
{
  "inputs": [
    {
      "decisionTableApiName": "Points_to_Redeem_Based_on_Product_and_Order_Channel",
      "isDecisionTableIncremental": true
    }
  ]
}
```

**Sample Response**

```
{
   "status":"Queued",//Queued or Failed
   "errorMessage":"" //in case any failure
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/dt-actions-refresh-decision-table.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
