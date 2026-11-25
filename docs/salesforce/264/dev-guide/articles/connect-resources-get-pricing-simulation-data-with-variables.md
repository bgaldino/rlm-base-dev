---
page_id: connect-resources-get-pricing-simulation-data-with-variables
title: Pricing Simulation Input Variables With Data (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-pricing-simulation-data-with-variables.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_get_pricing_simulation_data_with_variables.htm
fetched_at: 2026-11-25
---

# Pricing Simulation Input Variables With Data (GET)

Get details of the pricing simulation input variables along with associated data.

## Resource

```
/connect/core-pricing/simulationInputVariablesWithData
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/simulationInputVariablesWithData?expressionSetVersionId={9QMxx0000004CDsGAM}&entityId={0Q0xx0000004C92CAE}&contextDefinitionId={SalesTransactionContext__stdctx}&contextMappingId={QuoteEntitiesMapping}
```

## Available Version

64.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `context​DefinitionId` | String | ID or developer name of the context definition. | Required | 64.0 |
| `contextMapping​Id` | String | ID or name of the context mapping that’s used. | Required | 64.0 |
| `entityId` | String | ID of a quote or an order. | Required | 64.0 |
| `expressionSet​VersionId` | String | ID of the expression set that starts with `9QM`. | Required | 64.0 |

## Response Body for GET

[Pricing Simulation Input Variables With Data](./connect-responses-pricing-simulation-input-variables-with-data-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-pricing-simulation-data-with-variables.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
