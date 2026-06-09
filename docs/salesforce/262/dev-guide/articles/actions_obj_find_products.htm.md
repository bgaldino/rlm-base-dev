---
page_id: actions_obj_find_products.htm
title: Find Products Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_find_products.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Find Products Action

Search for the products from a catalog, category, or subcategory by
using the specified search term.

This action is available in API version 62.0 and later.

## Special Access Rules

The Find Products action is available in
Enterprise, Unlimited, and Developer Editions where Product Discovery is
enabled.

You can invoke this action via Apex and Flows only.

## Inputs

| Input | Details |
| --- | --- |
| additionalContextData | Type  Apex-defined  Description  An array of Apex [`runtime_industries_cpq.AdditionalContextData`](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)") records that contain the additional nodes that are used along with the context definition nodes for data hydration.  The maximum number of supported nodes is 10. |
| additionalFields | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.AdditionalFields`](./apex_class_runtime_industries_cpq_AdditionalFields.htm.md "HTML (New Window)") record that contains an array of additional standard or custom fields to include in the response.  The supported objects are:   - `Product2` - `ProductAttributeDefinition`—If the   fields defined for the `ProductAttributeDefinition` object aren’t   available for the `ProductClassificationAttr` object, then   the API request fails. |
| catalogId | Type  string  Description  Catalog ID that’s used to find and retrieve the products. |
| categoryId | Type  string  Description  ID of the category or subcategory to get the products for. |
| contextDefinition | Type  string  Description  API name of the context definition used for context creation. If you don’t specify a value, the context selected on the Product Discovery Settings page from Setup is used. |
| contextMapping | Type  string  Description  API name of the context mapping that’s used for data hydration. The value of this parameter is used only if it belongs to the specified context definition. |
| correlationId | Type  string  Description  Currency code that’s used to calculate and show prices. Only the products with the currency code matching the specified currency code are fetched. |
| currencyCode | Type  string  Description  Currency code that’s used to calculate and show prices. |
| cursor | Type  string  Description  A unique identifier that represents the position of the product from which the next set of results are retrieved. |
| executeConfigurationRules | Type  boolean  Description  Indicates whether configuration rules must run (`true`) or not (`false`). Available in API version 67.0 and later. |
| enablePricing | Type  boolean  Description  Indicates whether the pricing procedure must run (`true`) or not (`false`).  The default value is `true`. To use this parameter, you must enable the Pricing Procedure setting from Setup. |
| enableQualification | Type  boolean  Description  Indicates whether the qualification procedure must run (`true`) or not (`false`).  The default value is `true`. To use this parameter, you must enable the Qualification Procedure setting from Setup. |
| filter | Type  Apex-defined  Description  A collection of Apex [`runtime_industries_cpq.FilterInputRepresentation`](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md "HTML (New Window)") records where each record contains a related object and the filter criteria that’s applied on the object.  The filter parameter supports only the `name` property.  The supported operators are:   - `eq` - `in` - `contains`   If this parameter contains multiple criteria, all the criteria are applied. |
| includeCatalogDetails | Type  boolean  Description  Indicates whether catalog details must be included in the response (`true`) or not (`false`). |
| limit | Type  integer  Description  Maximum number of results to be returned in the response. Enter a value from 1 through 100.  The default value is 10. |
| orderBy | Type  string  Description  Comma-separated string of key-value pairs that specify how results are sorted. Each string must contain a field name and its sort order. For example, `["name:asc",”custom_field:asc”]`. |
| priceBookId | Type  string  Description  ID of the pricebook from which you wan to retrieve the pricing details. |
| productClassificationId | Type  string  Description  ID of the product classification that’s used to filter products. |
| pricingProcedure | Type  string  Description  API name of the pricing procedure to calculate product prices. If you don’t specify a value, the pricing procedure selected on the Product Discovery Settings page from Setup is used. |
| qualificationProcedure | Type  string  Description  API name of the qualification procedure to evaluate product eligibility. If you don’t specify a value, the qualification procedure selected on the Product Discovery Settings page from Setup is used. |
| transactionContextId | Type  string  Description  Context ID of the quote or order. Available in API version 67.0 and later. |
| transactionId | Type  string  Description  ID of the quote or order. Available in API version 67.0 and later. |
| relatedObjectFilters | Type  Apex-defined  Description  A collection of Apex [`runtime_industries_cpq.RelatedObjectFilterInputRepresentation`](./apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm.md "HTML (New Window)") records, where each record contains a related object and the filter criteria that’s applied on the object. |
| searchTerm | Type  string  Description  Required.  Search term to find and retrieve products. |
| userContext | Type  Apex-defined  Description  An Apex `ConnectApi.UserContextInputRepresentation` record that contains the user details to evaluate product eligibility and calculate prices. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatus | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains a status code and message. |
| contextId | Type  string  Description  ID of the context that’s created by using the specified context definition. |
| correlationId | Type  string  Description  ID to reference a series of related actions. |
| cursor | Type  string  Description  Unique identifier that represents the position of the next product in the dataset. It’s used as an input to retrieve the next set of products. |
| facets | Type  Apex-defined  Description  Collection of Apex ProductFacetsRepresentation records that contain details of the facet that's retrieved. |
| results | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.SearchProductsRepresentation`](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md "HTML (New Window)") record that contains the products that match the query. |
| userContext | Type  Apex-defined  Description  An Apex `ConnectApi.UserContextRepresentation` record that includes the user details. |

