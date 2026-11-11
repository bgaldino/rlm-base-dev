---
page_id: connect_requests_template_input.htm
title: Template Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_template_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Template Input

Input representation to get contract document related details.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `external​Review​Type` | String | Type of external review. Possible values are `OnlineMicrosoft365` or `OfflineMicrosoftWord`. | Optional | 60.0 |
| `isExternal​Review​Import` | Boolean | Indicates whether the checkout is for an external review import (`true`) or not (`false`). | Optional | 59.0 |
| `pdf​Document​Id` | String | ID for Contract PDF document. | Optional | 56.0 |
| `templateId` | String | Template ID with key prefix 2dt used to generate document. | Required | 56.0 |
| `word​Document​Id` | String | ID for Contract word document. | Optional | 56.0 |

    

    

## JSON Example

      
      

```

{
  "templateId": "2dtxx000000004rAAA",
  "isExternalReviewImport": false,
  "externalReviewType": "OnlineMicrosoft365"
}
```
