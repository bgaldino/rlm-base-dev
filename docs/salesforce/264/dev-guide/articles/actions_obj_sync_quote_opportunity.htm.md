---
page_id: actions_obj_sync_quote_opportunity.htm
title: Sync Quote to Opportunity Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_sync_quote_opportunity.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-09-29
---

# Sync Quote to Opportunity Action

Sync quote line items to the matching opportunity line items so that forecasts stay up to date.

    
      

This action is available in API version 68.0 and later.

    

    

## Special Access Rules

      
      

The sync Quote to Opportunity action is available in Developer, Enterprise, and Unlimited Editions of Revenue Management.

      

To use this action in a flow or other automation, in Revenue Settings, turn on **Asynchronous Opportunity Sync**.

    

    

## Supported REST HTTP Methods

      
      

**URI:** `/services/data/v68.0/actions/standard/syncQuoteOpportunity`

      

**Formats:** JSON

      

**HTTP Methods:** POST

      

**Authentication:** `Authorization: Bearer token`

    

    

## Inputs

      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

          

        
| Input | Type | Description |
| --- | --- | --- |
| quoteId | string | Required. The ID of the quote record to sync with an opportunity. Specify only one quote ID. |

    

    

## Outputs

      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

          

        
| Output | Type | Description |
| --- | --- | --- |
| aotId | string | The asynchronous operation tracker ID for monitoring the sync process. |
| errorCode | string | The error code when isSuccess is false. The value is null when the process is successful. |
| errorMessage | string | The error description when isSuccess is false. The error description is an empty string when the process is successful. |
| isSuccess | boolean | Indicates whether the sync completed successfully ( `true` ), or whether the validation failed or the asynchronous job couldn't be enqueued ( `false` ). |

    

    

## Example

      
      
      

**POST**

      

This sample request is for the Sync Quote to Opportunity action.

      

```
{
  "inputs": [
    {
      "quoteId": "0Q0RO0000003LyU"
    }
  ]
}
```

      

This sample response is for the Sync Quote to Opportunity action.

      

```
[
  {
    "actionName": "syncQuoteOpportunity",
    "errors": null,
    "isSuccess": true,
    "outputValues": {
      "aotId": "16PLT0000028ltR2AQ",
      "errorCode": null,
      "errorMessage": "",
      "isSuccess": true
    }
  }
]
```
