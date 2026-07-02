---
page_id: actions_obj_get_catalog_details.htm
title: Get Catalog Details Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_catalog_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Catalog Details Action

Get details of a catalog record.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Get Catalog Details action is available in Enterprise, Unlimited, and Developer
Editions where Product Discovery is enabled.

## Inputs

| Input | Details |
| --- | --- |
| catalogId | Type  string  Description  Required. ID of the catalog record. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, enabling reference to a specific transaction or event chain. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains the status of the request, including the status code and message. |
| catalogDetailsResult | Type  Apex-defined  Description  Details of the catalog record. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |

## Example

:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('getCatalogDetails');

    action.setInvocationParameter('correlationId', '9cbb9650-48c5-11ed-96d1-0afcf185843b');
    action.setInvocationParameter('catalogId', '0ZSZ6000000CtXYOA0');

    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Catalog Details Action + '+results);
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "getCatalogDetails",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "apiStatusOutputRepresentation": {
            "statusMessage": null,
            "statusCode": "FetchedDetailsSuccessfully",
            "messages": []
          },
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "catalogDetailsResult": {
            "status": null,
            "numberOfCategories": 2,
            "name": "Hardware Catalog",
            "id": "0ZSZ6000000CtXYOA0",
            "effectiveStartDate": null,
            "effectiveEndDate": null,
            "description": "Hardware Catalog Desc",
            "customFields": null,
            "catalogType": "Sales",
            "catalogCode": "HC"
          }
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
