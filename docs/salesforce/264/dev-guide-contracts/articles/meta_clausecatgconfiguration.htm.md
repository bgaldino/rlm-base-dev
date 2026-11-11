---
page_id: meta_clausecatgconfiguration.htm
title: ClauseCatgConfiguration
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_clausecatgconfiguration.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# ClauseCatgConfiguration

Represents the configuration about the library category that can be used by a user in their response document.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits fullName field.

    

    

## File Suffix and Directory Location

      
      

ClauseCatgConfiguration components have the suffix .clauseCatgConfiguration and are stored in the clauseCatgConfigurations folder.

    

    

## Version

      
      

ClauseCatgConfiguration components are available in API version 57.0 and later.

    

    

## Special Access Rules

      
      

ClauseManagementAddOn license is required.

    

  

    

## Fields

    
      

### description

        
        

**Type:** string

        

**Description:** The description about the clause category configuration.

      

      

### isProtected

        
        

**Type:** boolean

        

**Description:** An auto-generated value that doesn’t currently impact the behavior of the metadata type.

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Required.

        

A user-friendly name for ClauseCatgConfiguration, which is defined when the ClauseCatgConfiguration is created.

      

      

### usageType

        
        

**Type:** ClmCategoryUsageType (enumeration of type string)

        

**Description:** Required.

        

The usage type of the clause category configuration. Possible values are `ContractClauseCategory` or `DisclosureCategory`

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

The following is an example of a ClauseCatgConfiguration component.

        

```

<?xml version="1.0" encoding="UTF-8"?>
<ClauseCatgConfiguration
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<description>This is how to add description for Contract Clause Category</description>
	<usageType>ContractClauseCategory</usageType>
	<isProtected>false</isProtected>
	<masterLabel>Contract Clause Cat</masterLabel>
</ClauseCatgConfiguration>
```

        

The following is an example `package.xml` that references the previous definition.

        

```

<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<fullName>Pkg</fullName>
	<types>
		<members>DisclosureCategory</members>
		<members>ContractClauseCategory</members>
		<name>ClauseCatgConfiguration</name>
	</types>
	<version>57.0</version>
</Package>
```

      

    

  

    

## Wildcard Support in the Manifest File

    
      

### Wildcard Support in the Manifest File

        
        

This metadata type supports the wildcard character
            `*` (asterisk) in the
            package.xml manifest file. For information about using the manifest
          file, see [Deploying and Retrieving Metadata with the Zip
            File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
