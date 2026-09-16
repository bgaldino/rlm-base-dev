---
page_id: connect_requests_tag_values_input.htm
title: Tag Values Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_tag_values_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Tag Values Input

Input representation of the list of Tag Names to be updated and their
        values.

        
            
                
                    

**JSON example**

                    
: 
                        

```

                {
                    "tagName": "Name",
                    "tagValue": "updatedAccount"
                },
                {
                    "tagName": "City",
                    "tagValue": "Bangalore"
                }
         
```

                    

                
                
                    

**Properties**

                    
: 
                        

                                
                                
                                
                                
                                
                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                                
                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                    
                                        

                                        

                                        

                                        

                                        

                                    

                                

                            
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `tagName` | String | Name of tag thats need to be updated. | Required | 63.0 |
| `tagValue` | String | Updated value of tags. | Required | 63.0 |
