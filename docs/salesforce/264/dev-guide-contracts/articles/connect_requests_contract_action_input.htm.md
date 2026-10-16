---
page_id: connect_requests_contract_action_input.htm
title: Contract Action Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_contract_action_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Contract Action Input

Input to get action details for the contract.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `actionApiName` | String | API name for respective contract action. | Optional | 57.0 |
| `actionId` | String | ID for Object state Action Definition record. For the list of all standard actions supported, refer [Predefined Dynamic (Contract) Actions](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_Predefined_Contract_Actions.htm&type=5&language=en_US). | Optional | 57.0 |
| `actionData` | Map<String, String> | Action body with supported format string. | Optional | 57.0 |

      

#### Note

For any request, either `actionApiName` or `actionId` must be passed. If none passed, the application raises an exception.

    

    

## JSON Example

      
      

```

{
    "actionApiName" : "updateEnvelopeStatus",
...."actionId" : //object state action definition id,
    "actionData":{
        "isUpdateEnvelopeStatusSuccess": true
    }
}
```
