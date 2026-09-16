---
page_id: sforce_api_objects_productconfigflowassignment.htm
title: ProductConfigFlowAssignment
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productconfigflowassignment.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductConfigFlowAssignment

      A junction object that represents the many-to-many relationship between
         Product Configuration Flow, Product, and Product Classification. This object is
      available in API version 60.0 and later. 

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Fields

         
         

               
               
            
               
                  

                  

               

            

            
                  
                     

                     

: 

: 

: 
: 
- 
- 

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

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| AssignmentType | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies whether the Product Configuration Flow is assigned to the primary product or classification, or to dynamic components added within a bundle. Valid values are: `DynamicAdditionFlow` `PrimaryConfiguratorFlow` The default value is `PrimaryConfiguratorFlow`. Available in API version 65.0 and later. |
| ProductClassificationId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The product classification associated with the Product Configuration Flow. This field is a relationship field. **Relationship Name** ProductClassification **Relationship Type** Lookup **Refers To** ProductClassification |
| ProductConfigurationFlowId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The Product Configuration Flow associated with the Product Classification or Product. This field is a relationship field. **Relationship Name** ProductConfigurationFlow **Relationship Type** Lookup **Refers To** ProductConfigurationFlow |
| ProductId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The product associated with the Product Configuration Flow. This field is a relationship field. **Relationship Name** Product **Relationship Type** Lookup **Refers To** Product2 |
