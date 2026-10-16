---
page_id: tooling_api_objects_contextnode.htm
title: ContextNode
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextnode.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextNode

      Represents information about the structure of the nodes within the context.
         Within a structure, each node can have other nodes related to them and attributes to
         describe the object. A hierarchy for the nodes can also be defined here. This object
      is available in API version 59.0 and later. 

      
      

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

                  

            

            
| Field | Details |
| --- | --- |
| CanonicalNodeId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The canonical node associated with the context node. This field is a relationship field. This field is available in API version 61.0 and later. **Relationship Name** CanonicalNode **Refers To** ContextNode |
| ContextDefinitionVersionId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The context definition version record associated with the context node. This field is a relationship field. **Relationship Name** ContextDefinitionVersion **Relationship Type** Lookup **Refers To** ContextDefinitionVersion |
| Description | **Type** textarea **Properties** Create, Filter, Nillable, Sort, Update **Description** The description of the context node. |
| DisplayName | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The display name of the context node.This field is available in API version 61.0 and later. |
| InheritedFrom | **Type** string **Properties** Create, Filter, Nillable, Sort, Update **Description** The name of the parent context node that's used to derive the current context node.This field is available in API version 60.0 and later. |
| IsCustomMappingAllowed | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the attribute can be mapped to a source attribute in an extended context definition (`true`) or not (`false`). The default value is `false`. |
| IsTransposable | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the data in the Context Node record can be converted to field names (true) or not (false). The default value is `false`. |
| ManageableState | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Indicates the manageable state of the specified component that is contained in a package. Possible values are: `beta`—Managed-Beta `deleted`—Managed-Proposed-Deleted `deprecated`—Managed-Proposed-Deprecated `deprecatedEditable`—SecondGen-Installed-Deprecated `installed`—Managed-Installed `installedEditable`—SecondGen-Installed-Editable `released`—Managed-Released `unmanaged`—Unmanaged |
| Title | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The name of the context node. |
