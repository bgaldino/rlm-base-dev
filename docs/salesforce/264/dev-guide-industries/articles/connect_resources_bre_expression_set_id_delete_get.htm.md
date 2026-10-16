---
page_id: connect_resources_bre_expression_set_id_delete_get.htm
title: Expression Set (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_expression_set_id_delete_get.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set (DELETE, GET)

Read or delete expression set for a specified expression set
      ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/expression-set/${expressionSetId}
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/expression-set/$11Oxx0000006PcLEAU
```

          

        
        
          

**Available version**

          
: 58.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: DELETE, GET

        
        
          

**Response body for GET**

          
: [Expression Set Output](./connect_responses_expression_set_output.htm.md)

        
        
          

**Response body for DELETE**

          
: None.
