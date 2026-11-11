---
page_id: sforce_api_objects_documenttemplate.htm
title: DocumentTemplate
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_documenttemplate.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# DocumentTemplate

Represents information about dynamic document generation. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ContextDefinitionName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the context definition that contains the mapping details used for extraction in the Context Service token mapping type.

      

      

### ContextMappingName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the context mapping used for extraction in the Context Service token mapping type.

      

      

### ContextTransformationName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the transform that’s used to convert the hydrated data into the desired output structure. This transformation uses formulas, grouping operations, and hierarchical representations, including nested groups and product bundles. Available in API version 67.0 and later.

      

      

### CustomClassName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the custom class that provides token values required by the template for document generation.

      

      

### DefaultFontStyle

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The default font style for a web document template.

      

      

### DocumentConversionResourceName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the resource containing the Microsoft Word document file used to generate the output web document.

      

      

### DocumentGenerationMechanism

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the method for generating the document.

        

Possible values are `ClientSide` or `ServerSide`

        

The default value is `ClientSide`.

      

      

### ExtractOmniDataTransformName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the OmniDataTransform bundle of the extract type.

      

      

### GlobalKey

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The unique ID used when migrating the document template between Salesforce orgs. This field is specifically used for import and export operations in managed packages.

      

      

### HasBatchableSection

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the template has one or more batchable sections.

        

The default value is `false`.

      

      

### IsActive

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the document template is active.

        

The default value is `false`.

      

      

### IsSectionProcessed

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the contract boundary sections of the document template are processed.

        

The default value is `false`.

      

      

### LastEmbeddedTmplSectionKey

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The last auto generated key of the embedded template section.

      

      

### MapperOmniDataTransformName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The name of the OmniDataTransform bundle of the mapper type.

      

      

### Name

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, idLookup, Sort, Update

        

**Description:** The name of the document template.

      

      

### Namespace

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** Indicates whether the document template was exported using the industry-specific templates datapack (namespace prefix), or a user manually created or cloned an exported document template (blank). The namespace prefix is associated with the industry license. For example, `insurance_fsc_ise`.

      

      

### OwnerId

        
        

**Type:** reference

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** The ID of the document template.

        

This field is a polymorphic relationship field.

        

**Relationship Name:** Owner

        

**Relationship Type:** Lookup

        

**Refers To:** Group, User

      

      

### RecordTypeId

        
        

**Type:** reference

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** ID of the record type associated with this object.

        

This field is a relationship field.

        

**Relationship Name:** RecordType

        

**Relationship Type:** Lookup

        

**Refers To:** RecordType

      

      

### SectionHeaderFontStyle

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The field to select font style for the section header of the web document template.

      

      

### SectionHeaderFontStyleValue

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The value of the font style selected for the section header of the web document template.

      

      

### ShouldDisplayUnmappedToken

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the tokens without runtime values must be displayed.

        

The default value is `false`.

      

      

### ShouldExtractEmbeddedTmplToken

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether tokens from all the templates embedded within the document template must be extracted. If this field’s value is yes, the embedded template tokens are extracted into the mapping omnidatatransform associated with the template.

        

The default value is `false`.

      

      

### Status

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the status of the document template.

        

Possible values are `Active`, `Archived`, or `Draft`

      

      

### TargetTokenItemObject

        
        

**Type:** multipicklist

        

**Properties:** Create, Filter, Nillable, Update

        

**Description:** The line item object of the target token object associated with the document template, that's used for mapping tokens.

        

Possible values are `OpportunityLineItem`, `OrderLineItem`, or `QuoteLineItem`

      

      

### TargetTokenObject

        
        

**Type:** multipicklist

        

**Properties:** Create, Filter, Nillable, Update

        

**Description:**

        

The object associated with the document template that's used for mapping tokens.

        

Possible values are `Contract`, `Opportunity`, `Order`, or `Quote`

      

      

### TokenList

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The list of tokens used to define a section condition.

      

      

### TokenMappingMethodType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the processing method for the data which can come from same source object.

        

Possible values are `CustomClass` or `OmniDataTransform`

      

      

### TokenMappingType

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the mapping type for tokens of the document template.

        

Possible values are `JSON` or `SalesforceObject`

      

      

### Type

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Specifies the type of document template.

        

Possible values are `Web`, `MicrosoftWord`, `Microsoft365Word`, or `MicrosoftPowerpoint`

      

      

### UniqueName

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The unique name for the document template.

      

      

### UsageType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

        

**Description:** Specifies the document template usage. For example, the Contract Lifecycle Management option allows you to use the document template only for contract document generation.

        

The default value is `Contract_Lifecycle_Management`.

      

      

### VersionNumber

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

        

**Description:** The version number of the document template.

      

      

### XmlRelationshipMetadata

        
        

**Type:** textarea

        

**Properties:** Create, Nillable, Update

        

**Description:** The WML relationship metadata used to process Microsoft Word documents.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[DocumentTemplateChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[DocumentTemplateFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[DocumentTemplateHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[DocumentTemplateOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[DocumentTemplateShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
