---
page_id: actions_obj_update_context_attributes.htm
title: Update Context Attributes Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_update_context_attributes.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Update Context Attributes Action

Update the attributes in the context instance using tags.

        
            

This action is available in API version 63.0 and later.

        

        

## Special Access Rules

            
            

Available in Developer, Enterprise, Professional, and Unlimited editions for
                Industries clouds where Context Service is enabled.

        

        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: 
`/services/data/v`59.0`/actions/standard/updateContextAttributes`

                
                
                    

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
| contextId | **Type** string **Description** Required. ID of the context instance. |
| nodePathAndUpdatedValues | **Type** string **Description** Optional. The JSON containing the node path and its updated values. |

        

        

## Outputs

None.

        
        

## Example

            
            
                
                    

**POST**

                    
: 
                        

This sample request is for the Update Context Attributes action.

                        

```
{
  "inputs": [
    {
      "contextId": "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609",
      "NodePathAndUpdatedValues": [
        {
          "nodePath": {
            "dataPath": [
              "account1",
              "contact1"
            ]
          },
          "tagValues": [
            {
              "tagName": "Contact_LastName",
              "tagValue": "UPDATED_MILLER"
            }
          ]
        }
      ]
    }
  ]
}
```
