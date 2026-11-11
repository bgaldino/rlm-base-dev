---
page_id: connect_responses_save_external_document.htm
title: Save External Document Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_save_external_document.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Save External Document Output

Output representation for save external document
    operation.

    

## Properties

      
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of an external document. | Small, 58.0 | 58.0 |
| `isSuccess` | Boolean | The isSuccess flag for save external document operation. | Small, 58.0 | 58.0 |
| `message` | String | The response message for save external document. | Small, 58.0 | 58.0 |

    

    

## JSON Example

      
      

```

{
   "id":"XXXXXXXX",
    "isSuccess":true,
   "message":"XYZ"
}

```
