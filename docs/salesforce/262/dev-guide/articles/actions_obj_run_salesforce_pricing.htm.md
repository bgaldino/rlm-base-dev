---
page_id: actions_obj_run_salesforce_pricing.htm
title: Run Salesforce Pricing Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_run_salesforce_pricing.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Run Salesforce Pricing Action

Invoke the Pricing Connect API by providing the context, pricing
procedure, and price waterfall details.

This action is available in API version 60.0 and later. You can use this action with Flows
only. To use this action with an API tool such as Postman, see [Run Salesforce Headless
Pricing Action](./actions_obj_run_salesforce_headless_pricing.htm.md "HTML (New Window)").

## Special Access Rules

The Run Salesforce Pricing action is available in Developer, Enterprise,
and Unlimited Editions where Salesforce Pricing is enabled.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/runSalesforcePricing`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| contextInstanceId | Type  string  Description  Required.  ID of the context data that’s used to build the pricing procedure. Get the context instance ID by invoking the Context Service API. See [Context Service (POST)](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/connect_resources_create_context.htm "HTML (New Window)"). |
| discoveryProcedure | Type  string  Description  Name of the discovery procedure that’s used to execute the discovery process of the pricing data. |
| effectiveDate | Type  string  Description  Date when the pricing rules, as specified in the pricing procedure, are applied.  The effectiveDate parameter determines which pricing procedure to execute when multiple active versions of pricing procedures are available with different date ranges. |
| isDeveloperName | Type  boolean  Description  Indicates whether the input value in a procedure must use the API name of the pricing (`true`) or the field name (`false`). |
| isSkipWaterfall | Type  boolean  Description  Indicates whether the price waterfall data must be generated (`true`) or not (`false`). |
| pricingProcedureName | Type  string  Description  Required.  Name of the pricing procedure record that’s used to execute the pricing process. |
| skipDiscovery | Type  boolean  Description  Indicates whether to skip executing the discovery procedure (`true`) or not (`false`). |

## Outputs

| Output | Details |
| --- | --- |
| executionId | Type  string  Description  ID of the executed pricing data. |

## Example

POST
:   This sample request is for the Run Salesforce Pricing action.

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

#### See Also

- [Salesforce Help: Invoke Salesforce Pricing in a Flow](https://help.salesforce.com/s/articleView?id=ind.pricing_invoke_salesforce_pricing_flow.htm&type=5&language=en_US "Salesforce Help: Invoke Salesforce Pricing in a Flow - HTML (New Window)")
