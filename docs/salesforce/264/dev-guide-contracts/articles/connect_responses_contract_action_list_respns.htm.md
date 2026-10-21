---
page_id: connect_responses_contract_action_list_respns.htm
title: Contract Action List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_action_list_respns.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Contract Action List

List of contract actions.

    

## Properties

      
      

            
            
            
            
            
            
                
                    

                    

                    

                    

                    

                

            

            
                
                    

                    

                    

                    

                    

                

                
                    

                    

                    

                    

                    

                

            

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actions` | [Contract Action[]](./connect_responses_contract_action_respons.htm.md) | Specifies list of actions. | Big, 56.0 | 56.0 |
| `contractId` | String | Indicates ID of the contract. | Small, 56.0 | 56.0 |

    

    

## JSON Example

      
      

```

{
    "actions": [
        {
            "apiName": "cancelContract",
            "uiText": "Cancel Contract"
        },
        {
            "apiName": "submitForApproval",
            "uiText": "Submit for Approval"
        }
    ],
    "contractId": "800RO000000U7FaYAK"
}

```
