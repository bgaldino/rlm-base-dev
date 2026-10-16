---
page_id: connect_responses_contract_risk_analysis_element_output.htm
title: Contract Risk Analysis Element
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_risk_analysis_element_output.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Contract Risk Analysis Element

Output representation of an individual document element extracted and processed during risk analysis, including its content and the risk finding.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `changeType` | String | How this element changed relative to the prior version. Valid values are `Added`, `Modified`, `Deleted`, or `Extracted`. | Big, 68.0 | 68.0 |
| `completedAt` | Date | Timestamp at which this element reached a terminal processing state, either completed or failed. | Big, 68.0 | 68.0 |
| `content​ControlId` | String | Microsoft Word content control identifier used for change tracking and cross-run deduplication. | Big, 68.0 | 68.0 |
| `contentHash` | String | Hash of the element content used for change detection and cross-run deduplication. | Big, 68.0 | 68.0 |
| `contractRisk​Analysis​ElementId` | String | Unique ID of the contract risk analysis element record. | Big, 68.0 | 68.0 |
| `contract​RiskAnalysis​Finding` | [Contract Risk Analysis Finding](./connect_responses_contract_risk_analysis_finding_output.htm.md) | Risk finding produced for this element. | Big, 68.0 | 68.0 |
| `currentText` | String | Element text in the current document version. Populated when `changeType` is `Added` or `Modified`, and suppressed for deleted elements. | Big, 68.0 | 68.0 |
| `elementContext` | String | Surrounding context for this element. | Big, 68.0 | 68.0 |
| `elementIdentifier` | String | Human-readable location of this element in the document. | Big, 68.0 | 68.0 |
| `elementName` | String | Display name of this document element. | Big, 68.0 | 68.0 |
| `elementType` | String | Type of document component analyzed. Valid values are `Clause`, `Section`, or `Other`. | Small, 68.0 | 68.0 |
| `errorDetails` | String | Details of the error encountered during processing, if any. | Big, 68.0 | 68.0 |
| `isFinding​Reused` | Boolean | Indicates whether the element reuses findings from a previous analysis because the contract content has not changed (`true`) or not (`false`). | Small, 68.0 | 68.0 |
| `llmResponseRaw` | String | Raw model output before parsing into structured finding fields. | Big, 68.0 | 68.0 |
| `playbookContext` | String | Retrieved playbook standards used for comparison against the element. | Big, 68.0 | 68.0 |
| `playbookVersionId` | String | ID of the playbook version used when analyzing this element. | Big, 68.0 | 68.0 |
| `previousText` | String | The element text from the prior document version. Populated when `changeType` is `Modified` or `Deleted`, and suppressed for added elements. | Big, 68.0 | 68.0 |
| `processingStage` | String | Processing stage of this element. Valid values are `Started`, `QueryGen`, `Retrieval`, `RiskAnalysis`, or `Persist`. | Big, 68.0 | 68.0 |
| `processingStatus` | String | Processing status of the element at its current stage. Valid values are `Queued`, `Running`, `Completed`, or `Failed`. | Big, 68.0 | 68.0 |
| `retrievalQuery` | String | Generated query used to fetch matching playbook standards for this element. | Big, 68.0 | 68.0 |
| `startedAt` | Date | Timestamp at which processing began for this element. | Big, 68.0 | 68.0 |

    

    

## JSON Example

      
      

```
{
  "contractRiskAnalysisElementId": "1WJRM0000001AAA",
  "elementName": "Limitation of Liability",
  "processingStage": "RiskAnalysis",
  "processingStatus": "Completed",
  "elementType": "Clause",
  "changeType": "Modified",
  "elementContext": "Appears in the General Terms and Conditions, between the Indemnification and Governing Law clauses.",
  "contractRiskAnalysisFinding": {
    "contractRiskAnalysisFindingId": "1dwRM0000001AAA",
    "severity": "Critical",
    "riskScore": 95.0,
    "status": "Pending"
  }
}
```
