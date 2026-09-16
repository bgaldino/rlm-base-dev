---
page_id: connect_responses_decision_matrix_result_list.htm
title: Decision Matrix Result List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_result_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Result List

Output representation of the decision matrix result
    list.

      
        
          

**Sample Response**

          
: 
            

```
{
   "code" : "200",
   "decisionMatrices" : [ {
      "id" : "0lIx0000000001TEAQ",
      "name" : "Decision_Matrix_Test1"
   }, {
      "id" : "0lIx0000000000pEAA",
      "name" : "Decision_Matrix_Test2”
   }, {
      "id" : "0lIx0000000001OEAQ",
      "name" : "Decision_Matrix_Test3”
   } ],
   "isSuccess" : true,
   "message" : ""
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `decisionMatrices` | [Decision Matrix Basic[]](./connect_responses_decision_matrix_basic.htm.md) | The list of the decision matrices. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
