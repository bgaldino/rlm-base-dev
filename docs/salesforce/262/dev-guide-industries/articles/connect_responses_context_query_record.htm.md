---
page_id: connect_responses_context_query_record.htm
title: Context Query Record
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_query_record.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Query Record

Output representation of context query record, including primary and associated child
records.

Sample Response
:   ```
    {
       "childQueryRecords":[
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
| `childQueryRecords` | [Context Query Record](#connect_responses_context_query_record "Output representation of context query record, including primary and associated child records.") | List of child query records derived from the main context query. | Small, 59.0 | 59.0 |
| `record` | [Context Data Record](./connect_responses_context_data_record.htm.md "Output representation of context data record, including its attributes, type, associated child objects, and other relevant metadata.") | The context data record obtained from the query. | Small, 59.0 | 59.0 |
