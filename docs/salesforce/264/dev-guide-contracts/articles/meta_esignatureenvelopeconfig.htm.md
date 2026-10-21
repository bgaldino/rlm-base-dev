---
page_id: meta_esignatureenvelopeconfig.htm
title: ESignatureEnvelopeConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/meta_esignatureenvelopeconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-10-13
---

# ESignatureEnvelopeConfig

Represents the notification-specific settings for integrating with external eSignature providers.

    
      

#### Important

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

    

    

## Parent Type

      
      

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its fullName field.

    

    

## File Suffix and Directory Location

      
      

ESignatureEnvelopeConfig components have the suffix .eSignatureEnvelopeConfig and are stored in the eSignatureEnvelopeConfigs folder.

    

    

## Version

      
      

ESignatureEnvelopeConfig components are available in API version 54.0 and later.

    

    

## Special Access Rules

      
      
    

  

    

## Fields

    
      

### expirationPeriod

        
        

**Type:** integer

        

**Description:** The expiration period for signing.

      

      

### expirationWarningPeriod

        
        

**Type:** integer

        

**Description:** The number of days before expiration for warning notifications.

      

      

### firstReminderPeriod

        
        

**Type:** integer

        

**Description:** The number of days between envelope delivery and the first reminder email.

      

      

### isExpirationEnabled

        
        

**Type:** boolean

        

**Description:** Indicates whether expiration is enabled.

      

      

### isReminderEnabled

        
        

**Type:** boolean

        

**Description:** Indicates whether reminders are enabled.

      

      

### isVendorDefaultNtfcnEnabled

        
        

**Type:** boolean

        

**Description:** Indicates whether the envelope uses account default notification settings.

      

      

### masterLabel

        
        

**Type:** string

        

**Description:** Required.

        

The name of the setting.

      

      

### reminderIntervalPeriod

        
        

**Type:** integer

        

**Description:** The interval in days between reminder emails.

      

      

### targetObjectName

        
        

**Type:** string

        

**Description:** Required.

        

The object to which the eSignature applies, such as an Opportunity, Quote, or Order.

      

      

### vendor

        
        

**Type:** Vendor (enumeration of type string)

        

**Description:** Required.

        

The provider type to which the configuration setting belongs. Currently only `DocuSign` is supported.

      

      

### vendorAccountIdentifier

        
        

**Type:** string

        

**Description:** The eSignature branding identifier.

      

    

  

    

## Declarative Metadata Sample Definition

    
      
        

The following is an example of an ESignatureEnvelopeConfig component.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<ESignatureEnvelopeConfig xmlns="http://soap.sforce.com/2021/10/metadata">
    <masterLabel>DocuSign_Contract</masterLabel>
    <targetObjectName>Contract</targetObjectName>
    <vendorAccountIdentifier>vai</vendorAccountIdentifier>
    <isExpirationEnabled>true</isExpirationEnabled>
    <expirationPeriod>2</expirationPeriod>
    <expirationWarningPeriod>2</expirationWarningPeriod>
    <isReminderEnabled>true</isReminderEnabled>
    <firstReminderPeriod>2</firstReminderPeriod>
    <reminderIntervalPeriod>2</reminderIntervalPeriod>
    <isVendorDefaultNtfcnEnabled>true</isVendorDefaultNtfcnEnabled>
    <vendor>DocuSign</vendor>
</ESignatureEnvelopeConfig>
```

        

The following is an example `package.xml` that references the previous definition.

        

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2021/10/metadata">
    <types>
        <members>*</members>
        <name>ESignatureEnvelopeConfig</name>
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
