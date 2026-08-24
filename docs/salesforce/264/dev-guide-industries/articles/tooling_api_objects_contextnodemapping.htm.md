---
page_id: tooling_api_objects_contextnodemapping.htm
title: ContextNodeMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextnodemapping.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextNodeMapping

      Represents the relationship between the node in the context and values in the
         input schema. This object is available in API version 59.0 and later. 

      
      

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
- 
- 
- 
- 
- 
- 
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

                  

            

            
| Field | Details |
| --- | --- |
| ContextMappingId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The context mapping record that's associated with the context node mapping. This field is a relationship field. **Relationship Name** ContextMapping **Relationship Type** Lookup **Refers To** ContextMapping |
| ContextNodeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The context node record associated with this context node mapping. This field is a relationship field. **Relationship Name** ContextNode **Relationship Type** Lookup **Refers To** ContextNode |
| ManageableState | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Indicates the manageable state of the specified component that is contained in a package. Possible values are: `beta`—Managed-Beta `deleted`—Managed-Proposed-Deleted `deprecated`—Managed-Proposed-Deprecated `deprecatedEditable`—SecondGen-Installed-Deprecated `installed`—Managed-Installed `installedEditable`—SecondGen-Installed-Editable `released`—Managed-Released `unmanaged`—Unmanaged |
| Object | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The name of the object used for the mapping. |
| InheritedFrom | **Type** string **Properties** Create, Filter, Nillable, Sort, Update **Description** The name of the parent context node mapping that's used to derive the current context node mapping.This field is available in API version 60.0 and later. |
| MappedContextDefinition | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The API name of the context definition when context-to-context mappings exist.This field is available in API version 61.0 and later. |
