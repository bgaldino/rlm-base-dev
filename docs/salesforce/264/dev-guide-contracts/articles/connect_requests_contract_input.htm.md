---
page_id: connect_requests_contract_input.htm
title: Contract Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_contract_input.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Contract Input

Input to create and update contract.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isAutoDocgenRequired` | Boolean | Specifies whether automatic document generation is required or not. | Required | 56.0 |
| `recordTypeName` | String | Contract record type name. | Optional | 56.0 |
| `sourceObjectId` | String | Source record ID. | Required | 56.0 |
| `templateName` | String | Document template name for document generation. | Optional | 56.0 |

    

    

## JSON Example for Creating and Updating Contract

      
      

```

{
"sourceObjectId" : "006xx000001a4KaAAI",
"templateName" : "Value1",
"isAutoDocgenRequired" :true/false
}
```
