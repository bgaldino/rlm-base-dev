---
page_id: connect_resources_decision_table_definition_details.htm
title: Decision Table Definitions (DELETE, GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_definition_details.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Definitions (DELETE, GET)

Get details of a decision table definition. Delete a decision table
      definition associated with a decision table.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/decision-table/definitions/${decisionTableId}
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect/business-rules/decision-table/definitions/0lDxx00000002Ur
```

          

        
        
          

**Available version**

          
: 58.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: DELETE, GET

        
      

      
        
          

**Response body for DELETE**

          
: [Decision Table
              Output](./connect_responses_decision_table_output.htm.md)

        
        
          

**Response body for GET**

          
: [Decision Table Output](./connect_responses_decision_table_output.htm.md)
