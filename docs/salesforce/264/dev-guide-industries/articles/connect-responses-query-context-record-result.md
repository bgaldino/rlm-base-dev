---
page_id: connect-responses-query-context-record-result
title: Query Context Record Result
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-context-record-result.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-apis-responses
legacy_page_id: connect_responses_query_context_record_result.htm
fetched_at: 2026-11-25
---

# Query Context Record Result

Output representation of query result context record.

**Sample Response**

: 

```
{
   "contextId":"7bc695bc-f38b-4a94-8a95-0caa50f3da53",
   "isDone":true,
   "isSuccess":true,
   "queryRecords":[
      {
         "childQueryRecords":[

         ],
         "record":{
            "attributesAndValues":{
               "Name":"Acme Corp",
               "BillingAddress":"{city:New York,country:USA,geocodeAccuracy:null,latitude:null,longitude:null,postalCode:31349,state:NY,street:10 Main Rd.}",
               "Industry":"Manufacturing",
               "Type":"Prospect"
            },
            "businessObjectType":"Account",
            "childBusinessObjectTypes":[
               "OpportunityItem",
               "OrderItem"
            ],
            "contextDataRecordId":"003xx000004WhFsAAK",
            "currentState":"CREATED",
            "lastUpdatedTimeStamp":"2023-10-11 04:46:13.804"
         }
      }
   ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID for the context record that is queried. | Small, 59.0 | 59.0 |
| `isDone` | Boolean | Indicates whether the query operation is complete `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the status of query is successful `(true)` or not `(false)`. | Small, 59.0 | 59.0 |
| `queryRecords` | [Context Query Record](./connect-responses-context-query-record.md)[] | List of the retrieved context query records. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-query-context-record-result.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
