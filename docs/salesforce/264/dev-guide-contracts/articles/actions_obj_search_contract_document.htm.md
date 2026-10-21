---
page_id: actions_obj_search_contract_document.htm
title: Search Contract Document Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/actions_obj_search_contract_document.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_invocable_actions_parent.htm
fetched_at: 2026-10-13
---

# Search Contract Document Action

Search the latest contract document version based on the user's
            query.

        
            

This action is available in API version 64.0 and later.

        

        

## Special Access Rules

            
            

To use this action, Contracts AI User permission set is required.

        

        

## Supported REST HTTP Methods

            
            

**URI:** `/services/data/v68.0/actions/standard/searchContractDocument`

            

**Formats:** JSON, XML

            

**HTTP Methods:** POST

            

**Authentication:** `Authorization: Bearer TOKEN`

        

        

## Inputs

            
            

                    
                    
                    
                    
                        
                            

                            

                            

                        

                    

                    
                        
                            

                            

                            

                        

                        
                            

                            

                            

                        

                        
                            

                            

                            

                        

                    

                
| Input | Type | Description |
| --- | --- | --- |
| contractId | string | Required. ID of the contract record to use for the search. |
| searchQuery | string | Required. Text-based query to use to search contract documents. |
| resultLimit | string | Required. Maximum number of text segments that can be returned from the contract search. Each segment represents a relevant portion of a contract document. |

        

        

## Outputs

            
            

                    
                    
                    
                    
                        
                            

                            

                            

                        

                    

                    
                        
                            

                            

                            

                        

                    

                
| Output | Type | Description |
| --- | --- | --- |
| searchResult | string | Concatenated content of the top segments that match a user query. |

        

        

## Example

            
            

**POST**

            

This sample request is for the Search Contract Document action.

            

```
{
  "inputs": [
    {
      "contractId": "800VW000006142vYAA",
      "searchQuery": "Show me the contract for paper packaging deliveries.",
      "resultLimit": "1000"
    }
  ]
}
```

            

This sample response is for the Search Contract Document action.

            

```
{
  "actionName": "searchContractDocument",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outcome": null,
  "outputValues": {
    "searchResult": "AGREEMENT FOR DELIVERY OF PAPER PACKAGING MATERIALS\n\nThis Agreement...."
  },
  "sortOrder": -1,
  "version": 1
}
```
