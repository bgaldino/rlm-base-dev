---
page_id: connect_requests_decision_matrix_column.htm
title: Decision Matrix Column Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_column.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Column
    Input

Input representation of the information required to add, update, or
      delete columns in a decision matrix.

      
      
        
          

**Properties**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    
- 
- 

                    

#### 

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    
- 
- 

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

#### 

                    

                  

                  
                    

                    

                    

                    

                    

                  

                  
                    

                    

                    

                    

                    

                  

                

              
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | The type of action you want to perform on a column.Possible values are: `delete` `update` | Required Note Leave this field blank if you’re adding a column in a decision matrix. | 53.0 |
| `apiName` | String | The API name of a column. | Optional | 53.0 |
| `columnType` | String | The type of a column.Possible values are: `Input` `Output` | Required | 53.0 |
| `dataType` | String | The data type of a column. | Optional | 53.0 |
| `displaySequence` | Integer | The display sequence of a column. | Optional | 53.0 |
| `id` | String | The ID of the column record to be updated or deleted. | Required Note Leave this field blank if you’re adding a column in a decision matrix. | 53.0 |
| `name` | String | The name of a column. | Required | 53.0 |
| `rangeValues` | String | The range values of a column. The range columns contain a sorted list of comma-separated values, which are updated whenever a row is added to the Decision Matrix Version. | Optional | 53.0 |
