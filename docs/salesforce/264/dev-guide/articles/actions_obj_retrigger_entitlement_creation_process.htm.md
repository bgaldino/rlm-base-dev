---
page_id: actions_obj_retrigger_entitlement_creation_process.htm
title: Retrigger Entitlement Creation Process Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_retrigger_entitlement_creation_process.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Retrigger Entitlement Creation Process Action

Retrigger entitlement creation process for failed or unprocessed
            assets.

        

Trigger the entitlement creation process again in these scenarios.

                
- Process failed assets in the asset to entitlement journey.

                
- Assetize or create wallets for assets without corresponding records in Usage
                    Management.

            

This action is available in API version 65.0 and later.

        

## Special Access Rules

            
            

The Retrigger Entitlement Creation Process action is available in Enterprise,
                Developer, and       Unlimited Editions where Usage Management is enabled. To use
                this action, you need the Usage       Management Run Time User permission.

        

        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: `/services/data/v68.0/actions/standard/retriggerEntlCreaProc`

                
                
                    

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
| assetId | **Type** string **Description** Required. ID of the asset for which you want to trigger the asset to entitlement process again. |

        

        

## Outputs

None.

        
        

## Example

            
            
                
                    

**POST**

                    
: 
                        

Here's a sample request for the Retrigger Entitlement Creation Process
                            action.

                        

```
{
  "inputs": [
    {
      "assetId": "02iSB000000JzZFYA0"
    }
  ]
}
```

                    

                    
: 
                        

Here's a sample response for the Retrigger Entitlement Creation Process
                            action.

                        

```
[
  {
    "actionName": "retriggerEntlCreaProc",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": null,
    "sortOrder": -1,
    "version": 1
  }
]
```
