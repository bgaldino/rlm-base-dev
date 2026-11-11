---
page_id: connect_requests_contract_risk_analysis_input.htm
title: Contract Risk Analysis Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_contract_risk_analysis_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Contract Risk Analysis Input

Input representation to start a risk analysis for a contract
      document version.

    

## Properties

      
      

            
            
            
            
            
            
              
                

                

                

                

                

              

            

            
              
                

                

                

                

                

              

            

          
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentPlaybook​VersionId` | String | ID of the playbook version to use for risk analysis standards and comparison. | Optional | 68.0 |

    

    

## JSON Example

      
      

```
{
  "documentPlaybookVersionId" : "00OEE000003530L2AQ"
}
```
