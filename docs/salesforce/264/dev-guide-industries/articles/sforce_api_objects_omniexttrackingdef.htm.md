---
page_id: sforce_api_objects_omniexttrackingdef.htm
title: OmniExtTrackingDef
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_omniexttrackingdef.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_standard_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# OmniExtTrackingDef

      Represents a connection between an OmniTrackingGroup in OmniAnalytics and a
         third-party Analytics system such as Google Analytics. This object is available in API
      version 60.0 and later. 

      
         

#### Note

This object is part of OmniStudio Standard, not OmniStudio for Vlocity.

         

#### Important

 Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations. 

      

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeSObjects()`, 
         `query()`, 
         `retrieve()`, 
         `update()`, 
         `upsert()`
      

      

      

## Special Access Rules

         
         

Using OmniAnalytics requires having an OmniStudio license and enabling OmniAnalytics in
            Setup.

      

      

## Fields

         
         

               
               
            
               
                  

                  

               

            

            
                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

#### 

#### 

                  

                  
                     

                     

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

: 

                  

            

            
| Field | Details |
| --- | --- |
| Description | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** A description of the OmniExtTrackingDef. |
| DeveloperName | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The unique name of the OmniExtTrackingDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record. Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| IsActive | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Specifies whether the OmniExtTrackingDef is active. The default value is `true`. |
| Language | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The language for the OmniExtTrackingDef. |
| MasterLabel | **Type** string **Properties** Create, Filter, Group, Sort, Update **Description** The unique master label of the OmniExtTrackingDef. This internal label doesn’t get translated. |
| OmniExtTrackingDefKey | **Type** string **Properties** Filter, Group, idLookup, Nillable, Sort **Description** A UUID generated internally by Salesforce to uniquely identify an OmniExtTrackingDef record across all orgs. |
| TrackingFrameworkInformation | **Type** textarea **Properties** Create, Update **Description** JSON data containing information about an external service, such as the API call and input parameter names. |
| TrackingServiceProvider | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update **Description** The third-party Analytics system to which user interaction data is sent. Possible values are: `Google` The default value is `Google`. |
