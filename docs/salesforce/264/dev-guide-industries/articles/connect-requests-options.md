---
page_id: connect-requests-options
title: Expression Set Options Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-options.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-requests
legacy_page_id: connect_requests_options.htm
fetched_at: 2026-11-25
---

# Expression Set Options Input

Input representation of the options for executing an expression set.

## JSON Example

```
{
  "inputs": [
    {
      "age": "25",
      "state": "CA",
      "PatientId": "001xx000003GYjnAAG"
    }
  ],
  "options": {
    "effectiveDate": "2022-12-03T10:15:30Z",
    "useDatesOnly": "true",
    "actionContextCode": "9QLxx0000004C92GAE",
    "explainabilitySpecName": "ES_One_Explainability"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `actionContext​Code` | String | The code of the action context used to log explainability for a specific execution of an expression set. Note: To exclude decision explanations for expression set version steps from action logs, ensure that you exclude the `actionContextCode` and `explainabilitySpecName` properties from the payload. | Optional | 55.0 |
| `effectiveDate` | String | The date from which an expression set comes into effect. The date format is yyyy-mm-dd’T’hh:mm:ss’Z. Note: Multiple versions of an expression set can exist with different date ranges. For example, Version 1 is effective before December 2019, and Version 2 is effective from January 2020 to the present. If you specify `effectiveDate` as “2019-03-15T00:00:00Z”, Version 1 is executed. If you do not specify `effectiveDate`, the currently active version, Version 2, is executed. | Optional | 55.0 |
| `explainability​Spec​Name` | String | The name of the explainability specification that is used to log explainability for a specific execution of an expression set. Note: To exclude decision explanations for expression set version steps from action logs, ensure that you exclude the `actionContextCode` and `explainabilitySpecName` properties from the payload. | Optional | 55.0 |
| `useDatesOnly` | String | Specifies that only the date portion (yyyy-mm-dd) of the value of effectiveDate field is to be used at the time of execution. | Optional | 55.0 |
| `versionNumber` | String | The version number of the expression set version record. | Optional | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-options.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
