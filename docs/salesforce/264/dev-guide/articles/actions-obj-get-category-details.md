---
page_id: actions-obj-get-category-details
title: Get Category Details Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-get-category-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-invocable-actions-parent
legacy_page_id: actions_obj_get_category_details.htm
fetched_at: 2026-11-25
---

# Get Category Details Action

Get details of a category record.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Get Category Details action is available in Enterprise, Unlimited, and Developer Editions where Product Discovery is enabled.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `additionalContextData` | Apex-defined | Collection of Apex [`runtime_industries_cpq.AdditionalContextData`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalContextData.htm) records that contain additional context data for nodes of the custom context definition, if applicable. You can add details for up to 10 nodes. |
| `catalogId` | string | ID of the catalog record that’s used to search for products within a category. |
| `categoryId` | string | Required. ID of the category or subcategory that’s used to search for products. |
| `contextDefinitionName` | string | Name of the custom context definition that’s used to create context data for categories. If null, the default context definition is used. |
| `contextMappingName` | string | Name of the context mapping. By default, the default context mapping associated with the context definition is used. |
| `correlationId` | string | Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| `enableQualificationProcedure` | boolean | Indicates whether qualification rules are applied to categories ( `tru` e) or not ( `false` ). |
| `filterInputRepresentation` | Apex-defined | Collection of Apex [`runtime_industries_cpq.FilterInputRepresentation`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterInputRepresentation.htm) records that contain the filter criteria applied to the category records. |
| `qualificationProcedureName` | string | Name of the custom qualification procedure that’s executed to determine the category list. If null, the default qualification procedure is executed. |
| `userContextInputRepresentation` | Apex-defined | An Apex UserContextInputRepresentation record that contains user details, such as account ID, geographical location, language preferences, and more. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `apiStatusOutputRepresentation` | Apex-defined | An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm) record that contains the status of the request, including the status code and message. |
| `categoryDetailsRepresentations` | Apex-defined | Collection of Apex [CategoryDetailsRepresentation](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm) records that contain details about the retrieved category. |
| `correlationId` | string | Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |

## Example

Here’s a sample input to call this invocable action from Apex code.

```
Invocable.Action action = Invocable.Action.createStandardAction('getCategoryDetails');

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

action.setInvocationParameter('categoryId', '0ZGxx0000000001GAA');
action.setInvocationParameter('correlationId', '9cbb9650-48c5-11ed-96d1-0afcf185843b');
action.setInvocationParameter('userContext', userContext);
action.setInvocationParameter('enableQualification', True);
action.setInvocationParameter('qualificationProcedure', 'CatQual02');
action.setInvocationParameter('contextDefinition', 'CategoryCD');
action.setInvocationParameter('contextMapping', 'ProductDiscoveryMapping');
action.setInvocationParameter('additionalContextData', additionalContextDataOut);

List<Invocable.Action.Result> results = action.invoke();
System.debug('Search Action + '+results);
```

Here’s a sample response when you call this action.

```
{
  "root": [
    {
      "actionName": "getCategoryDetails",
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
        "categoryDetailsRepresentations": {
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
          "childCategories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": "0ZGxx0000000001GAA",
              "name": "level1",
              "isNavigational": true,
              "id": "0ZGxx000000004rGAA",
              "hasSubCategories": true,
              "description": null,
              "childCategories": [],
              "catalogId": null
            }
          ],
          "catalogId": "0ZSxx0000000002GAA"
        }
      },
      "sortOrder": -1,
      "version": 1
    }
  ]
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-get-category-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
