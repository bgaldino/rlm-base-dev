---
page_id: dt_actions_run_decision_table.htm
title: Decision Table Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/dt_actions_run_decision_table.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: dt_actions_parent.htm
fetched_at: 2026-06-25
---

# Decision Table Actions

Invoke a decision table.

Decision tables provide outcomes based on your business rules. For more information about
invoking decision tables, see [Invoke a Decision Table](https://help.salesforce.com/articleView?id=concept_decision_table_run.htm&language=en_US) in Salesforce Help.

This object is available in API version 51.0 and later.

## Supported REST HTTP Methods

Formats
:   JSON

HTTP Methods
:   GET, POST

Authentication
:   `Authorization: Bearer
    token`

The specific URI endpoint and the structure
of the JSON payload depend on whether a dataset link is configured for your decision table. To
check if a dataset link is enabled for your decision table, you can query the
DecisionTableDataLink table. If an entry for your decision table exists in this table, a dataset
link is active. For more information about dataset links, see [DecisionTableDatasetLink](https://developer.salesforce.com/docs/atlas.en-us.262.0.psc_api.meta/psc_api/tooling_api_objects_decisiontabledatasetlink.htm).

## Decision Table Without Dataset Link

If your `decisionTableId` isn't found in the `DecisionTableDatasetLink` table, you must append `_Default` to your decision table's API name to construct the endpoint URI.

URI without dataset link
:   `/services/data/vXX.X/actions/custom/decisionTableAction/dtapi_Default`

## Decision Table With Dataset Link

If your decisionTableId is present in the
DecisionTableDatasetLink table, the endpoint URI uses the API name of the dataset link.

URI with dataset link
:   `/services/data/vXX.X/actions/custom/decisionTableAction/dslapiname`

## Inputs

You can choose to invoke a decision table with or without dataset link.

To execute a default Decision Table without dataset link, specify the input fields that were
defined at the time of the Decision Table creation in the flow. The input fields are optional.
However, you must specify at least one field as the input parameter. Use the GET method to
retrieve input parameters of a Decision Table definition.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

For example, to decide discount
percentage for products, you can pass the input parameters, including Brand\_\_c,
Highest\_Price\_Point\_c, and Lowest\_Price\_Point\_c.

To execute a Decision Table with dataset link, specify the list that contains the source
object and its corresponding field to be used in the dataset link that is associated with the
decision table.

| Input | Details |
| --- | --- |
| sObjectType | Type  sObject  Description  The name of the dataset link’s object whose records, the decision table must provide an outcome for. |

## Outputs

| Output | Details |
| --- | --- |
| outcomeList | Type  sObject  Description  Outcome list that stores two or more outcomes provided by the decision table. Note Note A decision table that is invoked by the Decision Table custom invocable action can provide up to 50 outcomes. |
| outcomeType | Type  string  Description  Indicates the type of outcome provided by the decision table after the request is successful. Valid values are:  - `Multiple Match—Outcome returns multiple   matches.` - `No Match`—Outcome returns no match. - `Single Match`—Outcome returns single   match. |
| singleOutcome | Type  sObject  Description  Stores the outcome in case a single outcome is provided by the decision table. In case multiple outcomes are provided, it stores one of the outcomes. |

## Usage

**JSON Sample Request without dataset link**

When you invoke a decisionTableAction without a dataset link, the request contains an array of
input objects.

```
{
   "inputs" : [
      {
        "Product__c": "Cloud Kicks",
        "Price__c": 1000
      }
   ]
}
```

**JSON Sample Request with dataset Link**

When you invoke a decisionTableAction
with a dataset link, the input objects in the request are nested within another object, which is
typically the name of the transaction object.

```
{
   "inputs" : [
      {
         "Transaction__c" : {
            "Product__c": "Cloud Kicks",
            "Price__c": 1000
         }
      }
   ]
}
```

**JSON Sample Request with dataset Link containing multiple source objects**

```
{
   "inputs" : [
      {
         "Transaction__c" : {
            "Product__c": "Cloud Kicks",
            "Price__c": 1000
         }
      }
      {
         "Catalog__c" : {
            "name": "Highest_Price_Point_c",
            "value": "500",
         }
      }
   ]
}
```

**JSON Sample Response**

```
[{
   “outcomeType” : “SINGLE MATCH”,
   “singleOutcome”: { “Points”: 100 },
   "outcomeList" : [
      {
         “Points”: 100
      }
   ]
}]
```
