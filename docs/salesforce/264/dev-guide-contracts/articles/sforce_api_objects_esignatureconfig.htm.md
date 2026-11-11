---
page_id: sforce_api_objects_esignatureconfig.htm
title: ESignatureConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_esignatureconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ESignatureConfig

The settings for integrating with external eSignature providers. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ConfigType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** Indicates the configured setting.

        

Possible values are:

        
          
- `AnchorString`

          
- `SignerRoles`

          
- `SyncFileSizeLimit`

          
- `CalloutTimeout`

          
- `EnvelopesLastPollDate`

          
- `CalloutNamedCredential`

          
- `eSignVendorAccountId`

          
- `RecipientsCustomClass`

          
- `DocumentsCustomClass`

        

        

The default value is 'AnchorString'.

      

      

### ConfigValue

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Sort, Update

        

**Description:** Value of the configured setting.

      

      

### Description

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The description for the configuration setting.

      

      

### GroupType

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The group to which the configuration setting belongs.

        

Possible values are:

        
          
- `AnchorTabSetting`

          
- `EnvelopeObjectLimits`

          
- `CalloutConfigurationSetup`

          
- `Envelope`

          
- `eSignVendorAccount`

          
- `CustomClassSetting`

        

      

      

### Vendor

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The provider type to which the configuration setting belongs. Currently only DocuSign is supported.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ESignatureConfigChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ESignatureConfigFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ESignatureConfigHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ESignatureConfigOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ESignatureConfigShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
