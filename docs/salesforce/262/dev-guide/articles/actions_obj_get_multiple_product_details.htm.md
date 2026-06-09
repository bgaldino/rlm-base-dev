---
page_id: actions_obj_get_multiple_product_details.htm
title: Get Multiple Product Details Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_get_multiple_product_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Get Multiple Product Details Action

Get product details for a list of products.

This action is available in API version 64.0 and later.

You can invoke this action via Apex and Flows only.

## Special Access Rules

The Get Multiple Product Details action is available in Enterprise, Unlimited, and
Developer Editions where Product Discovery is enabled.

## Inputs

| Input | Details |
| --- | --- |
| additionalContextData | Type  Apex-defined  Description  Collection of Apex [`runtime_industries_cpq.AdditionalContextData`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md "HTML (New Window)") records that contain additional context data for nodes of the custom context definition, if applicable. You can add details for up to 10 nodes. |
| additionalFields | Type  Apex-defined  Description  An Apex [AdditionalFields](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_AdditionalFields.htm.md "HTML (New Window)") record that contains the additional fields that are passed for the Product2 object. |
| catalogId | Type  string  Description  ID of the catalog record. |
| contextDefinitionName | Type  string  Description  Name of the custom context definition that’s used to create context data for categories. If null, the default context definition is used. |
| contextMappingName | Type  string  Description  Name of the context mapping. By default, the default context mapping associated with the context definition is used. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| currencyCode | Type  string  Description  Currency code that’s used to calculate and show prices. |
| enablePricing | Type  boolean  Description  Indicates whether pricing procedure must run (`true`) or not (`false`). The default value is `true`. To use this parameter, the **Pricing Procedure** setting must be enabled. |
| enableQualificationProcedure | Type  boolean  Description  Indicates whether the qualification procedure is applied to categories (`true`) or not (`false`). |
| priceBookId | Type  string  Description  ID of the pricebook that the pricing information is retrieved from. |
| pricingProcedureName | Type  string  Description  Name of the pricing procedure to calculate product prices. If you don’t enter a value, the pricing procedure selected on the **Product Discovery Settings** page is used. |
| productDataInputs | Type  Apex-defined  Description  Required. Collection of Apex [BulkProductDetailsInputBody](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md "HTML (New Window)") records that contain details about the products that are to be retrieved. |
| qualificationProcedureName | Type  string  Description  Name of the custom qualification procedure that’s executed to determine the category list. If null, the default qualification procedure is executed. |
| userContextInputRepresentation | Type  Apex-defined  Description  An Apex UserContextInputRepresentation record that contains user details, such as account ID, geographical location, language preferences, and more. |

## Outputs

