---
page_id: connect_resources_bre_decision_model_entity.htm
title: Decision Model Notation Export (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_model_entity.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Model Notation Export (POST)

Export decision matrix data to a file in the DMN (Decision Model
      Notation) format, an easily readable format for business rules designed by Object Management
      Group.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/decision-models/export
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/decision-models/export
```

          

        
        
          

**Available version**

          
: 58.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: POST

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
   "decisionModelEntityIds":[
      “0lNRO00000004f72AA”,
      “0lNRO000000rfn27AA”
   ]
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `decision​Model​EntityIds` | String[] | A list of decision matrix version IDs to export data from. | Required | 58.0 |

          

        
        
          

**Response body for POST**

          
: [Decision Model Export Output](./connect_responses_decision_model_export_output.htm.md)

        
      

    

  

#### See Also

- [DMN (Decision Model Notation)](https://www.omg.org/dmn/#:~:text=DMN%20is%20a%20modeling%20language,monitor%20their%20application%3B%20business%20analysts.)
