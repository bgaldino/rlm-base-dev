---
page_id: actions_obj_delete_context_records.htm
title: Delete Context Records Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/actions_obj_delete_context_records.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_invocable_actions_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Delete Context Records Action

Deletes one or more records from a context instance.

        
            

This action is available in API version 67.0 and later.

        

        

## Special Access Rules

            
            

Available in Developer, Enterprise, Professional, and Unlimited editions for
                Industries clouds where Context Service is enabled.

        

        

## Supported REST HTTP Methods

            
            
                
                    

**URI**

                    
: 
`/services/data/v`68.0`/actions/standard/deleteContextRecords`

                
                
                    

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

                        

                        
                            

                            

: 

: 

                        

                    

                
| Input | Details |
| --- | --- |
| contextId | **Type** string **Description** Required. ID of the context instance from which records are deleted. |
| dataPaths | **Type** List<String> **Description** Required. A collection of data path objects that identify the records to delete from the context instance. Each object contains a `dataPath` field whose value is a list of strings representing the hierarchical path from the root to the target record in the context. |
| isPermanent​Delete | **Type** boolean **Description** Optional. Indicates whether the record is permanently deleted (`true`) or not (`false`). The default value is `false`. |

        

        

## Usage

            
            

Use this action to delete one or more records from a context instance. By default,
                records are soft deleted. To permanently delete the records, set `isPermanentDelete` to `true`.

        

        

## Example

            
            
                
                    

**POST**

                    
: 
                        

This sample request is for the Delete Context Records action.

                        

```
{
  "inputs": [
    {
      "contextId": "0000000a07da091002517526756248297be68492e6b442e8ad80182d518e45aa",
      "dataPaths": [
        { "dataPath": ["001xx000003GbMhAAK", "003xx000004Wia5AAC"] }
      ],
      "isPermanentDelete": false
    }
  ]
}
```

                    

                    
: 
                        

This sample response is for the Delete Context Records action.

                        

```
[
  {
    "actionName": "deleteContextRecords",
    "errors": null,
    "isSuccess": true,
    "outputValues": {}
  }
]
```
