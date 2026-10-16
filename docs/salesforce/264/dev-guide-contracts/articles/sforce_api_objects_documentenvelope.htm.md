---
page_id: sforce_api_objects_documentenvelope.htm
title: DocumentEnvelope
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentenvelope.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentEnvelope

The container for a document that is routed for signatures. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContractDocumentVersionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of the Contract for the Contract Document Version to which this Document Envelope belongs.

        

This is a relationship field.

        

**Relationship Name:** ContractDocumentVersion

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion

      

      

### DeliveredDateTime

        
        

**Type:** dateTime

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The timestamp at which the document was most recently viewed by all recipients.

      

      

### EnvelopeIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The identifier of this Document Envelope.

      

      

### EnvelopeMessageContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The body of the email sent to the recipient.

      

      

### EnvelopeSubject

        
        

**Type:** string

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The subject of the email sent to the recipient.

      

      

### EnvelopeUri

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The URI of this Document Envelope.

      

      

### FinalStatusDateTime

        
        

**Type:** dateTime

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The time-stamp at which this Document Envelope was completed.

      

      

### FinalStatusReason

        
        

**Type:** string

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The final status reason of this Document Envelope.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of this Document Envelope.

      

      

### ReferenceObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The ID of the object associated with this Document Envelope.

        

This is a polymorphic relationship field.

        

**Relationship Name:** ReferenceObject

        

**Relationship Type:** Lookup

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The status of this Document Envelope.

        

Possible values are `Sent`, `Delivered`, `Declined`, `Voided`, or `Completed`

      

      

### StatusChangeDateTime

        
        

**Type:** dateTime

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The most recent timestamp at which the Status of this Document Envelope was updated.

      

      

### Vendor

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The name of the online signature vendor.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentEnvelopeChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentEnvelopeFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentEnvelopeHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentEnvelopeOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentEnvelopeShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
