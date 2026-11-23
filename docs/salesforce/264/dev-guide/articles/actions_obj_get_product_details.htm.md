---
page_id: actions_obj_get_product_details.htm
title: Get Product Details Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_product_details.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Get Product Details Action

Get details such as attributes, hierarchy, and cardinality for the specified product.

This action is available in API version 62.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Get Product Details action is available in Enterprise, Unlimited, and Developer Editions where Product Discovery is enabled.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| additionalContextData | Apex-defined | An array of Apex [`runtime_industries_cpq.AdditionalContextData`](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)") records that contain the additional nodes that are used along with the context definition nodes for data hydration. The maximum number of supported nodes is 10. |
| additionalFields | Apex-defined | An Apex [`runtime_industries_cpq.AdditionalFields`](./apex_class_runtime_industries_cpq_AdditionalFields.htm.md "HTML (New Window)") record that contains an array of additional standard or custom fields to include in the response. The supported objects are `Product2` or `ProductAttributeDefinition`—If the fields defined for the `ProductAttributeDefinition` object aren’t available for the `ProductClassificationAttr` object, then the API request fails. |
| catalogId | string | Catalog ID that’s used to find and retrieve the products. |
| contextDefinition | string | API name of the context definition for context creation. If you don’t provide a value, the context selected on the Product Discovery Settings page from Setup is used. |
| contextMapping | string | API name of the context mapping for data hydration. The value of this parameter is used only if it belongs to the specified context definition. |
| correlationId | string | Currency code that’s used to calculate and show prices. Only the products with the currency code matching the specified currency code are fetched. |
| currencyCode | string | Currency code that’s used to calculate and show prices. |
| enablePricing | boolean | Indicates whether the pricing procedure must run (`true`) or not (`false`). The default value is `true`. To use this parameter, you must enable the Pricing Procedure setting from Setup. |
| enableQualification | boolean | Indicates whether the qualification procedure must run (`true`) or not (`false`). The default value is `true`. To use this parameter, you must enable the Qualification Procedure setting from Setup. |
| priceBookId | string | ID of the pricebook from which you want to retrieve the pricing details. |
| pricingProcedure | string | API name of the pricing procedure to calculate product prices. If you don’t specify a value, the pricing procedure selected on the Product Discovery Settings page from Setup is used. |
| productId | string | Required. ID of the product to get the details for. |
| productSellingModelId | string | ID of the product selling model. |
| qualificationProcedure | string | API name of the qualification procedure to evaluate product eligibility. If you don’t specify a value, the qualification procedure selected on the Product Discovery Settings page from Setup is used. |
| userContext | Apex-defined | An Apex `ConnectApi.UserContextInputRepresentation` record that contains the user details to evaluate product eligibility and calculate prices. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| apiStatus | Apex-defined | An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains a status code and message. |
| contextId | string | ID of the context that’s created by using the specified context definition. |
| correlationId | string | ID to reference a series of related actions. |
| results | Apex-defined | An Apex [`runtime_industries_cpq.ProductDetailsRepresentation`](./apex_class_runtime_industries_cpq_ProductDetailsRepresentation.htm.md "HTML (New Window)") record that contains the product details. |
| userContext | Apex-defined | An Apex `ConnectApi.UserContextRepresentation` record that contains the user details. |

## Usage of an Apex-Defined Data Type in a Flow

To use an Apex-defined input parameter in a flow, follow these guidelines.

**Create an Apex Class**

Create an Apex class defining the input and output parameters. In the flow, include the Apex-defined input parameters for which you want to add the details. In this example, we have created a class named ProductServiceAction that takes an object’s API name and record ID as input, and returns the additional context data.

```
public class ProductServiceAction {
    // Define input parameters
    public class FlowInput{
        @InvocableVariable(required=false)
        public String objectApiName;
        
        @InvocableVariable(required=false)
        public String recordId;
    }
    
    // Define output parameters
    public class FlowOutput{
        @invocableVariable
        public runtime_industries_cpq.AdditionalContextData additionalContextDataFinalOutput = new runtime_industries_cpq.AdditionalContextData();
        
    }
    
    // This method is invoked from a Flow
    @InvocableMethod(label='Process Input' description='Creates the Array of ContextDataInput for additional Context Data')
    public static List<FlowOutput> processContextData(List<FlowInput> inputs){
        String apiName;
        String recId;
        FlowOutput output = new FlowOutput();
        
    // Capture input from the flow
        for(FlowInput input: inputs){
            apiName = input.objectApiName;
            recId = input.recordId;
            }
    // Populate the ContextDataInput list to store additional context data    
        List<runtime_industries_cpq.ContextDataInput> listContextData = new List<runtime_industries_cpq.ContextDataInput>();
        runtime_industries_cpq.ContextDataInput cd1 = new runtime_industries_cpq.ContextDataInput();
        cd1.nodeName = apiName;
        cd1.nodeData = new Map<String, Object>();
        cd1.nodeData.put('id',recId);
        listContextData.add(cd1);
       
        output.additionalContextDataFinalOutput.additionalContextData = listContextData;
        List<FlowOutput> flowOutputs = new List<FlowOutput>();
        flowOutputs.add(output);
        
        List<runtime_industries_cpq.RelatedObjectFilter> relatedObjectFilterList = new List<runtime_industries_cpq.RelatedObjectFilter>();
       
        runtime_industries_cpq.RelatedObjectFilter relatedObjectFilter = new runtime_industries_cpq.RelatedObjectFilter();

        relatedObjectFilter.objectName = 'ProductSpecificationRecType';
        List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteriaList = new  List<runtime_industries_cpq.FilterCriteriaInputRepresentation>();
        runtime_industries_cpq.FilterCriteriaInputRepresentation criteria = new runtime_industries_cpq.FilterCriteriaInputRepresentation();
        criteria.property = 'IsCommercial';
        criteria.operator = 'eq';
        criteria.value = 'true';
        criteriaList.add(criteria);
        relatedObjectFilter.criteria = criteriaList;

        relatedObjectFilterList.add(relatedObjectFilter);
        output.relatedObjectFilter.relatedObjectFilter  = relatedObjectFilterList;
         
		output.userContext.accountId = '001DU000001nx9BYAQ';
        
        return flowOutputs;
       
    }

}
```

**Create a Flow with the Necessary Variables and Components:** Create a flow that enables users to add a search term to find products. Add the ProductService action that you’ve created above by using Apex. When a flow is invoked from a record, the flow sends the record's objectApiName and recordId to the Apex class, which then generates the flow output. The flow passes the objectApiName and recordId of the record that the flow is invoked from to the Apex class to generate the flow output. See [Example of How to Create a Flow for Product Discovery](https://help.salesforce.com/s/articleView?id=ind.product_catalog_example_create_custom_flow_for_browsing_and_adding_products.htm&type=5&language=en_US "HTML (New Window)").

**Configure the Action:** Configure the action (for example, Get Product Details action) to add values for the Apex-defined input parameters. Use the output of the created Apex class as the input of the Apex-defined parameter in the Get Product Details action, which users can use to get the product details.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_product_details.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
