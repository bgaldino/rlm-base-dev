---
page_id: tooling_api_objects_contextmappingintent.htm
title: ContextMappingIntent
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextmappingintent.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextMappingIntent

      Represents the purpose associated to a context mapping. This object is
      available in API version 61.0 and later. 

      
      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeSObjects()`, 
         `query()`, 
         `retrieve()`, 
         `update()`, 
         `upsert()`
      

      

      

## Supported REST API Methods

         
         

`DELETE, GET, HEAD, PATCH, POST, Query`
         

      

      

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
- 
- 
- 
- 

                  

            

            
| Field | Details |
| --- | --- |
| ContextMappingId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The context mapping that's associated with usage intent. This field is a relationship field. **Relationship Name** ContextMapping **Relationship Type** Master-detail **Refers To** ContextMapping (the master object) |
| MappingIntent | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Specifies the purpose to identify the type of context mapping required. Possible values are: `association`—Association `hydration`—Hydration `persistence`—Persistence `translation`—Translation |
