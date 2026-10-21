---
page_id: sforce_api_objects_esignatureenvelopeconfig.htm
title: ESignatureEnvelopeConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/sforce_api_objects_esignatureenvelopeconfig.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_objects_overview.htm
fetched_at: 2026-10-13
---

# ESignatureEnvelopeConfig

The notification-specific settings for integrating with external eSignature providers. This object is available in API version 56.0 and later.

    

## Supported Calls

      
      

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

    

  

    

## Fields

    
      

### ExpirationPeriod

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The expiration period for signing.

      

      

### ExpirationWarningPeriod

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The number of days before expiration for warning notifications.

      

      

### FirstReminderPeriod

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The number of days between envelope delivery and the first reminder email.

      

      

### IsExpirationEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether expiration is enabled.

        

The default value is 'false'.

      

      

### IsReminderEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether reminders are enabled.

        

The default value is 'false'.

      

      

### IsVendorDefaultNtfcnEnabled

        
        

**Type:** boolean

        

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

        

**Description:** Indicates whether the envelope uses account default notification settings.

        

The default value is 'false'.

      

      

### ReminderIntervalPeriod

        
        

**Type:** int

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The interval in days between reminder emails.

      

      

### TargetObjectName

        
        

**Type:** picklist

        

**Properties:** Create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The object to which the eSignature applies, such as an Opportunity, Quote, or Order.

      

      

### Vendor

        
        

**Type:** picklist

        

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

        

**Description:** The eSignature provider, for example DocuSign.

      

      

### VendorAccountIdentifier

        
        

**Type:** string

        

**Properties:** Create, Filter, Group, Nillable, Sort, Update

        

**Description:** The eSignature branding identifier.

      

    

  

    

## Associated Objects

    
      
        

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

        

**[ESignatureEnvelopeConfigChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_change_event.htm):** Change events are available for the object.

        

**[ESignatureEnvelopeConfigFeed](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm):** Feed tracking is available for the object.

        

**[ESignatureEnvelopeConfigHistory](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm):** History is available for tracked fields of the object.

        

**[ESignatureEnvelopeConfigOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_ownersharingrule.htm):** Sharing rules are available for the object.

        

**[ESignatureEnvelopeConfigShare](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm):** Sharing is available for the object.
