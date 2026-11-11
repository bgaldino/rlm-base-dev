---
page_id: meta_contextusecasemapping.htm
title: ContextUseCaseMapping
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_contextusecasemapping.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# ContextUseCaseMapping

Represents the setup object that stores configuration details for the context service for Salesforce Contracts.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its fullName field.

    

    

## File Suffix and Directory Location

      
      

ContextUseCaseMapping components have the suffix .contextUseCaseMapping and are stored in the contextUseCaseMappings folder.

    

    

## Version

      
      

ContextUseCaseMapping components are available in API version 61.0 and later.

    

    

## Special Access Rules

      
      

Requires Context Service to be enabled in the organization. This metadata type is specifically designed for contract lifecycle management and is part of the broader Context Service architecture for Industries solutions.

    

  

    

## Fields

    
      

### contextDefinition​Name

        
        

**Type:** string

        

**Description:** Required. Name of the context definition that stores hydration and persistence mapping details. References a [ContextDefinition](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_contextdefinition.htm) component that describes the relationship between node structures within a context.

      

      

### mappingName

        
        

**Type:** string

        

**Description:** Required. Name of the mapping associated with the mapping type. Examples include `OppToCntrHydrationMapping` for hydration scenarios and `OppToCntrPersistenceMapping` for persistence scenarios.

      

      

### mappingType

        
        

**Type:** ContextMappingType (enumeration of type string)

        

**Description:** Required. Mapping type used for context use case mappings. Valid values are `Hydration`—Mapping type for data retrieval and population from source objects or `Persistence`—Mapping type for data storage and updates to target objects

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Required. User-friendly name for the context use case mapping that appears in the user interface.

      

      

### referenceObject​Name

        
        

**Type:** string

        

**Description:** The standard or custom source object that the context mapping is fetched from. This field represents the originating object for the mapping relationship.

      

      

### referenceObject​RecordType

        
        

**Type:** string

        

**Description:** The record types associated with the reference object. This field is used for record type-specific mapping configurations within the same object type. Available in API version 61.0 and later.

      

      

### targetObject​CustomFieldName

        
        

**Type:** string

        

**Description:** Name of the custom field in the target object used to link the target object with the reference object. This field must be a valid field in the target object and establishes the relationship between source and target objects.

      

      

### targetObject​Name

        
        

**Type:** string

        

**Description:** Name of the standard or custom object that the context mapping from the reference object is pushed to. This represents the destination object for the mapping relationship, typically the Contract object.

      

      

### targetObject​RecordType

        
        

**Type:** string

        

**Description:** The record types associated with the target object. This field is used for record type-specific configurations within the target object, typically associated with the Contract object.

      

      

### useCaseType

        
        

**Type:** ContextUseCaseType (enumeration of type string)

        

**Description:** Required. Type of use case that defines the purpose and scope of the context mapping. Valid values are:

        
          
- 
`ContractCreationOrUpdation`—Use case for creating or updating contracts from source objects

          
- 
`ContractExtraction`—Use case for extracting contract data for document generation or other processes

        

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

This is an example of a ContextUseCaseMapping component.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<ContextUseCaseMapping xmlns="http://soap.sforce.com/2006/04/metadata">
    <contextDefinitionName>TestDefName</contextDefinitionName>
    <mappingName>TestMapName</mappingName>
    <mappingType>Hydration</mappingType>
    <masterLabel>TestMLabel</masterLabel>
    <referenceObjectName>Opportunity</referenceObjectName>
    <referenceObjectRecordType>TestOppRT</referenceObjectRecordType>
    <targetObjectCustomFieldName>SourceOpportunityId</targetObjectCustomFieldName>
    <targetObjectName>Contract</targetObjectName>
    <targetObjectRecordType>TestOppRT</targetObjectRecordType>
    <useCaseType>ContractCreationOrUpdation</useCaseType>
</ContextUseCaseMapping>
```

        

This is an example `package.xml` that references the previous definition.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>TestPkg</fullName>
    <types>
        <members>Opportunity.TestSalesProcess</members>
        <name>BusinessProcess</name>
    </types>
    <types>
        <members>TestDName</members>
        <name>ContextUseCaseMapping</name>
    </types>
    <types>
        <members>Contract.ContractLifecycleManagement</members>
        <members>Opportunity.TestOppRT</members>
        <name>RecordType</name>
    </types>
    <version>68.0</version>
</Package>
```

      

    

  

    

## Wildcard Support in the Manifest File

    
      
        

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
