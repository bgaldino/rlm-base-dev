---
page_id: connect_resources_doc_template.htm
title: Document Template
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_doc_template.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-10-13
---

# Document Template

Get the list of configured templates for a usage
    type.

    

## Resource

      
      

```
/connect/clm/document-template
```

    

    

## Available Version

      
      

56.0

    

    

## HTTP Methods

      
      

GET

    

    

## Example for GET

      
      

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/document-template?usageType=<usageType>&isActive=<true/false>&type=<>
```

    

    

## Request Parameters for GET

      
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contractId` | String | ID of the contract document. | Optional | 55.0 |
| `isActive` | Boolean | Status of the template. | Required | 55.0 |
| `type` | String | Format of the contract document. For example, `MicrosoftWord`. | Required | 55.0 |
| `usageType` | String | Usage type. For example, `Contract_Life_Cycle_Management`. | Required | 55.0 |

    

    

## Response Body for GET

      
      

[Template List Representation](./connect_responses_template_list.htm.md)
