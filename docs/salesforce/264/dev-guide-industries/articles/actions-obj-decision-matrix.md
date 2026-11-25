---
page_id: actions-obj-decision-matrix
title: Decision Matrix Actions
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-decision-matrix.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: lookup-tables-invocable-actions
legacy_page_id: actions_obj_decision_matrix.htm
fetched_at: 2026-11-25
---

# Decision Matrix Actions

Invoke a decision matrix in a flow with the Decision Matrix Actions. A decision matrix is a user-defined table where you can look up an output based on the inputs you provide.

For example, you can look up a candidate’s eligibility to avail medical insurance in a decision matrix based on the candidate’s age and gender.

These actions are available in API version 55.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/custom/runDecisionMatrix/{UniqueName}`

Where `XX.X` is the latest API version.

**Note:**

The value of UniqueName is the unique identifier of the record, which is sourced from the name of a decision matrix.

**Formats:** JSON

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

Vary depending on the selected decision matrix.

## Outputs

Vary depending on the inputs of the selected decision matrix.

## Usage

**Sample Request**

: 

Here’s an example POST request that has the inputs, such as, age and state:

```
{
   "inputs":[
      {
         "age":"25",
         "state":"NY"
      },
      {
         "age":"25",
         "state":"CA"
      },
      {
         "age":"",
         "state":"WA"
      }
   ]
}
```

**Sample Response**

: 

Here’s an example response that has the premium and tax values based on the inputs provided in the example request.

```
[
   {
      "actionName":"premiumTaxLookup",
      "errors":null,
      "isSuccess":true,
      "outputValues":{
         "premium":2400.0,
         "tax":200.0
      }
   },
   {
      "actionName":"premiumTaxLookup",
      "errors":null,
      "isSuccess":true,
      "outputValues":{
         "premium":2400.0,
         "tax":200.0
      }
   },
   {
      "actionName":"premiumTaxLookup",
      "errors":[
         {
            "statusCode":"REQUIRED_FIELD_MISSING",
            "message":"Missing required input parameter: age",
            "fields":[
            ]
         }
      ],
      "isSuccess":false,
      "outputValues":null
   }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-decision-matrix.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
