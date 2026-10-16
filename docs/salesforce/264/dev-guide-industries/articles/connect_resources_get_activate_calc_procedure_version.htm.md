---
page_id: connect_resources_get_activate_calc_procedure_version.htm
title: Calculation Procedure Version Definition (Activate, Get)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_get_activate_calc_procedure_version.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedure Version Definition (Activate, Get)

Retrieve the definition of an expression set (also known as
      calculation procedure) version record. Activate an expression set version
    record.

    
      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

      
        
          

**Resource**

          
: 
            

```
/connect/omnistudio/evaluation-services/version-definitions/${id}
```

          

        
        
          

**Example**

          
: 
            

```
/services/data/v53.0/connect/omnistudio/evaluation-services/
version-definitions/0lIxx000000001dEAA
```

          

        
        
          

**Available version**

          
: 53.0

        
        
          

**Requires Chatter**

          
: No

        
        
          

**HTTP methods**

          
: GET, PATCH

        
        
          

**Response body for GET**

          
: [Calculation Procedure Version Definition Output](./connect_responses_calculation_procedure_version_definition_output.htm.md)

        
        
          

**Response body for PATCH**

          
: [Calculation Procedure Activation Output](./connect_responses_calculation_procedure_activation_output.htm.md)
