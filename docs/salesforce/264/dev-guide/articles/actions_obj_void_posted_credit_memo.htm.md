---
page_id: actions_obj_void_posted_credit_memo.htm
title: Void Posted Credit Memo Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_void_posted_credit_memo.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Void Posted Credit Memo Action

Invoke the Void Posted Credit Memo API by providing a credit memo ID.

        
            

This action is available in API version 66.0 and later.

        

        
        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: `/services/data/v68.0/actions/standard/voidPostedCreditMemo`

                
                
                    

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

                        

                    

                
| Input | Details |
| --- | --- |
| creditMemoId | **Type** string **Description** Required. ID of the credit memo record in posted status to be voided. |

        

        

## Outputs

            
            

                    
                    
                    
                        
                            

                            

                        

                    

                    
                        
                            

                            

: 

: 

                        

                        
                            

                            

: 

: 

                        

                    

                
| Output | Details |
| --- | --- |
| debitMemoId | **Type** string **Description** ID of the created debit memo record. |
| statusUrl | **Type** string **Description** URL to use to check the status of the request. |

        

        
        

## Example

            
            
                
                    

**POST**

                    
: 
                        

Here's a sample request for the Void Posted Credit Memo action.

                        

```
{
  "inputs": [
    {
      "creditMemoId": "50gSG0000001y5NYAQ"
    }
  ]
}
```

                    

                    
: 
                        

Here's a sample response for the Void Posted Credit Memo action.

                        

```
[
  {
    "actionName": "voidPostedCreditMemo",
    "errors": [],
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "debitMemoId": "4DmSG000001YcIP0A0",
      "statusUrl": "/services/data/v68.0/sobjects/AsyncOperationTracker/16PSG000001qlyL2AQ"
    },
    "sortOrder": -1,
    "version": 1
  }
]
```
