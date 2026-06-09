---
page_id: actions_obj_get_categories.htm
title: Get Categories Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_categories.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Categories Action

Get the list of categories associated with a catalog
record.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Get Categories action is available in Enterprise, Unlimited, and Developer
Editions where Product Discovery is enabled.

## Inputs

| Input | Details |
| --- | --- |
| additionalContextData | Type  Apex-defined  Description  Collection of Apex [`runtime_industries_cpq.AdditionalContextData`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)") records that contain additional context data for nodes of the custom context definition, if applicable. You can add details for up to 10 nodes. |
| catalogId | Type  string  Description  Required. ID of the catalog record. |
| categoryNestLevel | Type  integer  Description  Level of nesting within the category hierarchy to include in the request. |
| contextDefinitionName | Type  string  Description  Name of the custom context definition that’s used to create context data for categories. If null, the default context definition is used. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| contextMappingName | Type  string  Description  Name of the context mapping. By default, the default context mapping associated with the context definition is used. |
| enableQualificationProcedure | Type  boolean  Description  Indicates whether qualification rules are applied to categories (`true`) or not (`false`). |
| filterInputRepresentation | Type  Apex-defined  Description  Collection of Apex [`runtime_industries_cpq.FilterInputRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md "HTML (New Window)") records that contain the filter criteria applied to the category records. |
| parentCategoryId | Type  string  Description  ID of the parent category record. |
| qualificationProcedureName | Type  string  Description  Name of the custom qualification procedure that’s executed to determine the category list. If null, the default qualification procedure is executed. |
| userContextInputRepresentation | Type  Apex-defined  Description  An Apex UserContextInputRepresentation record that contains user details, such as account ID, geographical location, language preferences, and more. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains the status of the request, including the status code and message. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| resultCategoryList | Type  Apex-defined  Description  List of filtered category records. See [CategoryOutputRepresentation](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md "HTML (New Window)"). |
| resultListCount | Type  integer  Description  Number of category records in the result. |

## Example

:   Here's a sample input to call this invocable action from Apex
    code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('getCategories');

    ConnectApi.UserContextInputRepresentation userContext = new ConnectApi.UserContextInputRepresentation();
    userContext.accountId = '001xx000003GYiEAAW';

    runtime_industries_cpq.ContextDataInput data = new runtime_industries_cpq.ContextDataInput();
    String nodeNameVal = 'Quote__c';
    Map<String,Object> nodeDataVal = new Map<String,Object>();
    nodeDataVal.put('id',(Object)'0Q0xx0000004CDsCAM');
    nodeDataVal.put('businessObjectType',(Object)'Quote');
    data.nodeName = nodeNameVal;
    data.nodeData = nodeDataVal;
    List<runtime_industries_cpq.ContextDataInput> contextData= new List<runtime_industries_cpq.ContextDataInput>();
    contextData.add(data);
    runtime_industries_cpq.AdditionalContextData additionalContextDataOut = new runtime_industries_cpq.AdditionalContextData();
    additionalContextDataOut.additionalContextData = new List<runtime_industries_cpq.ContextDataInput>();
    additionalContextDataOut.additionalContextData.add(data);

    action.setInvocationParameter('catalogId', '0ZSxx0000000002GAA');
    action.setInvocationParameter('correlationId', '9cbb9650-48c5-11ed-96d1-0afcf185843b');
    action.setInvocationParameter('userContextInputRepresentation', userContext);
    action.setInvocationParameter('enableQualificationProcedure', True);
    action.setInvocationParameter('qualificationProcedureName', 'CatQual02');
    action.setInvocationParameter('contextDefinitionName', 'CategoryCD');
    action.setInvocationParameter('contextMappingName', 'ProductDiscoveryMapping');
    action.setInvocationParameter('additionalContextData', additionalContextDataOut);
    //action.setInvocationParameter('categoryDepth', 4);
    //action.setInvocationParameter('parentCategoryId', '0ZGxx0000000001GAA');

    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Search Action + '+results);
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "getCategories",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "resultCategoryList": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": "Category is not qualified because one or more field(s) do not match the qualification criteria. Fields:- CategoryId - 0ZGxx0000000001GAA quotename - null Max_Number_of_Employees - 1500 Min_Number_of_Employees - 1500",
                "isQualified": false
              },
              "parentCategoryId": null,
              "name": "Laptops",
              "isNavigational": true,
              "id": "0ZGxx0000000001GAA",
              "hasSubCategories": true,
              "description": null,
              "childCategories": [],
              "catalogId": "0ZSxx0000000002GAA"
            },
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "Desktops",
              "isNavigational": true,
              "id": "0ZGxx0000000002GAA",
              "hasSubCategories": false,
              "description": null,
              "childCategories": [],
              "catalogId": "0ZSxx0000000002GAA"
            },
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "Accessories",
              "isNavigational": true,
              "id": "0ZGxx0000000003GAA",
              "hasSubCategories": false,
              "description": null,
              "childCategories": [],
              "catalogId": "0ZSxx0000000002GAA"
            }
          ],
          "resultListCount": 3,
          "apiStatusOutputRepresentation": {
            "statusMessage": null,
            "statusCode": "FetchedDetailsSuccessfully",
            "messages": []
          },
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
