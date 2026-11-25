---
page_id: connect-requests-procedure-plan-definition-input
title: Procedure Plan Definition Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-definition-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_procedure_plan_definition_input.htm
fetched_at: 2026-11-25
---

# Procedure Plan Definition Input

Input representation of the details of a procedure plan definition.

## JSON Example

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

This example shows a sample request to update a procedure plan definition by using the Procedure Plan Definition By ID (PATCH) API.

**Note:** The properties that aren’t specified in the input are deleted when updating the record.

```
{
  "description": "Default definition patch update",
  "developerName": "Quote_Definition",
  "name": "Quote_Definition",
  "primaryObject": "Quote",
  "recordId": "1FNxx0000004EsOGAU"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description of the procedure plan definition. | Optional | 62.0 |
| `developer​Name` | String | Developer name of the procedure plan definition. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](./connect-resources-get-procedure-plan-definition-records.md). | 62.0 |
| `name` | String | Name of the procedure plan definition. | Optional | 62.0 |
| `primary​Object` | String | Source object that’s used to create a procedure with rule-based criteria. This property value must be a valid object name and must be unique in the ProcedurePlanDefinition object. | Required if you’re invoking the [Procedure Plan Definitions API (POST)](./connect-resources-get-procedure-plan-definition-records.md) and if you’re creating a procedure with rule-based criteria. | 62.0 |
| `procedurePlan​Definition​Versions` | [Procedure Plan Definition Version Input](./connect-requests-procedure-plan-definition-version-input.md)[] | List of versions of a procedure plan definition. | Required | 62.0 |
| `processType` | String | Specifies the business processes that need a procedure plan for each sObject and definition. Valid values are `Billing`, `DRO`, `DeepClone`, `ProductDiscovery`, or `Revenue Cloud`. These values can be used based on the available license. If unspecified, the value is set to `Default`. | Required | 63.0 |
| `recordId` | String | ID of the procedure plan definition record. | Required if you’re invoking the [Procedure Plan Definition By ID API (PATCH)](./connect-resources-get-procedure-plan-definition-by-id.md). | 62.0 |
| `subType` | String | Specifies the vertical or cloud-specific subclassification for the procedure plan definition. | Optional | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-procedure-plan-definition-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
