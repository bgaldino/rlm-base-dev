---
page_id: tooling_api_objects_ctxattrhydrationctx.htm
title: CtxAttrHydrationCtx
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_ctxattrhydrationctx.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CtxAttrHydrationCtx

      Represents the queries that fetch the data for a chosen attribute from the
         input schema for context-to-context mapping This object is available in API version
      61.0 and later. 

      
      

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

: 

: 

                  

            

            
| Field | Details |
| --- | --- |
| ContextAttributeMappingId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The context attribute mapping record that's associated with the attribute hydration detail. This field is a relationship field. **Relationship Name** ContextAttributeMapping **Relationship Type** Master-detail **Refers To** ContextAttributeMapping (the master object) |
| ContextQueryAttribute | **Type** string **Properties** Create, Filter, Sort, Update **Description** The attribute in context definition that's the source of context hydration. |
| InheritedFrom | **Type** string **Properties** Create, Filter, Nillable, Sort, Update **Description** The name of the parent CtxAttrCtxHydrationDetail that's used to derive the current CtxAttrCtxHydrationDetail. |
