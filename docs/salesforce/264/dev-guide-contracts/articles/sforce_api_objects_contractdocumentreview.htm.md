---
page_id: sforce_api_objects_contractdocumentreview.htm
title: ContractDocumentReview
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contractdocumentreview.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContractDocumentReview

Represents the review process-related details, such as the reference object type and review status.  This object is available in API version 58.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

ContractDocumentReview is available if your org has the DocGen platform license and related addon and user licenses.

    

  

    

## Fields

    
      

### ContractDocumentVersionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The contract document version associated with the external document.

        

This field is a relationship field.

        

**Relationship Name:** ContractDocumentVersion

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion

      

      

### ExternalReviewerEmail

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The email ID for the document reviewer.

      

      

### ExternalReviewerIdentifier

        
        

**Type:** string

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The alphanumeric external identifier for the reviewer.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Name of contract document.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The status of document review. The default value is `NotStarted`.

        

Possible values are `Completed`—Complete, `InProgress`—In Progress, or `NotStarted`—Not Started

      

      

### UnresolvedCommentCount

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The number of unresolved comments in the document.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContractDocumentReviewChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContractDocumentReviewFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContractDocumentReviewHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContractDocumentReviewOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContractDocumentReviewShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
