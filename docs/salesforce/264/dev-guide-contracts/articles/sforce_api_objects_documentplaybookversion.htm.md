---
page_id: sforce_api_objects_documentplaybookversion.htm
title: DocumentPlaybookVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentplaybookversion.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentPlaybookVersion

Tracks the playbook versions through content updates and
         revisions. This object is available in API version 68.0 and
      later.

      

## Supported Calls

      
      

         `create()`,
         `delete()`,
         `describeLayout()`,
         `describeSObjects()`,
         `getDeleted()`,
         `getUpdated()`,
         `query()`,
         `retrieve()`,
         `search()`,
         `undelete()`,
         `update()`,
         `upsert()`
      

      

      

      

## Fields

      
         

### CreatedById

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Filter, Group, Sort

                 
- 
**Description**: The user who created this record.

             

         

         

### CreatedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Sort

                 
- 
**Description**: The date and time when this record was created.

             

         

         

### Description

             
             
                 
- 
**Type**: textarea

                 
- 
**Properties**: Create, Nillable, Update

                 
- 
**Description**: Additional details about the document playbook version.

             

         

         

### DocumentPlaybookId

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Create, Filter, Group, Sort

                 
- 
**Description**: The ID of the document playbook associated with the document
                                 playbook version.

This field is a relationship field.

                 
- 
**Relationship Name**: DocumentPlaybook

                 
- 
**Relationship Type**: Master-detail

                 
- 
**Refers To**: DocumentPlaybook (the master object)

             

         

         

### LastModifiedById

             
             
                 
- 
**Type**: reference

                 
- 
**Properties**: Filter, Group, Sort

                 
- 
**Description**: The user who most recently modified this record.

             

         

         

### LastModifiedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Sort

                 
- 
**Description**: The date and time when this record was most recently
                                 modified.

             

         

         

### LastReferencedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Nillable, Sort

                 
- 
**Description**: The timestamp for when the current user last viewed a record
                                 related to this record.

             

         

         

### LastViewedDate

             
             
                 
- 
**Type**: dateTime

                 
- 
**Properties**: Filter, Nillable, Sort

                 
- 
**Description**: The timestamp for when the current user last viewed this record.
                                 If this value is null, this record might only have been
                                 referenced (LastReferencedDate) and not viewed.

             

         

         

### Name

             
             
                 
- 
**Type**: string

                 
- 
**Properties**: Create, Filter, Group, idLookup, Sort, Update

                 
- 
**Description**: The name of the document playbook version.

             

         

         

### Status

             
             
                 
- 
**Type**: picklist

                 
- 
**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

                 
- 
**Description**: The status of the document playbook version.

                 
- 
**Default value**: `Draft`

                 
- 
**Possible values**:
                                    
  - `Active`

                                    
  - `Archived`

                                    
  - `Draft`

                                 

             

         

         

### VersionNumber

             
             
                 
- 
**Type**: int

                 
- 
**Properties**: Create, Filter, Group, idLookup, Sort, Update

                 
- 
**Description**: The version of the document playbook.

             

         

      

   

      

## Associated Objects

      
            
                

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[DocumentPlaybookVersionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)**

               
: Change events are available for the object.

            
            
               

**[DocumentPlaybookVersionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)**

               
: Feed tracking is available for the object.

            
            
               

**[DocumentPlaybookVersionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)**

               
: History is available for tracked fields of the object.

            
            
               

**[DocumentPlaybookVersionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)**

               
: Sharing is available for the object.
