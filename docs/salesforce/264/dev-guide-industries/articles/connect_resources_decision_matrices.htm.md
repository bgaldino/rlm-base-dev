---
page_id: connect_resources_decision_matrices.htm
title: Decision Matrices
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrices.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrices

Get a list of decision matrices ( also known as calculation matrix)
      based on a search text. The API returns a maximum of ten decision matrices records that
      contain the specified keyword.

**Resource**

: 

```
/connect/omnistudio/decision-matrices
```

        
          

**Example URI**

          
: 
            

```
/services/data/v53.0/connect/omnistudio/decision-matrices?searchKey=Test
```

          

        

**Available version**

: 53.0

**Requires Chatter**

: No

**HTTP methods**

: GET

**Request parameters for GET**

: 

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `searchKey` | String | The user-entered search text to retrieve a list of decision matrices. |  | 53.0 |

**Response body for GET**

: [Decision Matrix Result List](./connect_responses_decision_matrix_result_list.htm.md)
