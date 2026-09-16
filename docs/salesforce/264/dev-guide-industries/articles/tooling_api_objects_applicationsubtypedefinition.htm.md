---
page_id: tooling_api_objects_applicationsubtypedefinition.htm
title: ApplicationSubtypeDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/tooling_api_objects_applicationsubtypedefinition.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_tooling_api_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ApplicationSubtypeDefinition

      Represents a subtype of an application within an application domain.
      Available in API version 54.0 and later. 

      
         

#### Important

 Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported SOAP API Calls

         
         

            `create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`
         

      

      

## Supported REST API Methods

         
         

`DELETE, GET, HEAD, PATCH, POST, Query`
         

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 
: 
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
| ApplicationUsageType | **Type** string **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the application's domain that defines the application's subtype. Possible values are: `Explainability Service` The default value is `ExplainabilityService`. |
| Description | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The description of the application subtype definition record. |
| DeveloperName | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The unique name of the application subtype definition. |
| Language | **Type** string **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The language of the application subtype definition. |
| ManageableState | **Type** string **Properties** Filter, Group, Nillable, Restricted picklist, Sort **Description** Indicates the manageable state of the specified component that is contained in a package. Possible values are: `beta`—Managed-Beta `deleted`—Managed-Proposed-Deleted `deprecated`—Managed-Proposed-Deprecated `deprecatedEditable`—SecondGen-Installed-Deprecated `installed`—Managed-Installed `installedEditable`—SecondGen-Installed-Editable `released`—Managed-Released `unmanaged`—Unmanaged |
| MasterLabel | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The UI label of the application subtype definition. |
| NamespacePrefix | **Type** string **Properties** Filter, Group, Nillable, Sort **Description** The namespace prefix that is associated with this object. Each Developer Edition org that creates a managed package has a unique namespace prefix. Limit: 15 characters. You can refer to a component in a managed package by using the `namespacePrefix__componentName` notation. |
