---
page_id: meta_esignatureconfig.htm
title: ESignatureConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_esignatureconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# ESignatureConfig

Represents the settings for integrating with external eSignature providers.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its fullName field.

    

    

## File Suffix and Directory Location

      
      

ESignatureConfig components have the suffix .eSignatureConfig and are stored in the eSignatureConfigs folder.

    

    

## Version

      
      

ESignatureConfig components are available in API version 54.0 and later.

    

    

## Special Access Rules

      
      
    

  

    

## Fields

    
      

### configType

        
        

**Type:** ConfigType (enumeration of type string)

        

**Description:** Required.

        

Indicates the configured setting.

        

Possible values are `AnchorString`, `CalloutTimeout`, `EnvelopesLastPollDate`, `SignerRoles`, or `SyncFileSizeLimit`

      

      

### configValue

        
        

**Type:** string

        

**Description:** Required.

        

Indicates the value of the configured setting.

      

      

### description

        
        

**Type:** string

        

**Description:** The description for the configuration setting.

      

      

### groupType

        
        

**Type:** ConfigGroup (enumeration of type string)

        

**Description:** The description for the configuration setting.

        

Possible values are `AnchorTabSetting`, `CalloutConfigurationSetup`, `Envelope`, or `EnvelopeObjectLimits`

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Required.

        

Indicates the name of the setting.

      

      

### vendor

        
        

**Type:** Vendor (enumeration of type string)

        

**Description:** Required.

        

The provider type to which the configuration setting belongs. Currently only `DocuSign` is supported.

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

The following is an example of an ESignatureConfig component.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<ESignatureConfig xmlns="http://soap.sforce.com/2006/04/metadata">
    <configType>AnchorString</configType>
    <groupType>AnchorTabSetting</groupType>
    <configValue>12345</configValue>
    <masterLabel>DocuSignAnchorString</masterLabel>
    <vendor>DocuSign</vendor>
    <description>testdescription</description>
</ESignatureConfig>

```

        

The following is an example `package.xml` that references the previous definition.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>ESignatureConfig</name>
    </types>
    <version>54.0</version>
</Package>
```

      

    

  

    

## Wildcard Support in the Manifest File

    
      

### Wildcard Support in the Manifest File

        
        

This metadata type supports the wildcard character
            `*` (asterisk) in the
            package.xml manifest file. For information about using the manifest
          file, see [Deploying and Retrieving Metadata with the Zip
            File](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/file_based_zip_file.htm).
