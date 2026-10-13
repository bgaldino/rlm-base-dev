---
page_id: connect_responses_recipient_list_respons.htm
title: Recipient List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_recipient_list_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Recipient List

List of recipients.

    

## Properties

      
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recipients` | [Recipient Details[]](./connect_responses_recipient_respons.htm.md) | List of recipients. | Big, 56.0 | 56.0 |

    

    

## JSON Example

      
      

```

{
    "recipients":[
                        {
                            "id": "xxxx",
                            "name": "somename",
                            "email": "someemail",
                            "additionalFields": {
                                "key1": "value1"
                            }
                        },
                        ..............................
                        {
                            "id": "yyyy",
                            "name": "somename1",
                            "email": "someemail1",
                            "additionalFields": {
                                "key1": "value1"
                            }
                        }
                ]
}
```
