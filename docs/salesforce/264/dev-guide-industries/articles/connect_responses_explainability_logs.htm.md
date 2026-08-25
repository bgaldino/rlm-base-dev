---
page_id: connect_responses_explainability_logs.htm
title: Explainability Logs
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_logs.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Explainability Logs

Output representation of the list of explainability action
    logs.

      
        
          

**JSON example**

          
: 
            

```
{
  "actionLogs": [
    {
      "actionContextCode": "001x0000005SdzIAAS",
      "actionLog": "{This is a sample action log data.}",
      "applicationLogDate": "Mon Aug 01 10:29:35 GMT 2022",
      "applicationSubtype": "ASD1",
      "applicationType": "0",
      "name": "EAD1",
      "processType": "BPT1"
    }
  ],
  "queryMore": " "
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actionLogs` | [Explainability Log Detail](./connect_responses_explainability_log_detail.htm.md)[] | The list of explainability logs that matches the search criteria. | Small, 56.0 | 56.0 |
| `queryMore` | String | A string that can be passed to the next call to fetch the next batch of explainability log records. | Small, 56.0 | 56.0 |
