---
page_id: actions_obj_search_products_with_guided_selection.htm
title: Search Product with Guided Selection Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_search_products_with_guided_selection.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Search Product with Guided Selection Action

Use guided product selection to search for
products.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Search Product with Guided Selection action is available in Enterprise,
Unlimited, and Developer Editions where Product Discovery is enabled.

## Inputs

| Input | Details |
| --- | --- |
| additionalContextData | Type  Apex-defined  Description  Collection of Apex [`runtime_industries_cpq.AdditionalContextData`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)") records that contain the nodes used in addition to context definition nodes for data hydration. This parameter can contain up to 10 nodes. |
| additionalFields | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.AdditionalFields`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_AdditionalFields.htm.md "HTML (New Window)") record that contains the collection of additional fields to be included in the response. This parameter supports only the fields from the Product2 and ProductAttributeDefinition objects. The fields defined for the ProductAttributeDefinition object must also be available on the ProductClassificationAttr object. |
| catalogId | Type  string  Description  ID of the catalog to find and retrieve products. |
| categoryId | Type  string  Description  ID of the category or subcategory to find and retrieve products. |
| contextDefinition | Type  string  Description  API name of the context definition that's used for context creation. If you don’t specify a value, the context selected on the **Product Discovery Settings** page is used. |
| contextMapping | Type  string  Description  API name of the context mapping that's used for data hydration. The value of this parameter is used only if it belongs to the specified context definition. |
| correlationId | Type  string  Description  Unique ID that’s used to reference a series of related actions. |
| currencyCode | Type  string  Description  Currency code that’s used to calculate and show prices. Only the products with the currency code matching the entered currency code are fetched. |
| executeConfigurationRules | Type  boolean  Description  Indicates whether configuration rules must run (`true`) or not (`false`). Available in API version 67.0 and later. |
| enablePricing | Type  boolean  Description  Indicates whether pricing procedure must run (`true`) or not (`false`). The default value is `true`. To use this parameter, the **Pricing Procedure** setting must be enabled. |
| enableQualification | Type  boolean  Description  Indicates whether qualification procedure must run (`true`) or not (`false`). The default value is `true`. To use this parameter, the **Qualification Procedure** setting must be enabled. |
| filterInputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.FilterInputRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md "HTML (New Window)") record that contains the filter criteria. This parameter supports only the `name` property and the `eq`, `in`, or `contains` operators. If it contains multiple criteria, all the criteria are applied. |
| guidedSelectionResponseId | Type  string  Description  Response identifier that stores user responses specified in the guided product selection window. |
| includeCatalogDetails | Type  boolean  Description  Indicates whether catalog details must be included in the response (`true`) or not (`false`). |
| orderBy | Type  string  Description  Comma-delimited string of key-value pairs that specify how results are sorted. Each string must contain a field name and its sort order. For example, ["name:asc",”custom\_field:asc”]. |
| priceBookId | Type  string  Description  ID of the pricebook that the pricing information is retrieved from. |
| pricingProcedure | Type  string  Description  API name of the pricing procedure to calculate product prices. If you don’t specify a value, the pricing procedure selected on the **Product Discovery Settings** page is used. |
| productClassificationId | Type  string  Description  ID of the product classification that's used to filter products. |
| productCursor | Type  string  Description  Unique identifier that represents the position of the product from which the next set of results are retrieved. |
| qualificationProcedure | Type  string  Description  API name of the qualification procedure to evaluate product eligibility. If you don’t specify a value, the qualification procedure selected on the **Product Discovery Settings** page is used. |
| recordLimit | Type  integer  Description  Maximum number of results to be returned in the response. Specify a value from 1 through 100. Default value is 10. |
| relatedObjectFilters | Type  Apex-defined  Description  Collection of Apex [`runtime_industries_cpq.RelatedObjectFilterInputRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm.md "HTML (New Window)") records, each containing a related object and the filter criteria that’s applied on the object. |
| searchTerms | Type  Apex-defined  Description  Collection of terms that are used to search products. See [GuidedSelectionSearchTerm](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md). |
| transactionContextId | Type  string  Description  Context ID of the quote or order. Available in API version 67.0 and later. |
| transactionId | Type  string  Description  ID of the quote or order. Available in API version 67.0 and later. |
| userContext | Type  Apex-defined  Description  An Apex ConnectApi.UserContextInputRepresentation record containing user information to evaluate product eligibility and calculate pricing. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains the status of the request, including the status code and message. |
| contextId | Type  string  Description  ID of the context that’s created by using the specified context definition. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| productCursor | Type  string  Description  Unique identifier that represents the position of the product from which the next set of results are retrieved. |
| productListOutputRepresentations | Type  Apex-defined  Description  Collection of Apex [ProductListOutputRepresentation](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_ProductListRepresentation.htm.md "HTML (New Window)") records that contain details about the product shown by the Guided Product Selection. |
| recordOffset | Type  integer  Description  Number of catalog records to skip in the request. The default is 0. |
| searchTerms | Type  Apex-defined  Description  Collection of terms that are used to search products. See [GuidedSelectionSearchTerm](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md). |
| userContext | Type  Apex-defined  Description  An Apex ConnectApi.UserContextRepresentation record containing user information. |

