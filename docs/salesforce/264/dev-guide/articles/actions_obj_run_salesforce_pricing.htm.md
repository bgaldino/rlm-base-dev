---
page_id: actions_obj_run_salesforce_pricing.htm
title: Run Salesforce Pricing Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_salesforce_pricing.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Run Salesforce Pricing Action

Invoke the Pricing Connect API by providing the context, pricing procedure, and price waterfall details.

This action is available in API version 60.0 and later. You can use this action with Flows only. To use this action with an API tool such as Postman, see [Run Salesforce Headless Pricing Action](./actions_obj_run_salesforce_headless_pricing.htm.md "HTML (New Window)").

## Special Access Rules

The Run Salesforce Pricing action is available in Developer, Enterprise, and Unlimited Editions where Salesforce Pricing is enabled.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/runSalesforcePricing`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| contextInstanceId | string | Required. ID of the context data that’s used to build the pricing procedure. Get the context instance ID by invoking the Context Service API. See [Context Service (POST)](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/connect_resources_create_context.htm "HTML (New Window)"). |
| discoveryProcedure | string | Name of the discovery procedure that’s used to execute the discovery process of the pricing data. |
| effectiveDate | string | Date when the pricing rules, as specified in the pricing procedure, are applied. The effectiveDate parameter determines which pricing procedure to execute when multiple active versions of pricing procedures are available with different date ranges. |
| isDeveloperName | boolean | Indicates whether the input value in a procedure must use the API name of the pricing (`true`) or the field name (`false`). |
| isSkipWaterfall | boolean | Indicates whether the price waterfall data must be generated (`true`) or not (`false`). |
| pricingProcedureName | string | Required. Name of the pricing procedure record that’s used to execute the pricing process. |
| skipDiscovery | boolean | Indicates whether to skip executing the discovery procedure (`true`) or not (`false`). |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| executionId | string | ID of the executed pricing data. |

## Example

**POST**

This sample request is for the Run Salesforce Pricing action.

```
{
  "inputs": [
    {
      "contextInstanceId": "32f2c894-ba5e-41c0-91e4-2ab5826f579b",
      "pricingProcedureName": "PricingAction",
      "isSkipWaterfall": false,
      "skipDiscovery": false,
      "isDeveloperName": true,
      "effectiveDate": "2023-11-16T12:20:00.000Z",
      "discoveryProcedure": "ES1"
    }
  ]
}
```

This sample response is for the Run Salesforce Pricing action.

```
{
  "actionName": "runSalesforcePricing",
  "errors": null,
  "isSuccess": true,
  "outputValues": {
    "executionId": "2QTurzG2NRQ5bgrjvvqyh"
  },
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_salesforce_pricing.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
