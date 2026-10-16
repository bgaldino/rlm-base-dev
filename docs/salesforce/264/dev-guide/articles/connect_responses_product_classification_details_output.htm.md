---
page_id: connect_responses_product_classification_details_output.htm
title: Product Classification Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_details_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Classification Details

Output representation that contains the details of a single product classification,
    including its attributes and categories.

        
          

**JSON example**

          
: 
            

```
{
  "id": "dummyId",
  "name": "Dummy Product Classification",
  "code": "DUMMY_CODE",
  "attributeCategories": [{
          "attributes": [
            {
              "attributeNameOverride": "Dummy_Attribute__c",
              "code": "ATTR_CODE_1",
              "dataType": "String",
              "defaultValue": "default",
              "description": "A dummy attribute for demonstration.",
              "developerName": "Dummy_Attribute",
              "displayType": "Text",
              "helpText": "Help text for dummy attribute",
              "id": "attrId1",
              "isConfigurable": true,
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": false,
              "isValueCloneable": true,
              "label": "Dummy Attribute Label",
              "maximumCharacterCount": 100,
              "maximumValue": "100",
              "minimumCharacterCount": 1,
              "minimumValue": "1",
              "name": "Dummy Attribute",
              "sequence": 1,
              "status": "Active",
              "stepValue": "1"
            }
          ],
          "code": "GENERAL",
          "id": "catId1",
          "name": "General"
        }],
  "attributes": [{
          "attributeNameOverride": "Dummy_Attribute__c",
          "code": "ATTR_CODE_1",
          "dataType": "String",
          "defaultValue": "default",
          "description": "A dummy attribute for demonstration.",
          "developerName": "Dummy_Attribute",
          "displayType": "Text",
          "helpText": "Help text for dummy attribute",
          "id": "attrId1",
          "isConfigurable": true,
          "isHidden": false,
          "isPriceImpacting": false,
          "isReadOnly": false,
          "isRequired": false,
          "isValueCloneable": true,
          "label": "Dummy Attribute Label",
          "maximumCharacterCount": 100,
          "maximumValue": "100",
          "minimumCharacterCount": 1,
          "minimumValue": "1",
          "name": "Dummy Attribute",
          "sequence": 1,
          "status": "Active",
          "stepValue": "1"
        }]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              
              

              

              

              

            

            
              

              
              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeCategories` | [Product Classification Attribute Category](./connect_responses_attribute_category_output.htm.md)[] | List of attribute categories applicable to the product classification. | Small, 66.0 | 66.0 |
| `attributes` | [Product Classification Attribute Definition](./connect_responses_attribute_definition_output.htm.md)[] | List of uncategorized attributes applicable to the product classification. | Small, 66.0 | 66.0 |
| `code` | String | Code of the product classification. | Small, 66.0 | 66.0 |
| `id` | String | ID of the product classification. | Small, 66.0 | 66.0 |
| `name` | String | Name of the product classification. | Small, 66.0 | 66.0 |
