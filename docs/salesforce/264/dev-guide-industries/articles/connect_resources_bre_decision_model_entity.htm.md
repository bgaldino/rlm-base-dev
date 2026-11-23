---
page_id: connect_resources_bre_decision_model_entity.htm
title: Decision Model Notation Export (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_model_entity.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-11-23
---

# Decision Model Notation Export (POST)

Export decision matrix data to a file in the DMN (Decision Model
Notation) format, an easily readable format for business rules designed by Object Management
Group.

## Resource

```
/connect/business-rules/decision-models/export
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/decision-models/export
```

## Available Version

58.0

## Requires Chatter

No

## HTTP Methods

POST

#### See Also

- [DMN (Decision Model Notation)](https://www.omg.org/dmn/#:~:text=DMN%20is%20a%20modeling%20language,monitor%20their%20application%3B%20business%20analysts. "DMN (Decision Model Notation) - HTML (New Window)")

## Request Body for POST

### JSON Example

```
{
   "decisionModelEntityIds":[
      “0lNRO00000004f72AA”,
      “0lNRO000000rfn27AA”
   ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `decision​Model​EntityIds` | String[] | A list of decision matrix version IDs to export data from. | Required | 58.0 |

## Response Body for POST

[Decision Model Export Output](./connect_responses_decision_model_export_output.htm.md "Output representation of a completed DMN (Decision Model Notation) export request.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_model_entity.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
