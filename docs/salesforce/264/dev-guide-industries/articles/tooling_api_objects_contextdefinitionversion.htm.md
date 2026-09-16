---
page_id: tooling_api_objects_contextdefinitionversion.htm
title: ContextDefinitionVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_contextdefinitionversion.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ContextDefinitionVersion

      Represents information about the context definition version. Only one version
         can be active at a time. This object is available in API version 59.0 and later. 

      
      

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

                  

            

            
| Field | Details |
| --- | --- |
| ContextDefinitionId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The context definition record associated with the context definition version. This field is a relationship field. **Relationship Name** ContextDefinition **Relationship Type** Lookup **Refers To** ContextDefinition |
| EndDate | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** The date and time when the context definition version becomes inactive. |
| InheritedApexVersion | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The version of the Apex class generated from the context definition version. It is null when no Apex class is generated, 0.0 when an Apex class is generated for a custom definition, and equal to the value in InheritedVersionNumber when an Apex class is generated from an extended definition. This field is available in API version 68.0 and later. |
| IsActive | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the context definition version is active (true) or not (false). The default value is `false`. |
| ManageableState | **Type** picklist **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Indicates the manageable state of the specified component that is contained in a package. Possible values are: `beta`—Managed-Beta `deleted`—Managed-Proposed-Deleted `deprecated`—Managed-Proposed-Deprecated `deprecatedEditable`—SecondGen-Installed-Deprecated `installed`—Managed-Installed `installedEditable`—SecondGen-Installed-Editable `released`—Managed-Released `unmanaged`—Unmanaged |
| StartDate | **Type** dateTime **Properties** Create, Filter, Sort, Update **Description** The date and time when the context definition version becomes active. |
| VersionNumber | **Type** int **Properties** Create, Filter, Group, Sort, Update **Description** The context definition version number. |
