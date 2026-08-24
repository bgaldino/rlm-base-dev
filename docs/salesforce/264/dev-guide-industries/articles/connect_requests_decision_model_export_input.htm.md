---
page_id: connect_requests_decision_model_export_input.htm
title: Decision Model Export Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_model_export_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Model Export Input

Input representation of the request to export decision matrix
      data.

**JSON example**

: 

```
{
   "decisionModelEntityIds":[
      “0lNRO00000004f72AA”,
      “0lNRO000000rfn27AA”
   ]
}
```

**Properties**

: 

                    

                    

                    

                    

                    

                  

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `decision​Model​EntityIds` | String[] | A list of decision matrix version IDs to export data from. | Required | 58.0 |
