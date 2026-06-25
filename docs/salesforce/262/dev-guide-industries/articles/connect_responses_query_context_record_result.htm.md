---
page_id: connect_responses_query_context_record_result.htm
title: Query Context Record Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_query_context_record_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Query Context Record Result

Output representation of query result context record.

Sample Response
:   ```
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
| `queryRecords` | [Context Query Record](./connect_responses_context_query_record.htm.md "Output representation of context query record, including primary and associated child records.")[] | List of the retrieved context query records. | Small, 59.0 | 59.0 |
