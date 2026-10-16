---
page_id: connect_responses_calculation_procedure_list_output.htm
title: Calculation Procedure List Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_list_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Calculation Procedure List Output

Output representation of the expression set result
    list.

      

#### Note

This API has been deprecated as of API version 55.0.
        In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

      
        
          

**Sample Response**

          
: 
            

```
{
   "calculationProcedures" : [ {
      "id" : "0k0x0000000008ZAAQ",
      "description" : "Test calculation set",
      "name" : "Expression_Set_1"
   },{
      "id" : "0k0x000000000BQAAY",
      "description" : "Test procedure set",
      "name" : "Expression_Set_2"
   } ],
   "code" : "200",
   "isSuccess" : true,
   "message" : ""
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `calculationProcedures` | [Calculation Procedure Output[]](./connect_responses_calculation_procedure_output.htm.md) | The list of the expression sets. | Small, 53.0 | 53.0 |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `success` | Boolean | Indicates whether the request was successful. | Small, 53.0 | 53.0 |
