---
page_id: sforce_api_objects_generateddocumentsection.htm
title: GeneratedDocumentSection
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_generateddocumentsection.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# GeneratedDocumentSection

Represents a section of a generated document.  This object is available in API version 60.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
    

  

    

## Fields

    
      

### DisplayHeaderFontStyle

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Default font style of a section header in the generated web document.

      

      

### DocumentTemplateClauseId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the document template clause association with the section.

        

This field is a relationship field.

        

**Relationship Name:** DocumentTemplateClause

        

**Refers To:** DocumentClause

      

      

### DocumentTemplateSectionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the associated document template section.

        

This field is a relationship field.

        

**Relationship Name:** DocumentTemplateSection

        

**Refers To:** DocumentTemplateSection

      

      

### GeneratedDocumentId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** ID of the generated document associated with the section.

        

This field is a relationship field.

        

**Relationship Name:** GeneratedDocument

        

**Relationship Type:** Master-detail

        

**Refers To:** GeneratedDocument (the master object)

      

      

### IsBeginSplitSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section must be split in the generated web document.

        

The default value is `false`.

      

      

### IsEndSplitSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section split must end in the generated web document.

        

The default value is `false`.

      

      

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

        

**Description:** The name of the section in the generated web document.

      

      

### SectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The section content that's stored as HTML.

      

      

### SectionOrder

        
        

**Type:** double

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The order of the section in the section’s hierarchy.

      

      

### SectionTypeSignatureContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The tokens used for integration with eSignature applications.

      

      

### SplitSectionSequenceNumber

        
        

**Type:** double

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The sequence of the section that's split in the generated web document.

      

      

### TemplateSectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The content of the section in the original format.

      

      

### TokenList

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The list of tokens used to define a section condition in the generated web document.

      

      

### XmlContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The content of the section in the generated web document in the XML format.
