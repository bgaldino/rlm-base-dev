---
page_id: connect_responses_message_rules_output.htm
title: Message Rules
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_message_rules_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_responses_config_rule_output.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Message Rules

Output representation of the details of the message rules.

        
          

**JSON example**

          
: 
            

```
{
  "message": "Constraints is running for laptop",
  "messageType": "Info",
  "primaryRecordId": "0QLxx0000004CU0GAM",
  "relatedRecordId": "0QLxx0000004CU1GAM"
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

- 
- 
- 

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | List of message strings to display to the user. | Small, 67.0 | 67.0 |
| `messageType` | String | Severity level of the message. Valid values are: `INFO` `WARNING` `ERROR` | Small, 67.0 | 67.0 |
| `primaryRecordId` | String | ID of the primary sales transaction item record. | Small, 67.0 | 67.0 |
| `relatedRecordId` | String | ID of the related record. | Small, 67.0 | 67.0 |
