---
page_id: connect_resources_decision_matrix.htm
title: Decision Matrix
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrix.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix

Retrieve the details for a given decision matrix record (also known as
      calculation matrix).

**Resource**

: 

```
/connect/omnistudio/decision-matrices/${matrixId}
```

        
          

**Example URI**

          
: 
            

```
/services/data/v53.0/connect/omnistudio/decision-matrices/0lIx0000000000zEAA
```

          

        

**Available version**

: 53.0

**Requires Chatter**

: No

**HTTP methods**

: GET

**Response body for GET**

: [Decision Matrix Result](./connect_responses_decision_matrix_result.htm.md)
