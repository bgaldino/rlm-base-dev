---
page_id: connect_resources_clause_category_configurations.htm
title: Clause Category List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_clause_category_configurations.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clause_library_resources.htm
fetched_at: 2026-10-13
---

# Clause Category List

Access list of clause categories from the configuration.

    

## Resource

      
      

```
/connect/clause-library/clause-category-configurations
```

    

    

## Example URI

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/68.0/connect/clause-library/clause-category-configurations
```

    

    

## Available Version

      
      

57.0

    

    

## HTTP Methods

      
      

GET

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `name` | String | The name of the clause category. | Required | 57.0 |
| `usageType` | String | The usage type for the clause category. Valid values are `Contract Clause Category ` or `Disclosure Category`. | Required | 57.0 |

    

    

## Response Body for GET

      
      

[Clause Library Category Response](./connect_responses_clause_categories_respons.htm.md)