## Example

:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('searchPrdctWithGuidedSelection');

    action.setInvocationParameter('correlationId', '77f9dc6a-8ecc-44a3-8d89-4050179cc846');
    //action.setInvocationParameter('catalogId', '0ZSxx000000004sGAA');
    action.setInvocationParameter('guidedSelectionResponseId', '0U3xx0000004CPACA2');
    //action.setInvocationParameter('priceBookId', '01sxx0000005pyfAAA');
    //action.setInvocationParameter('categoryId', '0ZGxx000000004rGAA');
    action.setInvocationParameter('enableQualification', true);
    action.setInvocationParameter('enablePricing', true);
    //action.setInvocationParameter('contextDefinition', 'PDACDCtx');
    //action.setInvocationParameter('contextMapping', 'ProductDiscoveryMapping');
    //action.setInvocationParameter('qualificationProcedure', 'PDQualProceWithQuote');
    //action.setInvocationParameter('pricingProcedure', 'IconpricingProcedure');
    action.setInvocationParameter('includeCatalogDetails', true);
    action.setInvocationParameter('currencyCode', 'USD');
    action.setInvocationParameter('executeConfigurationRules', true);
    List<String> orderByInputs = new List<String>();
    orderByInputs.add('name:asc');
    orderByInputs.add('id:desc');
    action.setInvocationParameter('orderBy', orderByInputs);
    List<runtime_industries_cpq.GuidedSelectionSearchTerm> searchTerms = new List<runtime_industries_cpq.GuidedSelectionSearchTerm>();
    runtime_industries_cpq.GuidedSelectionSearchTerm searchTerm = new runtime_industries_cpq.GuidedSelectionSearchTerm();
    searchTerm.term = 'Laptop Basic Bundle';
    List<String> tags = new List<String>();
    tags.add('Laptop');
    tags.add('Desktop');
    searchTerm.tags = tags;
    searchTerms.add(searchTerm);

    runtime_industries_cpq.GuidedSelectionSearchTermList searchTermList = new runtime_industries_cpq.GuidedSelectionSearchTermList();
    searchTermList.searchTerms = searchTerms;
    action.setInvocationParameter('searchTerms', searchTermList);
    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Guided Selection result = ' + results);
    ```
:   Here's a sample response when you call this action.

    ```
    {
      "recordOffset": 5,
      "contextId": null,
      "correlationId": "854c487d-183e-40b6-ba42-f079a6e695a3",
      "apiStatusOutputRepresentation": {
        "statusMessage": null,
        "statusCode": "FetchedDetailsSuccessfully",
        "messages": []
      },
      "searchTerms": [
        {
          "term": "Additional API",
          "tags": []
        }
      ],
      "productListOutputRepresentations": [
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
          "childProducts": [],
          "categories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "API",
              "isNavigational": null,
              "id": "0ZGVW000000IUEG4A4",
              "hasSubCategories": null,
              "description": null,
              "childCategories": null,
              "catalogId": "0ZSVW000000AhdB4AS"
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
          "childProducts": [],
          "categories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "API",
              "isNavigational": null,
              "id": "0ZGVW000000IUEG4A4",
              "hasSubCategories": null,
              "description": null,
              "childCategories": null,
              "catalogId": "0ZSVW000000AhdB4AS"
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
          "childProducts": [],
          "categories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "API",
              "isNavigational": null,
              "id": "0ZGVW000000IUEG4A4",
              "hasSubCategories": null,
              "description": null,
              "childCategories": null,
              "catalogId": "0ZSVW000000AhdB4AS"
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
          "childProducts": [],
          "categories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "API",
              "isNavigational": null,
              "id": "0ZGVW000000IUEG4A4",
              "hasSubCategories": null,
              "description": null,
              "childCategories": null,
              "catalogId": "0ZSVW000000AhdB4AS"
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
          "childProducts": [],
          "categories": [
            {
              "sortOrder": null,
              "qualificationContext": {
                "reason": null,
                "isQualified": true
              },
              "parentCategoryId": null,
              "name": "API",
              "isNavigational": null,
              "id": "0ZGVW000000IUEG4A4",
              "hasSubCategories": null,
              "description": null,
              "childCategories": null,
              "catalogId": "0ZSVW000000AhdB4AS"
            }
          ],
          "catalogs": [],
          "availabilityDate": null,
          "attributeCategories": [],
          "additionalFields": []
        }
      ]
    }
    ```
