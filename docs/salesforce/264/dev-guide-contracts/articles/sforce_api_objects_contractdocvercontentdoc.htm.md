---
page_id: sforce_api_objects_contractdocvercontentdoc.htm
title: ContractDocVerContentDoc
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contractdocvercontentdoc.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContractDocVerContentDoc

Associates a contract document version with a content document. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContentDocumentId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** ID of the content document associated with the contract document version content document.

        

This is a relationship field.

        

**Relationship Name:** ContentDocument

        

**Relationship Type:** Lookup

        

**Refers To:** ContentDocument

      

      

### ContentVersion

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Identifies the content version.

      

      

### ContractDocumentVersionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** ID of the contract document version.

        

This is a relationship field.

        

**Relationship Name:** ContractDocumentVersion

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion

      

      

### DocumentSourceType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Source where the generated document originated.

        

Possible values are `Content` or `External`

        

The default value is 'Content'.

      

      

### DocumentType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the document type of the contract.

        

Possible values are:

        
          
- 
`AttachedDocument`—Attached Document

          
- 
`ComparisonDocument`—Comparison Document

          
- 
`ContractDocument`—Contract Document

          
- 
`ExternalReviewDocument`—External Review Document

          
- 
`SignedDocument`—Signed Document

        

      

      

### IsGeneratedDocCheckedIn

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the generated document is checked in.

        

The default value is 'false'.

      

      

### LastReferencedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed a record related to this record.

      

      

### LastViewedDate

        
        

**Type:** dateTime

        

**Properties:** Filter, Nillable, Sort

        

**Description:** The timestamp for when the current user last viewed this record. If this value is null, this record might only have been referenced (LastReferencedDate) and not viewed.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Lists the contract document name.

      

      

### RelatedCntrDocVerContentDocId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the contract document version content document that links PDF and Word documents.

        

This is a relationship field.

        

**Relationship Name:** RelatedCntrDocVerContentDoc

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocVerContentDoc

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContractDocVerContentDocChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContractDocVerContentDocFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContractDocVerContentDocHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContractDocVerContentDocOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContractDocVerContentDocShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
