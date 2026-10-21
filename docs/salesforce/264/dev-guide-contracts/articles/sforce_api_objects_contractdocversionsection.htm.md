---
page_id: sforce_api_objects_contractdocversionsection.htm
title: ContractDocVersionSection
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_contractdocversionsection.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ContractDocVersionSection

Tracks contract document sections through contract lifecycle stages. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContractDocumentVersionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort

        

**Description:** Contract Document Version to which this section belongs.

        

This is a relationship field.

        

**Relationship Name:** ContractDocumentVersion

        

**Relationship Type:** Lookup

        

**Refers To:** ContractDocumentVersion

      

      

### CreationProcessType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Indicates how this section was created.

        

Possible values are:

        
          
- `BatchMode`

          
- `Customize`

          
- `Generate`

          
- `Import`

          
- `ReconcileWord`

          
- `UpdateContract`

        

        

The default value is 'Generate'.

      

      

### DisplayHeaderFontStyle

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The default font style of a section header in the generated web document.

      

      

### DocumentTemplateClauseId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Clause from which this contract section is created.

        

This is a relationship field.

        

**Relationship Name:** DocumentTemplateClause

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentTemplateClause

      

      

### DocumentTemplateSectionId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** The template section from which this contract section is created.

        

This is a relationship field.

        

**Relationship Name:** DocumentTemplateSection

        

**Relationship Type:** Lookup

        

**Refers To:** DocumentTemplateSection

      

      

### HasReconciledRedlines

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the contract section contains reconciled red lines.

        

The default value is 'false'.

      

      

### IsBeginSplitSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates that a section split in the generated web document begins here.

        

The default value is 'false'.

      

      

### IsEndSplitSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates that a section split in the generated web document ends here.

        

The default value is 'false'.

      

      

### IsRedlinedSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the contract section contains red lines.

        

The default value is 'false'.

      

      

### IsSectionStandard

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether a section conforms to its template.

        

The default value is 'false'.

      

      

### Level

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Level of this section in the section hierarchy.

      

      

### ReconciledSectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Section content resulting from reconciliation in the Word document.

      

      

### SectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Update

        

**Description:** Section content in HTML format.

      

      

### Sequence

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** Section's sequence number in the contract document.

      

      

### SignatureContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** DocuSign signature tokens.

      

      

### SubSequence

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The sub sequence of the section in the generated web document.

      

      

### TemplateSectionContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Original section content from the corresponding template section.

      

      

### TokenList

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Tokens in the section that map to Salesforce object fields.

      

      

### Type

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Indicates section type.

        

Possible values are:

        
          
- `Clause`

          
- `Context`

          
- `Custom`

          
- `EmbeddedTemplate`

          
- `Image`

          
- `Item`

          
- `RepeatingContent`

          
- `Signature`

        

        

The default value is 'Context'.

      

      

### XmlContent

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** Section content in XML format.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ContractDocVersionSectionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ContractDocVersionSectionFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ContractDocVersionSectionHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ContractDocVersionSectionOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ContractDocVersionSectionShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
