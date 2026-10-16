---
page_id: actions_obj_post_draft_credit_memo.htm
title: Post Draft Credit Memo Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_post_draft_credit_memo.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Post Draft Credit Memo Action

Post a draft credit memo to a credit memo record for review and
            approval.

        
            

This action is available in API version 65.0 and later.

        

        
        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: `/services/data/v68.0/actions/standard/postDraftCreditMemo`

                
                
                    

**Formats**

                    
: JSON, XML

                
                
                    

**HTTP Methods**

                    
: POST

                
                
                    

**Authentication**

                    
: `Authorization:
                            Bearertoken`

                
            

        

        

## Inputs

            
            

                    
                    
                    
                        
                            

                            

                        

                    

                    
                        
                            

                            

: 

: 

                        

                        
                            

                            

: 

: 

                        

                    

                
| Input | Details |
| --- | --- |
| correlationId | **Type** string **Description** Splunk correlation ID to use to track messages that are related to the request and logged in Splunk by the different services involved in the request. If not specified, the service creates a random Universally Unique Identifier (UUID). |
| creditMemoId | **Type** string **Description** Required. ID of the credit memo record in `Draft` status to be posted. |

        

        

## Outputs

            
            

                    
                    
                    
                        
                            

                            

                        

                    

                    
                        
                            

                            

: 

: 

                        

                        
                            

                            

: 

: 

                        

                    

                
| Output | Details |
| --- | --- |
| requestIdentifier | **Type** string **Description** The UUID that's used to track the status of the asynchronous action. |
| statusUrl | **Type** string **Description** The URL to use to check the status of the request. |

        

        
        

## Example

            
            
                
                    

**POST**

                    
: 
                        

This example shows a sample request that contains the ID of the credit
                            memo to be posted.

                        

```
{
  "inputs": [
    {
      "creditMemoId": "50gDU00000001MdYAI"
    }
  ]
}
```

                    

                    
: 
                        

This example shows a sample successful response.

                        

```
[
  {
    "actionName": "postDraftCreditMemo",
    "errors": [],
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "statusUrl": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PDU000000A4nw2AC",
      "requestIdentifier": "d3a9d9ce-2a83-4a08-bcf3-df0348a0008c"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```
