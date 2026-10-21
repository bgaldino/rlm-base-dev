---
page_id: meta_externaldocstorageconfig.htm
title: ExternalDocStorageConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_externaldocstorageconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# ExternalDocStorageConfig

Represents configuration, which admin makes in setup to specify the drive, path, and named credential to be used for storing documents on external drives.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits fullName field.

    

    

## File Suffix and Directory Location

      
      

ExternalDocStorageConfig components have the suffix .externalDocStorageConfig and are stored in the externalDocStorageConfigs folder.

    

    

## Version

      
      

ExternalDocStorageConfig components are available in API version 57.0 and later.

    

  

    

## Fields

    
      

### documentPath

        
        

**Type:** string

        

**Description:** Required.

        

The path from the root in the external storage where documents are stored.

      

      

### externalDocStorageIdentifier

        
        

**Type:** string

        

**Description:** Required.

        

The ID of the external document storage.

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Required.

        

A user-friendly name for ExternalDocStorageConfig, which is defined when the ExternalDocStorageConfig is created.

      

      

### namedCredential

        
        

**Type:** string

        

**Description:** Required.

        

The Named Credential associated with the External Document Storage Configuration. A named credential can be specified as an endpoint to simplify the setup of authenticated call outs.

      

      

### recordType

        
        

**Type:** string

        

**Description:** The record type associated with the Reference object.

      

      

### storageDriveType

        
        

**Type:** StorageDriveType (enumeration of type string)

        

**Description:** Required.

        

The external document storage drive. Possible value is MicrosoftOneDrive

      

      

### targetObject

        
        

**Type:** TargetObject (enumeration of type string)

        

**Description:** The target object associated with the external document storage. Possible values are `All`, `Contract`, `DocumentTemplate`, `Disclosure`, or `InfoLibraryExternalDocument`

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

The following is an example of a ExternalDocStorageConfig component.

        

```
 
<?xml version="1.0" encoding="UTF-8"?>
<ExternalDocStorageConfig
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<documentPath>/Salesforce/Contracts/</documentPath>
	<externalDocStorageIdentifier>ExternalDocIdTest1234</externalDocStorageIdentifier>
	<masterLabel>Contract_Contract_Lifecycle_Management</masterLabel>
	<namedCredential>Salesforce</namedCredential>
	<recordType>ContractLifecycleManagement</recordType>
	<storageDriveType>MicrosoftOneDrive</storageDriveType>
	<targetObject>Contract</targetObject>
</ExternalDocStorageConfig>
```

        

The following is an example `package.xml` that references the previous definition.

        

```

<?xml version="1.0" encoding="UTF-8"?>
<Package
	xmlns="http://soap.sforce.com/2006/04/metadata">
	<fullName>ExternalDocStorageConfigObjectPackage</fullName>
	<types>
		<members>Contract_Contract_Lifecycle_Management</members>
		<name>ExternalDocStorageConfig</name>
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
