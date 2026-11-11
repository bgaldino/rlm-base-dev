---
page_id: sforce_api_objects_documentauthoredcontent.htm
title: DocumentAuthoredContent
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documentauthoredcontent.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentAuthoredContent

Represents the metadata of the content within the content boundary of a document such as a template or contract document. You can store metadata details of the marked clauses and sections in Salesforce with the document authored content.  This object is available in API version 58.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

DocumentAuthoredContent is available if your org has the DocGen platform license and related addon and user licenses.

    

  

    

## Fields

    
      

### Checksum

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The number of bits for the document authored content. Use the checksum to detect content changes.

      

      

### Content

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The text marked as a document authored content, such as clause content, or section content.

      

      

### ContentGenerationSource

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The source of content creation.

        

Possible values are:

        
          
- 
`GenAIDrafted`—Gen AI Drafted

          
- 
`GenAIExtracted`—Gen AI Extracted

          
- 
`MarkedContent`—Marked Content

          
- 
`StandardContent`—Standard Content

        

      

      

### ContentType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The document authored content type associated with the Reference Object. For example, Document Clause, Document Section.

        

Possible values are `DocumentAuthoredClause`—Document Authored Clause, `DocumentAuthoredSection`—Document Authored Section, or `StandardDocumentClause`—Standard Document Clause

      

      

### DocAuthoredContentIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The unique reference ID (128-bit text string) that's created at the document level and used to identify the document authored content.

      

      

### IsLibraryAdditionRequested

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Specifies if the promotion request is raised for the Document Authored Content

        

The default value is `false`.

      

      

### IsReviewed

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Specifies if the Document Authored Content is reviewed

        

The default value is `false`.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The name of the document authored content.

      

      

### ParentContentId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of parent content associated with the document authored content. For example, the ID of the section that contains clauses.

        

This field is a relationship field.

        

**Relationship Name:** ParentContent

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentAuthoredContent

      

      

### ReferenceObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** The object associated with the document authored content.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** ReferenceObject

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion, DocumentTemplate

      

      

### ReferenceObjectRecordType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The record type of the Reference Object. For example Contract Document Version, Document Template.

        

Possible values are `ContractDocumentVersion`—Contract Document Version, `DocumentTemplate`—Document Template, or `ContractExtractionResult`—Contract Extraction Result

      

      

### StandardContentObjectId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of the standard Salesforce content associated with the document authored content.

        

This field is a relationship field.

        

**Relationship Name:** StandardContentObject

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentClause

      

      

### StandardContentObjectType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the standard Salesforce content associated with the document authored content, such as Document Clause.

        

Possible values are `DocumentClause`—Document Clause

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentAuthoredContentChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentAuthoredContentFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentAuthoredContentHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentAuthoredContentOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentAuthoredContentShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
