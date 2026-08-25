---
page_id: connect_responses_decision_matrix_result.htm
title: Decision Matrix Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Result

Output representation of the decision matrix details.

      
        
          

**Sample Response**

          
: 
            

```
{
   "code" : "200",
   "id" : "0lIx0000000000zEAA",
   "inputVariables" : [ {
      "dataType" : "Number",
      "id" : "0lJx0000000000zEAA",
      "name" : "IN1"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000010EAA",
      "name" : "IN2"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000011EAA",
      "name" : "IN3"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000012EAA",
      "name" : "IN4"
   } ],
   "isSuccess" : true,
   "message" : "",
   "name" : "DescisionMatrix2",
   "outputVariables" : [ {
      "dataType" : "Text",
      "id" : "0lJx00000000013EAA",
      "name" : "OUT1"
   }, {
      "dataType" : "Text",
      "id" : "0lJx00000000014EAA",
      "name" : "OUT2"
   } ]
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `description` | String | The description of the decision matrix. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the decision matrix record. | Small, 53.0 | 53.0 |
| `inputVariables` | [Decision Matrix Variable[]](./connect_responses_decision_matrix_variable.htm.md) | The list of input variables of the decision matrix. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `name` | String | The name of the decision matrix. | Small, 53.0 | 53.0 |
| `outputVariables` | [Decision Matrix Variable[]](./connect_responses_decision_matrix_variable.htm.md) | The list of output variables of the decision matrix. | Small, 53.0 | 53.0 |
