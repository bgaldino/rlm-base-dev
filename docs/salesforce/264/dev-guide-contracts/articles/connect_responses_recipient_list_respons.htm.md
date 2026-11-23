---
page_id: connect_responses_recipient_list_respons.htm
title: Recipient List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_recipient_list_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Recipient List

List of recipients.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `recipients` | [Recipient Details[]](./connect_responses_recipient_respons.htm.md "Recipient details.") | List of recipients. | Big, 56.0 | 56.0 |

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_recipient_list_respons.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
