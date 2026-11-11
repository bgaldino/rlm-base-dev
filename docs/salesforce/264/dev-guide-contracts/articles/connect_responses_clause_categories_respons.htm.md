---
page_id: connect_responses_clause_categories_respons.htm
title: Clause Library Category Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_clause_categories_respons.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-10-13
---

# Clause Library Category Response

Output representation of the request to retrieve the clause library
      category configuration.

    

## Properties

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `clauseCategories` | [Clause Category Response[]](./connect_responses_clause_category_respons.htm.md) | The list of clause category configurations. | Small, 57.0 | 57.0 |

    

    

## JSON Example

      
      

```

{
  "clauseCategories": [
    {
      "id": "0zMRO000000001s", //not a required response field
      "name": "Confidential",
      "usageType": "Contract Clause Category"
    },
    {
      "name": "Environment",
      "usageType": "Disclosure Category"
    }
  ]
}
```
