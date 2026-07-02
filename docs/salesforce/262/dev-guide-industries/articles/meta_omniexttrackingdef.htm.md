---
page_id: meta_omniexttrackingdef.htm
title: OmniExtTrackingDef
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniexttrackingdef.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniExtTrackingDef

Represents a connection between an OmniTrackingGroup in OmniAnalytics and a
third-party Analytics system such as Google Analytics.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This metadata type is part of Omnistudio Standard, not Omnistudio for Vlocity.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on
customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniExtTrackingDef components have the suffix .OmniExtTrackingDef and are stored in the OmniExtTrackingDefs folder.

## Version

OmniExtTrackingDef components are available in API version 60.0 and later.

## Special Access Rules

Using OmniAnalytics requires having an Omnistudio license and enabling OmniAnalytics in
Setup.

## Fields

| Field Name | Description |
| --- | --- |
| description | Field Type  string  Description  A description of the OmniExtTrackingDef. |
| developerName | Field Type  string  Description  Required. The unique name of the OmniExtTrackingDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record.  Note Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| isActive | Field Type  boolean  Description  Required.  Specifies whether the OmniExtTrackingDef is active. |
| masterLabel | Field Type  string  Description  Required.  The unique master label of the OmniExtTrackingDef. This internal label doesn’t get translated. |
| omniExtTrackingDefKey | Field Type  string  Description  A UUID generated internally by Salesforce to uniquely identify an OmniExtTrackingDef record across all orgs. |
| omniExtTrackingEventDefs | Field Type  [OmniExtTrackingEventDef[]](#OmniExtTrackingEventDef)  Description  The OmniExtTrackingEventDef objects related to this OmniExtTrackingDef. |
| trackingFrameworkInformation | Field Type  string  Description  Required.  JSON data containing information about an external service, such as the API call and input parameter names. |
| trackingServiceProvider | Field Type  ExternalTrackingVendor (enumeration of type string)  Description  Required.  The third-party Analytics system to which user interaction data is sent.  Values are:   - `Google` - `Mixpanel` |

## OmniExtTrackingEventDef

Represents a format for FlexCard or OmniScript user interaction data that a third-party
Analytics system such as Google Analytics can accept.

| Field Name | Description |
| --- | --- |
| componentType | Field Type  OmniAnalyticsComponentType (enumeration of type string)  Description  Required.  The type of component for which user interactions are tracked.  Values are:   - `Flexcard` - `Omniscript` |
| description | Field Type  string  Description  A description of the OmniExtTrackingEventDef. |
| developerName | Field Type  string  Description  Required. The unique name of the OmniExtTrackingEventDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record.  Note Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| inclusionRule | Field Type  string  Description  Required.  A true-or-false condition that determines whether an event is sent to the third-party Analytics system. |
| masterLabel | Field Type  string  Description  Required.  The unique master label of the OmniExtTrackingEventDef. This internal label doesn’t get translated. |
| omniExtTrackingDef | Field Type  string  Description  The ID of the related OmniExtTrackingDef object. |
| omniExtTrackingEventDefKey | Field Type  string  Description  A UUID generated internally by Salesforce to uniquely identify an OmniExtTrackingEventDef record across all orgs. |
| payloadTemplate | Field Type  string  Description  Required.  The payload template structure with placeholders for runtime data. This is used at runtime to generate the actual payload to be sent to the external Analytics service. |

## Declarative Metadata Sample Definition

The following is an example of an OmniExtTrackingDef component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniExtTrackingDef xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>Purchase_Tracking_Google</developerName>
    <isActive>true</isActive>
    <masterLabel>Purchase_Tracking_Google</masterLabel>
    <trackingFrameworkInformation>{ "id": "GTM-XXXXXXX" }</trackingFrameworkInformation>
    <trackingServiceProvider>Google</trackingServiceProvider>
    <omniExtTrackingEventDefs>
        <componentType>Omniscript</componentType>
        <developerName>Purchase_Funnel_Google</developerName>
        <inclusionRule></inclusionRule>
        <masterLabel>Purchase_Funnel_Google</masterLabel>
        <payloadTemplate>
{
  "event": "promotionClick",
  "ecommerce": {
    "promoClick": {
      "promotions": [
        {
          "name": "%BusinessEvent%"
        }
      ]
    }
  }
}
        </payloadTemplate>
    </omniExtTrackingEventDefs>
</OmniExtTrackingDef>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniExtTrackingDef</name>
    </types>
    <version>60.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information
about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
