---
page_id: connect_responses_load_configuration_instance_output.htm
title: Configuration Load Instance
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_load_configuration_instance_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Load Instance

Output representation of the details of the context or session that are returned with a
    load configuration request.

      
        
          

**JSON Example**

          
: 
            

```
{
  "configuratorMessages": {},
  "configuratorUITreatments": [
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
  ],
  "contextId": "831f07b01cf0cbd2d046adf5350420f85f0611b4b1e22e183921a063857a1377",
  "errors": [],
  "productQualifications": {
    "01tDU000000EOTCYA4": {
      "isQualified": true
    }
  },
  "success": true
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Messages` | Map<String, <[Configurator Message](./connect_responses_configurator_message_output.htm.md)>> | Map of the product IDs to the list of configurator messages. Configurator messages are results from any validations, Business Rules Engines (BRE) calls, or Salesforce Pricing calls. | Small, 60.0 | 60.0 |
| `configurator​UITreatments` | [Configurator UI Treatment](./connect_responses_configurator_u_i_treatment_output.htm.md)[] | Details of the UI treatments that specify the product configuration rule actions to override the disable or hide behavior in the UI for product options, product attributes, and attribute picklist values. | Small, 62.0 | 62.0 |
| `contextId` | String | ID of the transaction context. | Small, 60.0 | 60.0 |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.264.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors, which contains an error code and a message. | Small, 60.0 | 60.0 |
| `product​Qualifications` | Map<String, [Configurator Qualification Context](./connect_responses_configurator_qualification_context_output.htm.md)> | Map of the product IDs to the execution results from qualification rules. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the call was successful (`true`) not (`false`). | Small, 60.0 | 60.0 |
