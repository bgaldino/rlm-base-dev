---
page_id: connect_responses_context_data_record.htm
title: Context Data Record
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_data_record.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Data Record

Output representation of context data record, including its attributes, type, associated
child objects, and other relevant metadata.

Sample Response
:   ```
    {
                "childQueryRecords": [
                    {
                        "childQueryRecords": [],
                        "record": {
                            "attributesAndValues": {
                                "Name": "Acme Corp",
                                "BillingAddress": "{city:New York,country:USA,geocodeAccuracy:null,latitude:null,longitude:null,postalCode:31349,state:NY,street:10 Main Rd.}",
                                "Industry": "Manufacturing",
                                "Type": "Prospect"
                            },
                            "businessObjectType": "Account",
                            "childBusinessObjectTypes": [
                                "OpportunityItem",
                                "OrderItem"
                            ],
                            "contextDataRecordId": "003xx000004WhFsAAK",
                            "currentState": "CREATED",
                            "lastUpdatedTimeStamp": "2023-10-11 04:46:13.804"
                        }
                    }
                ]
            }
        ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributesAndValues` | Map<String, Object> | Mapping of attributes to their corresponding values within the context. | Small, 59.0 | 59.0 |
| `businessObjectType` | String | Type of business object. | Small, 59.0 | 59.0 |
| `childBusinessObjectTypes` | String[] | List indicating types of child business objects. | Small, 59.0 | 59.0 |
| `contextDataRecordId` | String | Unique ID of the context data record. | Small, 59.0 | 59.0 |
| `currentState` | String | The current status of the context data record. | Small, 59.0 | 59.0 |
| `lastUpdatedTimeStamp` | String | The last updated time stamp of context data record. | Small, 59.0 | 59.0 |
