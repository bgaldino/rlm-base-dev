---
page_id: actions-obj-invoke-rating-service
title: Invoke Rating Service Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-invoke-rating-service.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-invocable-actions-parent
legacy_page_id: actions_obj_invoke_rating_service.htm
fetched_at: 2026-11-25
---

# Invoke Rating Service Action

Invoke the rating service to rate the usage records.

The Invoke Rating Service action acts as a connector between batch management and the rating service. This action is available in API version 62.0 and later.

## Special Access Rules

The Invoke Rating Service action is available in Enterprise, Unlimited, and Developer Editions where Rate Management is enabled.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/invokeRatingService`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `attributeRateCardID` | string | ID of the rate card that’s used to define adjustments based on the attributes that impact the rate. |
| `baseRateCardID` | string | ID of the rate card that includes the base rate for the resource to be rated, based on its consumption. |
| `contextDefinitionId` | string | Required. ID of the context definition that’s used to create the context instance. |
| `contextMappingID` | string | ID of the context mapping that maps a standard object, context definition object, or any other input data source to the node that’s defined in the context definition. |
| `isSkipWaterfall` | boolean | Indicates whether to skip the generation of price waterfall data (`true`) or not (`false`). |
| `procedureName` | string | Name of the rating procedure that’s used to calculate the rates. |
| `recordID` | reference | Required. ID of the usage ratable summary record to be rated. |
| `tierRateCardID` | string | ID of the rate card that’s used to define adjustments for different tiers of a resource. |

## Outputs

None

## Example

**POST**

This example shows a sample request for the Invoke Rating Service action.

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

This example shows a sample response for the Invoke Rating Service action.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-invoke-rating-service.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
