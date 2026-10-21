---
page_id: connect_resources_contract_risk_analysis.htm
title: Contract Document Risk Analysis
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contract_risk_analysis.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# Contract Document Risk Analysis

Start an asynchronous risk analysis for a contract document version,
    or get the status and results of the most recent risk analysis run.

    

## Resource

      
      

```
/connect/contracts-ai/contract-document-version/$CONTRACT_DOCUMENT_VERSION_ID/risk-analysis
```

    

    

## Available Version

      
      

68.0

    

    

## HTTP Methods

      
      

GET, POST

    

    

## Request Parameters

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractDocument​VersionId` | String | ID of the contract document version to analyze. | Required | 68.0 |
| `contractRisk​AnalysisRunId` | String | ID of the contract risk analysis run. Available for GET only. If omitted, the response returns the most recent risk analysis run for the contract document version. | Optional | 68.0 |

    

    

## Example for POST

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/contracts-ai/contract-document-version/0qtRM0000004CGv/risk-analysis
```

    

    

## Request Body for POST

      
      

**JSON Example**

      

```
{
  "documentPlaybookVersionId" : "00OEE000003530L2AQ"
}
```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `documentPlaybook​VersionId` | String | ID of the playbook version to use for risk analysis standards and comparison. | Optional | 68.0 |

    

    

## Response Body for POST

      
      

[Contract Risk Analysis Run](./connect_responses_contract_risk_analysis_run_output.htm.md)

    

    

## Example for GET

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/contracts-ai/contract-document-version/0qtRM0000004CGv/risk-analysis
```

    

    

## Response Body for GET

      
      

[Contract Risk Analysis Run](./connect_responses_contract_risk_analysis_run_output.htm.md)
