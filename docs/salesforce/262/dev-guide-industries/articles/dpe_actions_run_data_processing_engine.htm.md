---
page_id: dpe_actions_run_data_processing_engine.htm
title: Data Processing Engine Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/dpe_actions_run_data_processing_engine.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: dpe_actions_parent.htm
fetched_at: 2026-06-25
---

# Data Processing Engine Actions

Run an active Data Processing Engine definition. This action executes a
Data Processing Engine definition asynchronously.

A Data Processing Engine definition transforms data from your Salesforce org and writes back
the results to your org. For more information about running Data Processing Engine definitions,
see [Run a Data Processing Engine Definition](https://help.salesforce.com/articleView?id=task_data_processing_engine_run.htm&language=en_US) in Salesforce
Help.

This object is available in API version 51.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/vXX.X/actions/custom/dataProcessingEngineAction`

Formats
:   JSON

HTTP Methods
:   GET, POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

Use the GET method to retrieve input variables of a Data Processing Engine definition. The
input variables of each Data Processing Engine definition are unique. The Data Processing Engine
action uses the input variables to execute the Data Processing Engine definition and generate a
batch job ID.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

You can't use this action to start two simultaneous runs of a definition with the same
input variables.

## Outputs

| Output | Details |
| --- | --- |
| batchJobId | Type  string  Description  ID of the batch job generated after the request is successful. This ID is used to track the progress of the batch job in Monitor Workflow Services. |

## Usage

**JSON Sample Request to execute PointsAccrual DPE Definition**

```
{
   "PointsAccrual" : {
      "memberTier" : "Gold",
      "minimumPointBalanceRequired" : "50000",
      "pointType" : "non-qualifying"
   }
}
```

**JSON Sample Response**

```
{
   "actionName":"PointsAccrual",
      "errors":null,
      "isSuccess":true,
      "outputValues":{ 
        "batchJobId":"0lMxx0000A000001EAA"
      }
}
```

## Example

GET
:   This example shows how to retrieve input variables of a Data Processing Engine action
    type.

    ```
    curl --include --request GET \
    --header "Authorization: Authorization: Bearer 00DR...xyz" \
    --header "Content-Type: application/json" \
    "https://instance.salesforce.com/services/data/v60.0/actions/custom/dataProcessingEngineAction/newinputvardefn"
    ```

POST
:   Here’s a request to retrieve DPE definition

    ```
    {
      "inputs": [
        {
          "start_date": "26-09-2023",
          "end_date": "12-12-2023",
          "randomkey": "069SM0000001SgbYAE"
        }
      ]
    }
    ```

    Here’s a response for this action.

    ```
    [
      {
        "actionName": "newinputvardefn",
        "errors": null,
        "invocationID": null,
        "isSuccess": true,
        "outputValues": {
          "batchJobId": "0mdSM0000006EJdYAM",
          "accepted": true
        },
        "version": 1
      }
    ]
    ```
