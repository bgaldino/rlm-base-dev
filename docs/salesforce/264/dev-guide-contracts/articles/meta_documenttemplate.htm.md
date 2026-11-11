---
page_id: meta_documenttemplate.htm
title: DocumentTemplate
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_documenttemplate.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# DocumentTemplate

Represents the document template definitions that enable dynamic document generation from templates within Salesforce organizations.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends the [MetadataWithContent](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_metadatawithcontent.htm) metadata type and inherits its content and fullName fields.

    

    

## File Suffix and Directory Location

      
      

DocumentTemplate components have the suffix .dt and are stored in the documentTemplates folder.

    

    

## Version

      
      

DocumentTemplate components are available in API version 59.0 and later.

    

  

    

## Fields

    
      

### contextDefinitionName

        
        

**Type:** string

        

**Description:** Context service definition that describes the relationship between node structures within a context. Available in API version 65.0 and later.

      

      

### contextFilterName

        
        

**Type:** string

        

**Description:** The name of the context filter that extracts records in the Context Service token mapping type. For example, filter Line Items with Total Price greater than 1000 and sort by Quantity in descending order. This is optional and applicable only for context token mapping. Available in API version 66.0 and later.

      

      

### contextMappingName

        
        

**Type:** string

        

**Description:** Context service mapping that defines the mapping of attributes and nodes to related objects. Available in API version 65.0 and later.

      

      

### contextTransformationName

        
        

**Type:** string

        

**Description:** Name of the context transformation used in the Context Service token mapping type. Applicable only for context token mapping. Available in API version 67.0 and later.

      

      

### customClassName

        
        

**Type:** string

        

**Description:** Custom class to process document template operations and transformations.

      

      

### defaultFontStyle

        
        

**Type:** string

        

**Description:** Default font styling applied to the document template content.

      

      

### documentConversionResourceName

        
        

**Type:** string

        

**Description:** Conversion resource reference used for transforming document content between formats.

      

      

### documentGenerationMechanism

        
        

**Type:** DocumentGenerationMechanism (enumeration of type string)

        

**Description:** Specifies how documents are generated from the template, defining the generation mechanism and processing approach.

        

Valid values are `ClientSide` or `ServerSide`. The default value is `ClientSide`.

      

      

### extractOmniDataTransformName

        
        

**Type:** string

        

**Description:** Data extraction transform name for OmniStudio integration, enabling extraction of data from various sources for template processing.

      

      

### fileExtension

        
        

**Type:** string

        

**Description:** Output file format extension for documents generated from this template.

      

      

### hasBatchableSection

        
        

**Type:** boolean

        

**Description:** Indicates whether the template supports batch processing of sections ( `true`) or not ( `false`). The default value is `false`.

      

      

### isActive

        
        

**Type:** boolean

        

**Description:** Indicates whether the template is active and available for document generation ( `true`) or not ( `false`). The default value is `false`.

      

      

### isSectionProcessed

        
        

**Type:** boolean

        

**Description:** Indicates whether sections are processed in the template ( `true`) or not ( `false`). The default value is `false`.

      

      

### lastEmbeddedTmplSectionKey

        
        

**Type:** string

        

**Description:** Last processed section key for embedded template processing, used for tracking template section processing state.

      

      

### mapperOmniDataTransformName

        
        

**Type:** string

        

**Description:** Data mapping transform name for OmniStudio integration, enabling mapping of data between different formats and structures. Available in API version 56.0 and later.

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Display label for the template that appears in the user interface.

      

      

### name

        
        

**Type:** string

        

**Description:** Internal name used to identify the template within the system.

      

      

### namespace

        
        

**Type:** string

        

**Description:** Package namespace for the template used in managed package deployments.

      

      

### sectionHeaderFontStyle

        
        

**Type:** string

        

**Description:** Header font styling applied to section headers within the document template.

      

      

### sectionHeaderFontStyleValue

        
        

**Type:** string

        

**Description:** Header font values and properties for section header styling configuration.

      

      

### shouldDisplayUnmappedToken

        
        

**Type:** boolean

        

**Description:** Indicates whether unmapped tokens must be displayed in the generated document ( `true`) or not ( `false`). The default value is `false`.

      

      

### shouldExtractEmbeddedTmplToken

        
        

**Type:** boolean

        

**Description:** Indicates whether embedded template tokens must be extracted during processing ( `true`) or not ( `false`). The default value is `false`.

      

      

### status

        
        

**Type:** DocumentTemplateStatus (enumeration of type string)

        

**Description:** Template status that indicates the current state and availability of the document template.

        

Valid values are `Active`, `Archived`, or `Draft`

      

      

