---
page_id: connect_requests_envelope_void_reques.htm
title: Envelope Void Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_requests_envelope_void_reques.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_requests.htm
fetched_at: 2026-10-13
---

# Envelope Void Input

Input to get void envelope related details.

    

## Properties

      
      

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `senderEmail` | String | Refers to the email of the user who initiated the voiding. | Optional | 56.0 |
| `voidedReason` | String | Reason for which the envelope is being voided. | Required | 56.0 |

    

    

## JSON Example

      
      

```

{
    "voidedReason": "",//required
    "senderEmail": ""
}
```
