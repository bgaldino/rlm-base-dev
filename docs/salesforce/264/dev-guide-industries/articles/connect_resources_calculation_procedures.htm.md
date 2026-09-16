---
page_id: connect_resources_calculation_procedures.htm
title: Calculation Procedures
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedures.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedures

Get a list of expression sets (also known as calculation procedure)
      based on a search text. The API returns a maximum of ten expression set records that contain
      the specified keyword.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

**Resource**

: 

```
/connect/omnistudio/evaluation-services
```

        
          

**Example URI**

          
: 
            

```
/services/data/v53.0/connect/omnistudio/evaluation-services?searchKey=Expression
```

          

        

**Available version**

: 53.0

**Requires Chatter**

: No

**HTTP methods**

: GET

**Request parameters for GET**

: 

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `searchKey` | String | The user-entered search text to retrieve a list of expression sets. | Required | 53.0 |

**Response body for GET**

: [Calculation Procedure List Output](./connect_responses_calculation_procedure_list_output.htm.md)
