---
page_id: connect-resources-rules-engine-message-templates-list
title: Explainability Message Templates (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-message-templates-list.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-explainer-bre-resources
legacy_page_id: connect_resources_rules_engine_message_templates_list.htm
fetched_at: 2026-11-25
---

# Explainability Message Templates (GET)

Retrieves a list of explainability message templates that matches the given search parameters.

## Resource

```
/connect/business-rules/explainability/message-templates
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect
/business-rules/explainability/message-templates?messageType=Passed
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

56.0

## Requires Chatter

No

## HTTP Methods

GET

## Request Parameters for GET

**Note:**

You must specify at least one parameter as part of the GET request.

- 
- 
- 
- 
- 
- 
- 
- 

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isDefault` | Boolean | Specifies whether the message in the explainability message template for an expression set step type is default (`true`) or not (`false`). | Optional | 56.0 |
| `messageType` | String | The message defined for a step when the step result is either passed or failed. | Optional | 56.0 |
| `searchKey` | String | The keyword used to retrieve the list of templates. | Optional | 56.0 |
| `stepType` | String | The type of expression set step element. Pass one of these values for this field: CalculationBranchConditionDecision Matrix LookupDecision Table LookupAggregationSub ExpressionBusiness Element | Optional | 56.0 |

## Response Body for GET

[Message Templates List](./connect-responses-message-templates-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-message-templates-list.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
