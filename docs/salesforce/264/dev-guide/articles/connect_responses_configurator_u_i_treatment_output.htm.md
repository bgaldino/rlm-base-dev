---
page_id: connect_responses_configurator_u_i_treatment_output.htm
title: Configurator UI Treatment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_u_i_treatment_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-09-29
---

# Configurator UI Treatment

Output representation of the details of the UI treatments of a product configurator. The details include the product configuration rule actions to override the disable or hide behavior in the UI for product options, product attributes, and attribute picklist values.

    

## JSON Example

      
      

```
[
  {
    "details": {
      "attributeId": "0tjxx0000000007AAA",
      "prcId": "0dSxx0000000007EAA",
      "stiId": "0QLxx0000004CU0GAM",
      "attributePicklistValueId": "0v6xx0000000005AAA"
    },
    "uiTreatmentScope": "Bundle",
    "uiTreatmentTarget": "Attribute_Picklist_Value",
    "uiTreatmentType": "Hide"
  },
  {
    "details": {
      "stiId": "ref_f0f2da7b_c431_482d_bf4b_599052f3a2e1"
    },
    "uiTreatmentScope": "Product",
    "uiTreatmentTarget": "Component",
    "uiTreatmentType": "Disable"
  }
]
```

    

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `details` | Map<String, Object> | Key-value pair that specifies the items to apply the rules on, which includes these details. ID of the sales transaction item, ID of the product-related component, ID of the attribute, or ID of the attribute picklist value. | Small, 62.0 | 62.0 |
| `uiTreatment​Scope` | String | Type of the UI treatment to be performed. Valid values are `Product`—UI treatment is applicable to a certain product only or `Bundle`—UI treatment is applicable to the whole bundle. | Small, 62.0 | 62.0 |
| `uiTreatment​Target` | String | Target of the UI treatment. Valid values are `Component`—Represents a product option or bundle component, `Quantity`—Represents a quantity field, `Attribute`—Represents a certain attribute of the product, or `Attribute_Picklist_Value`—Represents one of the picklist values of a product attribute. | Small, 62.0 | 62.0 |
| `uiTreatment​Type` | String | Type of UI treatment to be performed. Valid values are `Hide`—Hide the associated target or `Disable`—Disable the associated target. | Small, 62.0 | 62.0 |
