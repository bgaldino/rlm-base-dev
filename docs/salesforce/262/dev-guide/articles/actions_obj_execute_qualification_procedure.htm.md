---
page_id: actions_obj_execute_qualification_procedure.htm
title: Execute Qualification Procedure Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_execute_qualification_procedure.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Execute Qualification Procedure Action

Execute a qualification procedure, which returns the qualification
status for the specified products.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Execute Qualification Procedure action is
available in Enterprise, Unlimited, and Developer Editions where Product Discovery
is enabled.

## Inputs

| Input | Details |
| --- | --- |
| additionalContextData | Type  Apex-defined  Description  Collection of Apex AdditionalContextData records that contain additional context data for nodes of the custom context definition, if applicable. You can add details for up to 10 nodes. See [AdditionalContextData](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)"). |
| contextDefinitionName | Type  string  Description  Name of the custom context definition that’s used to create context data for categories. If null, the default context definition is used. |
| contextMappingName | Type  string  Description  Name of the context mapping. By default, the default context mapping associated with the context definition is used. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| productIds | Type  string  Description  Required. Collection of IDs of products that are to be checked for qualification. |
| qualificationProcedureName | Type  string  Description  Name of the custom qualification procedure that’s executed to determine the category list. If null, the default qualification procedure is executed. |
| userContextInputRepresentation | Type  Apex-defined  Description  An Apex UserContextInputRepresentation record that contains user details, such as account ID, geographical location, language preferences, and more. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex ApiStatusOutputRepresentation record that contains the status of the request, including the status code and message. |
| contextId | Type  string  Description  ID of the context that’s created by using the specified context definition. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| qualificationResultRepresentations | Type  Apex-defined  Description  Collection of Apex QualificationResultRepresentation records that contain details about the qualified product. |

## Example

:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('executeQualificationProcedure');

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

    List<String> productIds = new List<String>();
    prodIds.add('01txx0000006i2ZAAQ');
    prodIds.add('01txx0000006i35AAA');
    action2.setInvocationParameter('productIds', productIds);
    action.setInvocationParameter('correlationId', '9cbb9650-48c5-11ed-96d1-0afcf185843b');
    action.setInvocationParameter('userContextInputRepresentation', userContext);
    action.setInvocationParameter('qualificationProcedureName', 'CatQual02');
    action.setInvocationParameter('contextDefinitionName', 'CategoryCD');
    action.setInvocationParameter('contextMappingName', 'ProductDiscoveryMapping');
    action.setInvocationParameter('additionalContextData', additionalContextDataOut);

    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Execute Qualification Procedure Action + '+results);
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "executeQualificationProcedure",
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
          "qualificationResultRepresentations": [
            {
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "productId": "01tSG000007uDL8YAM"
            },
            {
              "qualificationContext": {
                "reason": "Product is not qualified because one or more field(s) do not match the qualification criteria. Fields:- ProductId - 01tSG000007uDLBYA2 Max_Number_of_Employees - 50 Min_Number_of_Employees - 50 RootProductId - ",
                "isQualified": false
              },
              "productId": "01tSG000007uDLBYA2"
            }
          ],
          "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
          "contextId": "0000000b28op21g00251747224654739cade16577eac4c8fb5d94a20d952fdab"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
