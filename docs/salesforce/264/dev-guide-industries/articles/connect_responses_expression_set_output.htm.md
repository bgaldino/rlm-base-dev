---
page_id: connect_responses_expression_set_output.htm
title: Expression Set Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Expression Set Output

Output representation of the expression set
      create,
      update and delete request.

    
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

- 
- 

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `api​Name` | String | Unique name of the expression set. | Small, 58.0 | 58.0 |
| `context​Definitions` | [Context ​Definition Output](./connect_responses_context_definition_output.htm.md) | List of context definitions in an expression set. | Small, 58.0 | 58.0 |
| `description` | String | Description of the expression set. | Small, 58.0 | 58.0 |
| `error` | [Expression Set​ Error](./connect_responses_expression_set_error.htm.md) | Details of the error message in the case of failure of the expression set create request. | Small, 58.0 | 58.0 |
| `id` | String | ID of the expression set. | Small, 58.0 | 58.0 |
| `name` | String | Name of the expression set. | Small, 58.0 | 58.0 |
| `status` | String | Response status of the expression set.Valid values are: `Failed` `Success` | Small, 58.0 | 58.0 |
| `usage​Type` | String | Usage type of the expression set. Valid value is `Bre`. The default value is `Bre`. When Business Rules Engine is enabled for a Salesforce org, the default value is `Bre`. Other usage types may be available to you depending on your industry solution and permission sets. | Small, 58.0 | 58.0 |
| `versions` | [Expression Set​ Version Output](./connect_responses_expression_set_version_output.htm.md) | List of the expression set versions. | Small, 58.0 | 58.0 |
