---
page_id: connect_responses_decision_model_export_output.htm
title: Decision Model Export Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_model_export_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Model Export Output

Output representation of a completed DMN (Decision Model Notation)
      export request.

      
        
          

**JSON example**

          
: 
            

```
{
   "message":"OK",
   "success":true,
   "errors":[
      {
         "errorCode":"BAD_REQUEST",
         "errorMessage":"We couldn’t find this record. Specify a valid ID for decisionModelEntityIds parameter.",
         "recordId":"0lNRO00000004fsdfAA"
      }
   ]
}
```

          

        
      

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Decision Model Export Error](./connect_responses_decision_model_export_error.htm.md)[] | List of errors corresponding to a failed export request. | Small, 58.0 | 58.0 |
| `message` | String | Response message from the completed export request. | Small, 58.0 | 58.0 |
| `success` | Boolean | Indicates whether the export request was successful (`true`) or not (`false`). | Small, 58.0 | 58.0 |
