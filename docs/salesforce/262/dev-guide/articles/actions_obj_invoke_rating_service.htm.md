---
page_id: actions_obj_invoke_rating_service.htm
title: Invoke Rating Service Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_invoke_rating_service.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Invoke Rating Service Action

Invoke the rating service to rate the usage records.

The Invoke Rating Service action acts as a connector between batch management and the rating
service. This action is available in API version 62.0 and later.

## Special Access Rules

The Invoke Rating Service action is available in Enterprise, Unlimited, and
Developer Editions where Rate Management is enabled.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/invokeRatingService`

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
| attributeRateCardID | Type  string  Description  ID of the rate card that’s used to define adjustments based on the attributes that impact the rate. |
| baseRateCardID | Type  string  Description  ID of the rate card that includes the base rate for the resource to be rated, based on its consumption. |
| contextDefinitionId | Type  string  Description  Required.  ID of the context definition that’s used to create the context instance. |
| contextMappingID | Type  string  Description  ID of the context mapping that maps a standard object, context definition object, or any other input data source to the node that’s defined in the context definition. |
| isSkipWaterfall | Type  boolean  Description  Indicates whether to skip the generation of price waterfall data (`true`) or not (`false`). |
| procedureName | Type  string  Description  Name of the rating procedure that’s used to calculate the rates. |
| recordID | Type  reference  Description  Required.  ID of the usage ratable summary record to be rated. |
| tierRateCardID | Type  string  Description  ID of the rate card that’s used to define adjustments for different tiers of a resource. |

## Outputs

None

## Example

POST
:   This example shows a sample request for the Invoke Rating Service action.

    ```
    {
      "inputs": [
        {
          "recordIDs": "56jSB000002Bn12CXC",
          "contextMappingId": "11jSB000002Bn13YAC",
          "contextDefinitionId": "11OSB0000000WSv2AM",
          "procedureName": "Invoke Rate",
          "isSkipWaterfall": false,
          "baseRateCardID": "11jSB000002Bn13YAC",
          "tierRateCardID": "fgjjSB0sdf987dsf",
          "attributeRateCardID": "asdfgh563034lk"
        }
      ]
    }
    ```
:   This example shows a sample response for the Invoke Rating Service action.

    ```
    [
        {
            "actionName": "invokeRatingService",
            "errors": null,
            "isSuccess": true,
            "outputValues": {}
        }
    ]
    ```
