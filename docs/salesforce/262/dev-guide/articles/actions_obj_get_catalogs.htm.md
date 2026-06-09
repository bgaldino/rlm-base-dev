---
page_id: actions_obj_get_catalogs.htm
title: Get Catalogs Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_catalogs.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Catalogs Action

Get a list of catalog records.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

## Inputs

| Input | Details |
| --- | --- |
| recordLimit | Type  integer  Description  Number of catalog records to get. The minimum is 1, the maximum is 100, and the default is 100. |
| recordOffset | Type  integer  Description  Number of catalog records to skip in the request. The default is 0. |
| correlationId | Type  string  Description  Unique identifier for tracking requests and messages, allowing reference to a specific transaction or event chain. |
| orderBy | Type  string  Description  Sort records in ascending or descending order. |

## Outputs

| Output | Details |
| --- | --- |
| resultCatalogList | Type  Apex-defined  Description  List of filtered catalog records. See [CatalogOutputRepresentation](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md "HTML (New Window)"). |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains the status of the request, including the status code and message. |
| recordLimit | Type  integer  Description  Number of catalog records to show per page. |
| resultListCount | Type  integer  Description  Number of catalog records in the result. |
| correlationId | Type  string  Description  Unique identifier for tracking requests and messages, allowing reference to a specific transaction or event chain. |
| recordOffset | Type  integer  Description  Number of catalog records to skip in the request. The default is 0. |

## Example

POST
:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('getCatalogs');

    action.setInvocationParameter('correlationId', '9cbb9650-48c5-11ed-96d1-0afcf185843b');
    action.setInvocationParameter('recordLimit', 1);
    action.setInvocationParameter('recordOffset', 1);
    String[] sortOrder = new String[]{'Name:ASC'};
    action.setInvocationParameter('orderBy', sortOrder);

    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Catalog List Action + '+results);
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "getCatalogs",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "resultListCount": 2,
          "apiStatusOutputRepresentation": {
            "statusMessage": null,
            "statusCode": "FetchedDetailsSuccessfully",
            "messages": []
          },
          "resultCatalogList": [
            {
              "status": null,
              "numberOfCategories": 2,
              "name": "Hardware Catalog",
              "id": "0ZSZ6000000CtXYOA0",
              "effectiveStartDate": null,
              "effectiveEndDate": null,
              "description": "Hardware Catalog Desc",
              "customFields": [],
              "catalogType": "Sales",
              "catalogCode": "HC"
            }
          ],
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "recordOffset": 0,
          "recordLimit": 1
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
