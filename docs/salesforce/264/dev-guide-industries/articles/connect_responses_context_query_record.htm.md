---
page_id: connect_responses_context_query_record.htm
title: Context Query Record
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_query_record.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Query Record

Output representation of context query record, including primary and associated child
    records.

      
        
          

**Sample Response**

          
: 
            

```
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
| `childQueryRecords` | [Context Query Record](#connect_responses_context_query_record) | List of child query records derived from the main context query. | Small, 59.0 | 59.0 |
| `record` | [Context Data Record](./connect_responses_context_data_record.htm.md) | The context data record obtained from the query. | Small, 59.0 | 59.0 |
