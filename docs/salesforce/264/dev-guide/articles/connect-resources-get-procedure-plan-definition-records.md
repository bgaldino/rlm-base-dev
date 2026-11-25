---
page_id: connect-resources-get-procedure-plan-definition-records
title: Procedure Plan Definitions (GET, POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-procedure-plan-definition-records.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_get_procedure_plan_definition_records.htm
fetched_at: 2026-11-25
---

# Procedure Plan Definitions (GET, POST)

Get the records of procedure plan definitions. Additionally, create a record of a procedure plan definition.

## Resource

```
/connect/procedure-plan-definitions
```

## Resource Example

```
https://{yourInstance}.salesforce.com​/services/data​/v68.0/connect/​procedure-plan-definitions?​isTemplate=true
```

## Available Version

62.0

## HTTP Methods

GET, POST

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isTemplate` | Boolean | Indicates whether to return a list of file-based definitions (`true`) or not (`false`). This API request returns a list of database-based definitions, by default. | Optional | 62.0 |

## Response Body for GET

[Procedure Plan Definitions](./connect-responses-procedure-plan-definitions-output.md)

## Request Body for POST

**JSON Example**

This example shows a sample request to create a procedure plan definition record by using the Procedure Plan Definitions (POST) API.

```
  {
  "description": "Definition for Quote",
  "developerName": "Quote_Definition_Sample",
  "name": "Quote_Definition_Sample",
  "processType": "Default",
  "primaryObject": "BusinessHours",
  "procedurePlanDefinitionVersions": [
    {
      "active": false,
      "contextDefinition": "SalesTransactionContext__stdctx",
      "readContextMapping": "QuoteEntitiesMapping",
      "saveContextMapping": "QuoteEntitiesMapping",
      "effectiveFrom": "2024-07-15T10:15:30.000Z",
      "developerName": "Quote_Definition_V1",
      "rank": 1
    }
  ]
}
```

## Response Body for POST

[Procedure Plan Generic](./connect-responses-procedure-plan-generic-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-procedure-plan-definition-records.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
