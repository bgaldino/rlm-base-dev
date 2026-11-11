---
page_id: sforce_api_objects_contractdocumentversion.htm
title: ContractDocumentVersion
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contractdocumentversion.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContractDocumentVersion

Tracks contract document versions through contract lifecycle stages. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContractId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** The ID of the contract associated with the contract document version.

        

This is a relationship field.

        

**Relationship Name:** Contract

        

**Relationship Type:** Lookup

        

**Refers To:** Contract

      

      

### CreatedByFullName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** User who created this contract document version.

      

      

### CreationProcessType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Indicates how the document version was created

        

Possible values are:

        
          
- 
`BatchMode`—Batch Mode

          
- `Checkout`

          
- 
`CheckoutModify`—Checkout Modify

          
- 
`ContractReconciliation`—Contract Reconciliation

          
- 
`CreateContract`—Create Contract

          
- `Customize`

          
- 
`External_Online_Editor`—Microsoft 365

          
- `Generate`

          
- `Import`

          
- 
`Microsoft365ExternalReview`—Non-Private External Review

          
- 
`Microsoft365PrivateExternalReview`—Private External Review

          
- `ReconcileWord`

          
- `UpdateContract`

        

      

      

### DocConversionResourceName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the resource containing the Microsoft Word document file used to generate the output web document.

      

      

### DocumentTemplateId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Document Template Identifier.

        

This is a relationship field.

        

**Relationship Name:** DocumentTemplate

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentTemplate

      

      

### HasNewTemplateVersionAvl

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the latest version of the template is newer than the version used to generate the document.

        

The default value is 'false'.

      

      

### HasReconRedlinedSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether this contract document version contains red lines.

        

The default value is 'false'.

      

      

### HasRedlinedSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether this contract document version contains red lines.

        

The default value is 'false'.

      

      

### IsDocumentVersionLocked

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the document is locked.

        

The default value is 'false'.

      

      

### IsLockedByCurrentUser

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the user currently accessing the document has locked the document.

        

The default value is 'false'.

      

      

### IsSectionInfoStoredInDoc

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether section IDs are stored in the document (used for internal processing).

        

The default value is 'false'.

      

      

### ShouldBypassStateMdlTrnst

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the Contract State Model Transition is bypassed (true) or ignored (false).

        

The default value is 'false'.

      

      

### LastReferencedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed a record related to this record.

      

      

### LastViewedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed.

      

      

### LockType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the reason why the document version is locked.

        

Possible values are `Generate`, `SuperUser`, or `User`

      

      

### LockedById

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the user who locked this version.

        

This is a relationship field.

        

**Relationship Name:** LockedBy

        

**Relationship Type:** Lookup

        

**Refers To:** User

      

      

### LockedByUserName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Name of the user who locked this version.

      

      

### NonStandardSectionCount

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Count of non-standard sections.

      

      

### ReconRedlinedSectionCount

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Total count of sections that contain red lines in the document version.

      

      

### RedlinedSectionCount

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Total count of sections that contain red lines in the document version.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Contract document version status.

        

Possible values are `Active`, `Inactive`, or `Draft`

      

      

### VersionNumber

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Contract document version number.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContractDocumentVersionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContractDocumentVersionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContractDocumentVersionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContractDocumentVersionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContractDocumentVersionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