| Output | Details |
| --- | --- |
| apiStatusOutputRepresentation | Type  Apex-defined  Description  An Apex [`runtime_industries_cpq.ApiStatusRepresentation`](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md "HTML (New Window)") record that contains the status of the request, including the status code and message. |
| contextId | Type  string  Description  ID of the context that’s created using the specified context definition. |
| correlationId | Type  string  Description  Unique identifier attached to requests and messages, allowing reference to a specific transaction or event chain. |
| productDetailsOutputRepresentation | Type  Apex-defined  Description  Collection of Apex [BulkProductDetailsRepresentation](https://developer.salesforce.com/docs/./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md "HTML (New Window)") records that contain details of available products. |
| userContext | Type  Apex-defined  Description  An Apex ConnectApi.UserContextRepresentation record containing user information. |

## Example

:   Here's a sample input to call this invocable action from Apex code.

    ```
    Invocable.Action action = Invocable.Action.createStandardAction('getMultipleProductDetails');

    List<runtime_industries_cpq.BulkProductDetailsInputBody> productDataList = new List<runtime_industries_cpq.BulkProductDetailsInputBody>();
    runtime_industries_cpq.BulkProductDetailsInputBody productData = new runtime_industries_cpq.BulkProductDetailsInputBody();
    productData.productId = '01tIY000000nCxhYAE';

    productDataList.add(productData);

    runtime_industries_cpq.BulkProductDetailsInputBodyList productList = new runtime_industries_cpq.BulkProductDetailsInputBodyList();
    productList.productData = productDataList; 

    action.setInvocationParameter('productDataInputs', productList); 

    List<Invocable.Action.Result> results = action.invoke();
    System.debug('Result === ' + results);
    ```
:   Here's a sample response when you call this action.

    ```
    [
      {
        "actionName": "getMultipleProductDetails",
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
          "contextId": null,
          "productDetailsOutputRepresentation": [
            {
              "unitOfMeasure": {
                "unitCode": null,
                "scale": null,
                "roundingMethod": null,
                "name": null,
                "id": null
              },
              "status": null,
              "qualificationContext": null,
              "productType": null,
              "productSpecificationType": null,
              "productSellingModelOptions": [
                {
                  "productSellingModelId": "0jPxx0000000002EAA",
                  "productSellingModel": {
                    "status": "Active",
                    "sellingModelType": "TermDefined",
                    "pricingTermUnit": "Annual",
                    "pricingTerm": 1,
                    "name": "Term Based - Yearly",
                    "id": "0jPxx0000000002EAA"
                  },
                  "productId": "01txx0000006i2oAAA",
                  "id": "0iOxx000000000JEAQ"
                }
              ],
              "productRelatedComponent": {
                "unitOfMeasure": null,
                "sequence": null,
                "quoteVisibility": null,
                "quantityScaleMethod": null,
                "quantity": null,
                "productRelationshipTypeId": null,
                "productComponentGroupId": null,
                "productClassificationId": null,
                "parentSellingModelId": null,
                "parentProductId": null,
                "minQuantity": null,
                "maxQuantity": null,
                "isQuantityEditable": null,
                "isExcluded": null,
                "isDefaultComponent": null,
                "isComponentRequired": null,
                "id": null,
                "doesBundlePriceIncludeChild": null,
                "childSellingModelId": null,
                "childProductId": null
              },
              "productQuantity": {
                "quantity": null,
                "minQuantity": null,
                "maxQuantity": null
              },
              "productPricingInformation": null,
              "productInformation": null,
              "productComponentGroups": [],
              "productCode": "ASTCERT001",
              "productClassification": {
                "id": null
              },
              "prices": [
                {
                  "pricingModel": {
                    "unitOfMeasure": null,
                    "pricingModelType": "TermDefined",
                    "occurrence": 1,
                    "name": "Term Based - Yearly",
                    "id": "0jPxx0000000002EAA",
                    "frequency": "Annual"
                  },
                  "priceBookId": "01sxx0000005ptpAAA",
                  "priceBookEntryId": "01uxx0000008yXaAAI",
                  "price": 2000,
                  "isSelected": true,
                  "isDerived": false,
                  "isDefault": true,
                  "effectiveTo": null,
                  "effectiveFrom": null,
                  "currencyIsoCode": "USD"
                }
              ],
              "nodeType": "simpleProduct",
              "name": "AI Specialist Certification",
              "isSoldOnlyWithOtherProds": false,
              "isQuantityEditable": null,
              "isDefaultComponent": null,
              "isComponentRequired": null,
              "isAssetizable": true,
              "isActive": true,
              "id": "01txx0000006i2oAAA",
              "endOfLifeDate": null,
              "displayUrl": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsp4GoUP_nGiCXJ-wzYkPx-RlA_UCUX0zIDv3slxnJACqXaRd1vHJUZe6yQklUiXvEDgo&usqp=CAU",
              "discontinuedDate": null,
              "description": "The Certified Artificial Intelligence Expert certification is typically designed for individuals who have an in-depth understanding of artificial intelligence (AI) concepts, algorithms, and applications and want to validate their expertise in the field.",
              "configureDuringSale": "NotAllowed",
              "childProducts": [],
              "catalogs": [],
              "availabilityDate": null,
              "attributes": [],
              "attributeCategories": [],
              "additionalFields": []
            },
            {
              "unitOfMeasure": {
                "unitCode": null,
                "scale": null,
                "roundingMethod": null,
                "name": null,
                "id": null
              },
              "status": null,
              "qualificationContext": null,
              "productType": null,
              "productSpecificationType": null,
              "productSellingModelOptions": [
                {
                  "productSellingModelId": "0jPxx0000000002EAA",
                  "productSellingModel": {
                    "status": "Active",
                    "sellingModelType": "TermDefined",
                    "pricingTermUnit": "Annual",
                    "pricingTerm": 1,
                    "name": "Term Based - Yearly",
                    "id": "0jPxx0000000002EAA"
                  },
                  "productId": "01txx0000006i2rAAA",
                  "id": "0iOxx000000000QEAQ"
                }
              ],
              "productRelatedComponent": {
                "unitOfMeasure": null,
                "sequence": null,
                "quoteVisibility": null,
                "quantityScaleMethod": null,
                "quantity": null,
                "productRelationshipTypeId": null,
                "productComponentGroupId": null,
                "productClassificationId": null,
                "parentSellingModelId": null,
                "parentProductId": null,
                "minQuantity": null,
                "maxQuantity": null,
                "isQuantityEditable": null,
                "isExcluded": null,
                "isDefaultComponent": null,
                "isComponentRequired": null,
                "id": null,
                "doesBundlePriceIncludeChild": null,
                "childSellingModelId": null,
                "childProductId": null
              },
              "productQuantity": {
                "quantity": null,
                "minQuantity": null,
                "maxQuantity": null
              },
              "productPricingInformation": null,
              "productInformation": null,
              "productComponentGroups": [],
              "productCode": "ACERT001",
              "productClassification": {
                "id": null
              },
              "prices": [
                {
                  "pricingModel": {
                    "unitOfMeasure": null,
                    "pricingModelType": "TermDefined",
                    "occurrence": 1,
                    "name": "Term Based - Yearly",
                    "id": "0jPxx0000000002EAA",
                    "frequency": "Annual"
                  },
                  "priceBookId": "01sxx0000005ptpAAA",
                  "priceBookEntryId": "01uxx0000008yXdAAI",
                  "price": 2000,
                  "isSelected": true,
                  "isDerived": false,
                  "isDefault": true,
                  "effectiveTo": null,
                  "effectiveFrom": null,
                  "currencyIsoCode": "USD"
                }
              ],
              "nodeType": "simpleProduct",
              "name": "Admin Certification",
              "isSoldOnlyWithOtherProds": false,
              "isQuantityEditable": null,
              "isDefaultComponent": null,
              "isComponentRequired": null,
              "isAssetizable": true,
              "isActive": true,
              "id": "01txx0000006i2rAAA",
              "endOfLifeDate": null,
              "displayUrl": null,
              "discontinuedDate": null,
              "description": null,
              "configureDuringSale": "Allowed",
              "childProducts": [],
              "catalogs": [],
              "availabilityDate": null,
              "attributes": [],
              "attributeCategories": [],
              "additionalFields": []
            }
          ]
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
