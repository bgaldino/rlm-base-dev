---
page_id: sforce_api_objects_documenttemplatesection.htm
title: DocumentTemplateSection
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documenttemplatesection.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentTemplateSection

Represents a section in a document template. A document template section can be a clause, image, context, embedded template, or signature. This object is available in API version 52.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

    

## Special Access Rules

      
      

DocumentTemplateSection is available if your org has the DocGen platform license and related addon and user licenses.

    

  

    

## Fields

    
      

### AccessType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** The type of access for the section in a generated document.

        

Possible values are `Editable` or `ReadOnly`—Read Only

        

The default value is `Editable`.

      

      

### DisplayConditionExpression

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The condition that controls the display of a section in the document template.

      

      

### DocumentTemplateClauseId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of the document template clause association with the section.

        

This field is a relationship field.

        

**Relationship Name:** DocumentTemplateClause

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentClause

      

      

### DocumentTemplateId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** The ID of the document template associated with the section.

        

This field is a relationship field.

        

**Relationship Name:** DocumentTemplate

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentTemplate

      

      

### EmbeddedDocumentTemplateId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The ID of the embedded document template associated with the section.

        

This field is a relationship field.

        

**Relationship Name:** EmbeddedDocumentTemplate

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentTemplate

      

      

### EmbeddedKey

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        
      

      

### HasSectionNumberReset

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section number must be reset in the generated web document.

        

The default value is `false`.

      

      

### IsBatchable

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section must be generated using a batch job.

        

The default value is `false`.

      

      

### IsDisplayOnNewPage

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates if the section must be displayed on a new page in the generated web document.

        

The default value is `false`.

      

      

### IsNewLineAfterSectionEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether a line should get added after the section in a generated web document.

        

The default value is `false`.

      

      

### IsSectionNumberDisplayEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section number must be displayed on the generated web document.

        

The default value is `false`.

      

      

### IsTableHeaderRepeatable

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the table header must be displayed on every page in the generated web document.

        

The default value is `false`.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the section in a document template.

      

      

### ReferenceClassName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the custom class associated with the section.

      

      

### SectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The content of the section in either HTML or JSON format.

      

      

### SectionSequenceNumber

        
        

**Type:** double

        

**Properties:** Create, Filter, Nillable, Sort, Update

        

**Description:** The sequence of the section in the generated web document.

      

      

### SectionType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The type of section in a document template.

        

Possible values are:

        
          
- `Clause`

          
- `Context`

          
- `Custom`

          
- 
`EmbeddedTemplate`—Embedded Template

          
- `Image`

          
- `Item`

          
- 
`RepeatingContent`—Repeating Content

          
- `Signature`

        

      

      

### SectionTypeItemFontStyle

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The field to select font style for the display of item section type in the generated web document.

      

      

### SectionTypeItemFontValue

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The value of the font style selected for the display of the item section type in the generated web document.

      

      

### SectionTypeSignatureContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The tokens used for integration with eSignature applications.

      

      

### ShouldDisplayHeaderContentInline

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section content must be displayed inline with the section header in the generated web document.

        

The default value is `false`.

      

      

### ShouldDisplayHeaderName

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the section name must be displayed in the generated web document.

        

The default value is `false`.

      

      

### ShouldGenerateEmbeddedKey

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the embedded key should be generated in the generated web document.

        

The default value is `false`.

      

      

### TokenList

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The list of tokens used in a section of the generated web document.

      

      

### TotalSectionConditionCount

        
        

**Type:** int

        

**Properties:** Filter, Group, Nillable, Sort

        

**Description:** The number of display conditions for the section in a document template.

        

This field is a calculated field.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentTemplateSectionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentTemplateSectionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentTemplateSectionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentTemplateSectionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentTemplateSectionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
