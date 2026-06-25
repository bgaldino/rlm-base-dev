---
page_id: meta_omniinteractionaccessconfig.htm
title: OmniInteractionAccessConfig
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/meta_omniinteractionaccessconfig.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-06-25
---

# OmniInteractionAccessConfig

Represents configuration settings for access to Omnistudio
FlexCard caching and data sources.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)")
metadata type and inherits its fullName field.

## File Suffix and Directory Location

OmniInteractionAccessConfig components have the suffix
.omniInteractionAccessConfig and are stored in the
OmniInteractionAccessConfig folder.

## Version

OmniInteractionAccessConfig components are available in API version 53.0 and later.

## Special Access Rules

OmniInteractionAccessConfig is available if your org has the Omnistudio platform license
and related addon and user licenses.

## Fields

| Field Name | Field Type | Description |
| --- | --- | --- |
| configName | string | Not used. |
| isAsyncCardCachingEnabled | boolean | Required. If set to `true`, enables asynchronous FlexCard caching. The default is `false`. |
| isCardApexRemoteDisabled | boolean | Required. If set to `true`, disables remote Apex method calls for FlexCards. The default is `false`. |
| isCardCacheDisabled | boolean | Required. If set to `true`, disables FlexCard caching. The default is `false`. |
| isCardDataTfrmDisabled | boolean | Required. If set to `true`, disables Data Mapper data sources for FlexCards. The default is `false`. |
| isCardIntegrationProcDisabled | boolean | Required. If set to `true`, disables Integration Procedure data sources for FlexCards. The default is `false`. |
| isCardRestApiDisabled | boolean | Required. If set to `true`, disables REST calls for FlexCards. The default is `false`. |
| isCardSoqlDisabled | boolean | Required. If set to `true`, disables SOQL queries for FlexCards. The default is `false`. |
| isCardSoslDisabled | boolean | Required. If set to `true`, disables SOSL queries for FlexCards. The default is `false`. |
| isCardStreamingApiDisabled | boolean | Required. If set to `true`, disables Streaming API calls for FlexCards. The default is `false`. |
| isDataTfrmEncrpFieldsDisabled | boolean | Required. If set to `true`, disables Data Mapper field encryption for FlexCards. The default is `false`. |
| masterLabel | string | Required. The name of the setting. The value is `Profile_`ProfileId, `User_`UserId, or `Org_Wide`. |
| setupOwner | string | The ID of the profile, user, or org to which the settings apply. |

## Declarative Metadata Sample Definition

The following is an example of an OmniInteractionAccessConfig component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniInteractionAccessConfig xmlns="http://soap.sforce.com/2021/10/metadata">
   <isAsyncCardCachingEnabled>false</isAsyncCardCachingEnabled>
   <isCardApexRemoteDisabled>false</isCardApexRemoteDisabled>
   <isCardCacheDisabled>false</isCardCacheDisabled>
   <isCardDataTfrmDisabled>false</isCardDataTfrmDisabled>
   <isCardIntegrationProcDisabled>false</isCardIntegrationProcDisabled>
   <isCardRestApiDisabled>false</isCardRestApiDisabled>
   <isCardSoqlDisabled>false</isCardSoqlDisabled>
   <isCardSoslDisabled>false</isCardSoslDisabled>
   <isCardStreamingApiDisabled>false</isCardStreamingApiDisabled>
   <isDataTfrmEncrpFieldsDisabled>false</isDataTfrmEncrpFieldsDisabled>
   <masterLabel>Profile_00eB0000000ijOH</masterLabel>
   <setupOwner>00eB0000000ijOH</setupOwner>
</OmniInteractionAccessConfig>
```

The following is an example `package.xml` that references the previous
definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2021/10/metadata">
    <types>
        <members>*</members>
        <name>OmniInteractionAccessConfig</name>
    </types>
    <version>53.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*`
(asterisk) in the package.xml manifest file. For information about
using the manifest file, see [Deploying and
Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
