---
page_id: dt_actions_refresh_decision_table.htm
title: Decision Table Refresh Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/dt_actions_refresh_decision_table.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_actions_parent.htm
fetched_at: 2026-06-25
---

# Decision Table Refresh Action

Refresh business rules for an active decision table.

For more information about refreshing an active decision table, see [Refresh Decision Tables in Flows](https://help.salesforce.com/articleView?id=task_refresh_decision_table_flow.htm&language=en_US) in Salesforce Help. This
object is available in API version 51.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/vXX.X/actions/standard/refreshDecisionTable`

Formats
:   JSON

HTTP Methods
:   GET, POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| decisionTable​ApiName | Type  string  Description  Required. API name of an active decision table that you want to refresh. |
| isDecisionTable​Incremental | Type  boolean  Description  Specifies whether to trigger an incremental refresh (`true`) or not (`false`). If set to true, this field triggers an update only on changes made to the recent sObject data instead of performing a full refresh. The default value is `false`.  This feature requires a full refresh to be performed initially. After a full refresh is done, you can proceed with incremental refreshes. However, if the changes exceed 2,000 records, the incremental refresh fails. In such cases, a full refresh is necessary to update the Decision Table with the latest sObject data.  An incremental refresh updates `LastIncrementalSyncDate` only. A full refresh updates `LastRefreshedDate` and `LastSyncDate`. |

## Outputs

| Output | Details |
| --- | --- |
| errorMessage | Type  string  Description  Error message to indicate why the request wasn't successful. |
| status | Type  string  Description  Indicates whether the decision table is queued for refresh. Valid values are `Queued` or `Failed`. |

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
