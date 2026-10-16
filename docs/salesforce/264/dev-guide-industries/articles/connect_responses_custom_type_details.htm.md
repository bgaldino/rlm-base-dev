---
page_id: connect_responses_custom_type_details.htm
title: Custom Type Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_custom_type_details.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Custom Type Details

Output representation of the custom type details of the Omniscript elements.

        
          

**JSON example**

          
: 
            

```
          "customTypeDetails" : {
            "discoveryFramework": {
                "questionText": "Can you provide more details about the transaction"
            }
          }
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `discovery​Framework` | [OS Element Discovery Framework](./connect_responses_os_element_discovery_framework_output.htm.md)[] | Custom type details for the Omniscript element for Discovery framework. | Small, 60.0 | 60.0 |
