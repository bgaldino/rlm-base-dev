---
page_id: connect-responses-pricing-simulation-input-variables-with-data-output
title: Pricing Simulation Input Variables With Data
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-simulation-input-variables-with-data-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_pricing_simulation_input_variables_with_data_output.htm
fetched_at: 2026-11-25
---

# Pricing Simulation Input Variables With Data

Output representation of the pricing simulation variables with data.

## JSON Example

```
{
  "error": "",
  "simulationInputJsonWithData": "{\"SalesTransaction\": [{\"PriceBooks\": \"01sxx0000005ptpAAA\",\"SalesTransactionItem\": [{\"LineItemQuantity\": 4,\"ProductSellingModel\": null,\"Product\": \"01txx0000006i2SAAQ\",\"LineItem\": \"0QLxx0000004C92GAE\"},{\"LineItemQuantity\": 3,\"ProductSellingModel\": null,\"Product\": \"01txx0000006i2TAAQ\",\"LineItem\": \"0QLxx0000004C93GAE\"}]}]}",
  "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | String | Returns the cause of error, if any. For a successful request, this API returns an empty string. | Small, 64.0 | 64.0 |
| `simulationInput​JsonWith​Data` | String | Resultant simulation input variables with quote or order data such as ID, which was specified in the query parameters. | Small, 64.0 | 64.0 |
| `success` | Boolean | Indicates whether the request was successful (`true`) or not (`false`). | Small, 64.0 | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-pricing-simulation-input-variables-with-data-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
