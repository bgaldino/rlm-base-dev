---
page_id: connect_responses_decision_matrix_result_list.htm
title: Decision Matrix Result List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_result_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix Result List

Output representation of the decision matrix result
list.

Sample Response
:   ```
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
| `decisionMatrices` | [Decision Matrix Basic[]](./connect_responses_decision_matrix_basic.htm.md "Output representation of the decision matrices details.") | The list of the decision matrices. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
