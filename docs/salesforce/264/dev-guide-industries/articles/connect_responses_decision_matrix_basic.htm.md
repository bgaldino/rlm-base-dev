---
page_id: connect_responses_decision_matrix_basic.htm
title: Decision Matrix Basic
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_basic.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Basic

Output representation of the decision matrices
    details.

      
        
          

**Sample Response**

          
: 
            

```
{
   "decisionMatrices" : [ {
      "id" : "0lIx0000000001TEAQ",
      "name" : "Decision_Matrix_Test1"
   } ],
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | The description of the decision matrix. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the decision matrix record. | Small, 53.0 | 53.0 |
| `name` | String | The name of the decision matrix. | Small, 53.0 | 53.0 |
