---
page_id: connect_responses_contract_risk_analysis_finding_output.htm
title: Contract Risk Analysis Finding
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_risk_analysis_finding_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Contract Risk Analysis Finding

Output representation of the risk analysis for a document element, capturing the identified risk, how the element compares to the playbook, and the recommended remediation.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actualText` | String | Actual clause text from the counterparty document. | Big, 68.0 | 68.0 |
| `confidence​Reason` | String | Short explanation of why the confidence score was assigned. | Big, 68.0 | 68.0 |
| `confidence​Score` | Double | Confidence in the risk determination. | Big, 68.0 | 68.0 |
| `contract​Risk​Analysis​FindingId` | String | Unique ID of the contract risk analysis finding record. | Big, 68.0 | 68.0 |
| `deviationSummary` | String | Brief description of what deviated and why it matters. | Big, 68.0 | 68.0 |
| `explanation` | String | Detailed reasoning for the risk determination, written in plain language for non-legal reviewers. | Big, 68.0 | 68.0 |
| `fallbackText` | String | Playbook's acceptable alternate language. | Big, 68.0 | 68.0 |
| `matchType` | String | How the element's actual text compares to the playbook standard. Valid values are `Preferred`, `Fallback`, `NonStandard`, `Missing`, or `NotDetected`. | Big, 68.0 | 68.0 |
| `preferredText` | String | Playbook's preferred clause language for this element type. | Big, 68.0 | 68.0 |
| `redline​Suggestion` | String | Alternative language that the reviewer can apply directly to the document to remediate the identified risk. | Big, 68.0 | 68.0 |
| `riskScore` | Double | Risk score from 0 through 100. Higher values indicate greater risk exposure. | Big, 68.0 | 68.0 |
| `severity` | String | Risk severity classification for this finding. Valid values are `Low`, `Medium`, `High`, or `Critical`. | Big, 68.0 | 68.0 |
| `status` | String | Current review status of this finding, set by the reviewer. Valid values are `Pending`, `InReview`, `RedlineApplied`, or `RiskAccepted`. | Big, 68.0 | 68.0 |

    

    

## JSON Example

      
      

```
{
  "contractRiskAnalysisFindingId": "1dwRM0000001AAA",
  "severity": "Critical",
  "riskScore": 95.0,
  "confidenceScore": 0.97,
  "matchType": "NonStandard",
  "actualText": "Liability of either party shall not exceed one hundred thousand dollars ($100,000).",
  "status": "Pending"
}
```
