---
page_id: sforce_api_objects_productconfigurationflow.htm
title: ProductConfigurationFlow
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productconfigurationflow.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductConfigurationFlow

      Specifies the many-to-many relationship between Product Classification,
         Product, and Flow Definition objects. The flow definition is used to configure standalone
         and bundled products of a specific product classification along with the product
         attributes, quantities, and product selling models. This object is available in API
      version 60.0 and later. 

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `search()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Fields

         
         

               
               
            
               
                  

                  

               

            

            
                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

                  

                  
                     

                     

: 

: 

: 
: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 

: 

                  

            

            
| Field | Details |
| --- | --- |
| FlowIdentifier | **Type** String **Properties** Create, Filter, Group, Sort, Update **Description** Stores the flow API name. |
| IsDefault | **Type** Boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates the default configurator flow. The default value is `false`. |
| IsRequestDetailEditable | **Type** Boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether request attributes and products can be edited (`true`) or not (`false`). When enabled, users can modify the attributes and products in associated cases, incidents, or service requests after the request is created. The default value is `false`. |
| Status | **Type** Picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Indicates the status of the product configuration flow. Possible values include Draft, Active, and Inactive Possible values are: `Active` `Draft` `Inactive` The default value is `Draft`. |
