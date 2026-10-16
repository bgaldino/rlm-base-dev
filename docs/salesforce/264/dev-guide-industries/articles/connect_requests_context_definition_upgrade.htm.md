---
page_id: connect_requests_context_definition_upgrade.htm
title: Context Definition Upgrade Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_upgrade.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Upgrade Input

Input representation of context definition upgrade.

        
            
                
                    

**JSON example**

                    
: 
                        

```
{
  "contextDefinitions": [
    {
      "contextDefinitionId": "11Oxx0000006PfZEAU",
      "upgradeMode": "Sync"
    }
  ]
}
```

                    

                
                
                    

**Properties**

                    
: 
                        

                                
                                
                                
                                
                                
                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        
- 
- 
- 

                                        

                                        

                                    

                                

                            
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of this context definition to be upgraded. | Required | 64.0 |
| `upgradeMode` | String | The upgrade mode enum. Possible values are: Sync Preview OverrideThe default value is Sync. | Optional | 64.0 |
