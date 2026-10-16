---
page_id: tooling_api_objects_contextnodeattrdictionary.htm
title: ContextNodeAttrDictionary
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextnodeattrdictionary.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextNodeAttrDictionary

Represents
         the
         relationship between
         the
         ContextNodeMapping and ContextDictionary
         objects
         as a junction table. This object is available in API version 62.0
      and later.

      
      

## Supported SOAP API Calls

         
         

            `create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`
         

      

      

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
| ContextAttrrDictIdentifier | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The developer name of the context attribute dictionary. |
| ContextNodeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the context node. This field is a relationship field. **Relationship Name** ContextNode **Relationship Type** Lookup **Refers To** ContextNode |
| ContextNodeMapingId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The ID of the context node mapping. This field is a relationship field. **Relationship Name** ContextNodeMapping **Relationship Type** Lookup **Refers To** ContextNodeMapping |
| ContextNodeTagPrefix | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The tag prefix of the context node that's used to create the unique identifier of the parent context node. |
