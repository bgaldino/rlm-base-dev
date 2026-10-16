---
page_id: connect_resources_calculation_procedure.htm
title: Calculation Procedure
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedure.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedure

Retrieve the details for a given expression set (also known as
      calculation procedure) record.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

          

**Resource**

          
: 
            

```
/connect/omnistudio/evaluation-services/${id}
```

          

        
        
          

**Example**

          
: 
            

```
/services/data/v53.0/connect/omnistudio/evaluation-services/0k0x000000000BQAAY
```

          

        

**Available version**

: 53.0

**Requires Chatter**

: No

**HTTP methods**

: GET

**Response body for GET**

: [Calculation Procedure Detail Output](./connect_responses_calculation_procedure_detail_output.htm.md)
