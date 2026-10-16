---
page_id: connect_responses_contract_risk_analysis_run_output.htm
title: Contract Risk Analysis Run
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_risk_analysis_run_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Contract Risk Analysis Run

Output representation of the status and results of a contract document version risk analysis run.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `completedAt` | Date | Timestamp at which the run reached a terminal state. | Big, 68.0 | 68.0 |
| `contractDocument​VersionId` | String | ID of the contract document version against which the risk analysis was performed. | Big, 68.0 | 68.0 |
| `contractRisk​AnalysisElements` | [Contract Risk Analysis Element[]](./connect_responses_contract_risk_analysis_element_output.htm.md) | List of completed document elements processed in this analysis run. | Big, 68.0 | 68.0 |
| `contract​Risk​Analysis​RunId` | String | ID of the contract risk analysis run record that represents this analysis. | Big, 68.0 | 68.0 |
| `documentContext` | String | Extracted summary of the contract document used as context for AI-driven risk analysis of individual clauses. | Big, 68.0 | 68.0 |
| `error` | [Contract Risk Analysis Error](./connect_responses_contract_risk_analysis_error_output.htm.md) | Error code and error message when the API request is unsuccessful. | Big, 68.0 | 68.0 |
| `initiatedById` | String | ID of the user who initiated the run. | Big, 68.0 | 68.0 |
| `overallScore` | Double | Aggregate risk score for the run, computed as the average of all finding risk scores. Ranges from 0 through 100, where a higher value indicates greater risk. Populated only when the run is completed. | Big, 68.0 | 68.0 |
| `overallSeverity` | String | Highest severity across all findings produced in this run. Valid values are `Low`, `Medium`, `High`, or `Critical`. | Big, 68.0 | 68.0 |
| `processed​ElementCount` | Integer | Number of elements completed so far, whether analysis finished successfully or failed. Use this value to render a progress indicator. Equals `totalElementCount` when the run is completed. | Big, 68.0 | 68.0 |
| `startedAt` | Date | Timestamp at which the run began change detection. | Big, 68.0 | 68.0 |
| `status` | String | Current lifecycle state of the analysis run. Valid values are `New`, `Skipped`, `Running`, `Completed`, or `Failed`. | Big, 68.0 | 68.0 |
| `success` | Boolean | Indicates whether the API request was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |
| `summary` | String | Executive summary of all findings, for a quick review of the document's risk posture without drilling into individual clauses. Populated only when the run is completed. | Big, 68.0 | 68.0 |
| `totalElement​Count` | Integer | Total number of elements for this run. Populated after change detection completes. | Big, 68.0 | 68.0 |

    

    

## JSON Example

      
      

```
{
  "contractRiskAnalysisRunId": "1gMRM0000004DBq",
  "contractDocumentVersionId": "0qtRM0000004CGv",
  "initiatedById": "005xx000001X8B7AAK",
  "status": "Completed",
  "startedAt": "2026-05-04T09:48:12Z",
  "completedAt": "2026-05-04T09:52:41Z",
  "totalElementCount": 2,
  "processedElementCount": 2,
  "overallScore": 82.0,
  "overallSeverity": "Critical",
  "summary": "Document contains 1 critical liability cap reduction and 1 high-risk governing law change.",
  "documentContext": "Master services agreement covering liability, indemnification, and governing law provisions.",
  "success": true,
  "contractRiskAnalysisElements": [
    {
      "contractRiskAnalysisElementId": "1WJRM0000001AAA",
      "elementName": "Limitation of Liability",
      "processingStage": "Persist",
      "processingStatus": "Completed",
      "elementType": "Clause",
      "contractRiskAnalysisFinding": {
        "contractRiskAnalysisFindingId": "1dwRM0000001AAA",
        "severity": "Critical",
        "riskScore": 95.0,
        "matchType": "NonStandard",
        "actualText": "Liability of either party shall not exceed one hundred thousand dollars ($100,000).",
        "status": "Pending"
      }
    }
  ]
}
```