## Example

:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('findProducts');
    action.setInvocationParameter('searchTerm', 'Additional API');
    action.setInvocationParameter('executeConfigurationRules', true);
    action.setInvocationParameter('catalogId', '0ZSVW000000AhdB4AS');
    action.setInvocationParameter('transactionId', '0Q0VW0000018J6X0AU');
    List<String> orderBy = new List<String>();
    orderBy.add('name:asc');
    action.setInvocationParameter('orderBy', orderBy);
    List<Invocable.Action.Result> results = action.invoke();

    for (Invocable.Action.Result res : results) {
        if (res.isSuccess()) {
            Map<String, Object> outMap = res.getOutputParameters();
            String jsonOutput = JSON.serialize(outMap);	
            System.debug(jsonOutput);
        }
    }
    ```
:   Here’s a sample response for this action.

    ```
    {
      "facets": [],
      "apiStatus": {
        "statusMessage": null,
        "statusCode": "FetchedDetailsSuccessfully",
        "messages": []
      },
      "results": [
        {
          "unitOfMeasure": null,
          "status": null,
          "qualificationContext": {
            "reason": null,
            "isQualified": true
          },
          "productType": null,
          "productSpecificationType": null,
          "productSellingModelOptions": [
            {
              "productSellingModelId": "0jPVW0000001fh32AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Annual",
                "pricingTerm": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA"
              },
              "productId": "01tVW000003l7txYAA",
              "id": "0iOVW00000049w22AA"
            },
            {
              "productSellingModelId": "0jPVW0000001fh52AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "Evergreen",
                "pricingTermUnit": "Months",
                "pricingTerm": 1,
                "name": "Evergreen Monthly",
                "id": "0jPVW0000001fh52AA"
              },
              "productId": "01tVW000003l7txYAA",
              "id": "0iOVW00000049w12AA"
            },
            {
              "productSellingModelId": "0jPVW0000001fh62AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Months",
                "pricingTerm": 1,
                "name": "Term Monthly",
                "id": "0jPVW0000001fh62AA"
              },
              "productId": "01tVW000003l7txYAA",
              "id": "0iOVW00000049w32AA"
            }
          ],
          "productRelatedComponent": null,
          "productQuantity": null,
          "productPricingInformation": null,
          "productInformation": null,
          "productComponentGroups": [],
          "productCode": "QB-API",
          "productClassification": {
            "id": "11BVW000004ljiZ2AQ"
          },
          "prices": [
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA",
                "frequency": "Annual"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzfGYAQ",
              "price": 15000,
              "isSelected": false,
              "isDerived": false,
              "isDefault": true,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            },
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "Evergreen",
                "occurrence": 1,
                "name": "Evergreen Monthly",
                "id": "0jPVW0000001fh52AA",
                "frequency": "Months"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzg8YAA",
              "price": 2000,
              "isSelected": false,
              "isDerived": false,
              "isDefault": false,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            },
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Monthly",
                "id": "0jPVW0000001fh62AA",
                "frequency": "Months"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzg9YAA",
              "price": 1500,
              "isSelected": false,
              "isDerived": false,
              "isDefault": false,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            }
          ],
          "nodeType": "simpleProduct",
          "name": "Additional API",
          "isSoldOnlyWithOtherProds": false,
          "isQuantityEditable": null,
          "isDefaultComponent": null,
          "isComponentRequired": null,
          "isAssetizable": true,
          "isActive": true,
          "id": "01tVW000003l7txYAA",
          "endOfLifeDate": null,
          "displayUrl": "/resource/add_api",
          "discontinuedDate": null,
          "description": null,
          "configureDuringSale": "Allowed",
          "configurationRules": [
            {
              "type": "disable",
              "details": [
                {
                  "message": "This is disabled"
                }
              ]
            }
          ],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        },
        {
          "unitOfMeasure": null,
          "status": null,
          "qualificationContext": {
            "reason": null,
            "isQualified": true
          },
          "productType": null,
          "productSpecificationType": null,
          "productSellingModelOptions": [
            {
              "productSellingModelId": "0jPVW0000001fh32AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Annual",
                "pricingTerm": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA"
              },
              "productId": "01tVW000003l7tyYAA",
              "id": "0iOVW00000049w42AA"
            }
          ],
          "productRelatedComponent": null,
          "productQuantity": null,
          "productPricingInformation": null,
          "productInformation": null,
          "productComponentGroups": [],
          "productCode": "QB-API-FLEX",
          "productClassification": {
            "id": null
          },
          "prices": [
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA",
                "frequency": "Annual"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzfFYAQ",
              "price": 450,
              "isSelected": false,
              "isDerived": false,
              "isDefault": true,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            }
          ],
          "nodeType": "simpleProduct",
          "name": "Additional API Flex (100M)",
          "isSoldOnlyWithOtherProds": false,
          "isQuantityEditable": null,
          "isDefaultComponent": null,
          "isComponentRequired": null,
          "isAssetizable": true,
          "isActive": true,
          "id": "01tVW000003l7tyYAA",
          "endOfLifeDate": null,
          "displayUrl": "/resource/api_flex",
          "discontinuedDate": null,
          "description": "API instances remain under management until they are deleted. Instances of API Manager are aggregated using a Max Concurrent model. The usage for a month is the highest number of APIs Managed in a single given hour during a month.",
          "configureDuringSale": null,
          "configurationRules": [],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        },
        {
          "unitOfMeasure": null,
          "status": null,
          "qualificationContext": {
            "reason": null,
            "isQualified": true
          },
          "productType": null,
          "productSpecificationType": null,
          "productSellingModelOptions": [
            {
              "productSellingModelId": "0jPVW0000001fh32AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Annual",
                "pricingTerm": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA"
              },
              "productId": "01tVW000003l7tzYAA",
              "id": "0iOVW00000049w52AA"
            }
          ],
          "productRelatedComponent": null,
          "productQuantity": null,
          "productPricingInformation": null,
          "productInformation": null,
          "productComponentGroups": [],
          "productCode": "QB-API-GOVT",
          "productClassification": {
            "id": null
          },
          "prices": [
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA",
                "frequency": "Annual"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzfHYAQ",
              "price": 1450,
              "isSelected": false,
              "isDerived": false,
              "isDefault": true,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            }
          ],
          "nodeType": "simpleProduct",
          "name": "Additional API Gov",
          "isSoldOnlyWithOtherProds": false,
          "isQuantityEditable": null,
          "isDefaultComponent": null,
          "isComponentRequired": null,
          "isAssetizable": true,
          "isActive": true,
          "id": "01tVW000003l7tzYAA",
          "endOfLifeDate": null,
          "displayUrl": "/resource/api_govt",
          "discontinuedDate": null,
          "description": "API instances remain under management until they are deleted. Instances of API Manager are aggregated using a Max Concurrent model. The usage for a month is the highest number of APIs Managed in a single given hour during a month.",
          "configureDuringSale": null,
          "configurationRules": [],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        },
        {
          "unitOfMeasure": null,
          "status": null,
          "qualificationContext": {
            "reason": null,
            "isQualified": true
          },
          "productType": null,
          "productSpecificationType": null,
          "productSellingModelOptions": [
            {
              "productSellingModelId": "0jPVW0000001fh32AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Annual",
                "pricingTerm": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA"
              },
              "productId": "01tVW000003l7u0YAA",
              "id": "0iOVW00000049w92AA"
            }
          ],
          "productRelatedComponent": null,
          "productQuantity": null,
          "productPricingInformation": null,
          "productInformation": null,
          "productComponentGroups": [],
          "productCode": "QB-API-PREP",
          "productClassification": {
            "id": null
          },
          "prices": [
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA",
                "frequency": "Annual"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzfSYAQ",
              "price": 3240,
              "isSelected": false,
              "isDerived": false,
              "isDefault": true,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            }
          ],
          "nodeType": "simpleProduct",
          "name": "Additional API Pre-Prod",
          "isSoldOnlyWithOtherProds": false,
          "isQuantityEditable": null,
          "isDefaultComponent": null,
          "isComponentRequired": null,
          "isAssetizable": true,
          "isActive": true,
          "id": "01tVW000003l7u0YAA",
          "endOfLifeDate": null,
          "displayUrl": "/resource/api_preprod",
          "discontinuedDate": null,
          "description": "API instances remain under management until they are deleted. Instances of API Manager are aggregated using a Max Concurrent model. The usage for a month is the highest number of APIs Managed in a single given hour during a month.",
          "configureDuringSale": null,
          "configurationRules": [],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        },
        {
          "unitOfMeasure": null,
          "status": null,
          "qualificationContext": {
            "reason": null,
            "isQualified": true
          },
          "productType": null,
          "productSpecificationType": null,
          "productSellingModelOptions": [
            {
              "productSellingModelId": "0jPVW0000001fh32AA",
              "productSellingModel": {
                "status": "Active",
                "sellingModelType": "TermDefined",
                "pricingTermUnit": "Annual",
                "pricingTerm": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA"
              },
              "productId": "01tVW000003l7u1YAA",
              "id": "0iOVW00000049wA2AQ"
            }
          ],
          "productRelatedComponent": null,
          "productQuantity": null,
          "productPricingInformation": null,
          "productInformation": null,
          "productComponentGroups": [],
          "productCode": "QB-API-PROD",
          "productClassification": {
            "id": null
          },
          "prices": [
            {
              "pricingModel": {
                "unitOfMeasure": null,
                "pricingModelType": "TermDefined",
                "occurrence": 1,
                "name": "Term Annual",
                "id": "0jPVW0000001fh32AA",
                "frequency": "Annual"
              },
              "priceBookId": "01sVW0000024PZlYAM",
              "priceBookEntryId": "01uVW000000jzfdYAA",
              "price": 3240,
              "isSelected": false,
              "isDerived": false,
              "isDefault": true,
              "effectiveTo": null,
              "effectiveFrom": null,
              "currencyIsoCode": "USD"
            }
          ],
          "nodeType": "simpleProduct",
          "name": "Additional API Prod",
          "isSoldOnlyWithOtherProds": false,
          "isQuantityEditable": null,
          "isDefaultComponent": null,
          "isComponentRequired": null,
          "isAssetizable": true,
          "isActive": true,
          "id": "01tVW000003l7u1YAA",
          "endOfLifeDate": null,
          "displayUrl": "/resource/api_prod",
          "discontinuedDate": null,
          "description": "API instances remain under management until they are deleted. Instances of API Manager are aggregated using a Max Concurrent model. The usage for a month is the highest number of APIs Managed in a single given hour during a month.",
          "configureDuringSale": null,
          "configurationRules": [],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        }
      ],
      "contextId": "0000000r25tp21g002517775323419202e0743b1f275423d8a489c12ca99da72",
      "correlationId": "4ac34e38-13d6-4720-97c4-4db7b3d41678"
    }
    ```

## Usage of an Apex-Defined Data Type in a Flow

To use an Apex-defined input parameter in a flow, follow these guidelines.

Create an Apex Class
:   Create an Apex class defining the input and output parameters. In the flow, include the
    Apex-defined input parameters for which you want to add the details. In this
    example, we’ve created a class named ProductServiceAction that takes an
    object’s API name and record ID as input, and returns the additional context
    data.

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

Create a Flow with the Necessary Variables and Components
:   Create a flow that enables users to add a search term to find products. Add the
    ProductService action that you’ve created above by using Apex. When a flow
    is invoked from a record, the flow sends the record's objectApiName and
    recordId to the Apex class, which then generates the flow output. The flow
    passes the objectApiName and recordId of the record that the flow is invoked
    from to the Apex class to generate the flow output. See [Example of How to
    Create a Flow for Product Discovery](https://help.salesforce.com/s/articleView?id=ind.product_catalog_example_create_custom_flow_for_browsing_and_adding_products.htm&type=5&language=en_US "HTML (New Window)").

Configure the Action
:   Configure the action (for example, Find Products action) to add values for the Apex-defined
    input parameters. Use the output of the created Apex class as the input of
    the Apex-defined parameter in the Find Products action, which users can use
    to find products.
