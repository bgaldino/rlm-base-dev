---
page_id: tooling_api_objects_contexttag.htm
title: ContextTag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contexttag.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextTag

      Represents a shortened name of an attribute or node instead of its fully
         qualified tag structure name. This object is available in API version 59.0 and later. 

      
      

## Supported SOAP API Calls

      
      

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
| ContextAttributeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The context attribute record that's associated with the context tag. This field is a relationship field. **Relationship Name** ContextAttribute **Relationship Type** Lookup **Refers To** ContextAttribute |
| ContextNodeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The context node record that's associated with the context tag. This field is a relationship field. **Relationship Name** ContextNode **Relationship Type** Lookup **Refers To** ContextNode |
| Title | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The name of the context tag. |
| InheritedFrom | **Type** string **Properties** Create, Filter, Nillable, Sort, Update **Description** The name of the parent context tag that's used to derive the current context tag.This field is available in API version 60.0 and later. |
