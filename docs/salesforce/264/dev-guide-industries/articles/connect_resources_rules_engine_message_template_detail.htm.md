---
page_id: connect_resources_rules_engine_message_template_detail.htm
title: Explainability Message Template Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_rules_engine_message_template_detail.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Explainability Message Template Details (GET)

Retrieves the details of an explainability message template for a
      specified template ID.

    
      
        
          

**Resource**

          
: 
            

```
/connect/business-rules/explainability/message-templates/${messageTemplateId}
```

          

        
        
          

**Resource Example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v67.0/connect
/business-rules/explainability/message-templates/8U8x00000000027CAA
```

          

        
        
          

**Available version**

          
: 56.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET

        
        
          

**Response body for GET**

          
: [Message Template Details](./connect_responses_message_template_detail_output.htm.md)