### targetTokenItemObject

        
        

**Type:** TargetTokenItemObject (enumeration of type string)

        

**Description:** Target item object for token mapping, defining specific item-level token replacement rules and configurations.

        

Valid values are `OPPORTUNITY_LINE_ITEM`, `ORDER_LINE_ITEM`, or `QUOTE_LINE_ITEM`

      

      

### targetTokenObject

        
        

**Type:** TargetTokenObject (enumeration of type string)

        

**Description:** Target object for token mapping, defining the primary object used for token replacement and data binding.

        

Valid values are `CONTRACT`, `OPPORTUNITY`, `ORDER`, or `QUOTE`

      

      

### tokenList

        
        

**Type:** string

        

**Description:** List of available tokens that can be used within the template for dynamic content generation.

      

      

### tokenMappingMethodType

        
        

**Type:** TokenMappingMethodType (enumeration of type string)

        

**Description:** Token mapping method that defines the approach used for mapping tokens to data values.

        

Valid values are `ContextService`, `CustomClass`, or `OmniDataTransform`. The default value is `ContextService`.

      

      

### tokenMappingType

        
        

**Type:** TokenMappingType (enumeration of type string)

        

**Description:** Required.

        

Defines how tokens are mapped within the template, specifying the token mapping strategy and configuration.

        

Valid values are:

        
          
- `JSON`

          
- `SalesforceObject`

        

      

      

### type

        
        

**Type:** DocumentTemplateType (enumeration of type string)

        

**Description:** Required.

        

Type of document template, defining the category and intended use case of the template.

        

Valid values are:

        
          
- `HTMLArchive`

          
- `Microsoft365Word`

          
- `MicrosoftPowerpoint`

          
- `MicrosoftWord`

          
- `Web`

        

      

      

### uniqueName

        
        

**Type:** string

        

**Description:** Unique ID of the template, ensuring template uniqueness across the organization.

      

      

### usageType

        
        

**Type:** DocumentTemplateUsageType (enumeration of type string)

        

**Description:** Defines how the template is used within the system, specifying the usage context and application scenarios.

        

Valid values are `Contract_Lifecycle_Management` or `Revenue_Lifecycle_Management`

      

      

### versionNumber

        
        

**Type:** string

        

**Description:** Template version number to track template revisions and changes over time.

      

      

### xmlRelationshipMetadata

        
        

**Type:** string

        

**Description:** Relationship metadata in XML format that defines connections and dependencies between template components.

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

This is an example of a DocumentTemplate component.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<DocumentTemplate xmlns="http://soap.sforce.com/2006/04/metadata">
    <customClassName></customClassName>
    <defaultFontStyle>'Times New Roman', times, serif</defaultFontStyle>
    <documentConversionResourceName></documentConversionResourceName>
    <documentGenerationMechanism>ClientSide</documentGenerationMechanism>
    <type>MicrosoftWord</type>
    <usageType>Contract_Lifecycle_Management</usageType>
    <extractOmniDataTransformName>extractorv1</extractOmniDataTransformName>
    <mapperOmniDataTransformName>mapperv1</mapperOmniDataTransformName>
    <fileExtension>docx</fileExtension>
    <hasBatchableSection>false</hasBatchableSection>
    <isActive>false</isActive>
    <isSectionProcessed>false</isSectionProcessed>
    <lastEmbeddedTmplSectionKey></lastEmbeddedTmplSectionKey>
    <name>Sample</name>
    <namespace></namespace>
    <sectionHeaderFontStyle></sectionHeaderFontStyle>
    <sectionHeaderFontStyleValue></sectionHeaderFontStyleValue>
    <shouldDisplayUnmappedToken>false</shouldDisplayUnmappedToken>
    <shouldExtractEmbeddedTmplToken>false</shouldExtractEmbeddedTmplToken>
    <status>Draft</status>
    <tokenList></tokenList>
    <tokenMappingMethodType>OmniDataTransform</tokenMappingMethodType>
    <tokenMappingType>JSON</tokenMappingType>
    <targetTokenItemObject>OPPORTUNITY_LINE_ITEM</targetTokenItemObject>
    <targetTokenObject>CONTRACT</targetTokenObject>
    <uniqueName>Sample_1</uniqueName>
    <versionNumber>1</versionNumber>
    <xmlRelationshipMetadata></xmlRelationshipMetadata>
    <masterLabel>Sample_1</masterLabel>
</DocumentTemplate>
```

        

This is an example `package.xml` that references the previous definition.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>DocumentTemplate</name>
    </types>
    <version>68.0</version>
</Package>
```

      

    

  

    

## Wildcard Support in the Manifest File

    
      
        

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
