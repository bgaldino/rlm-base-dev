---
page_id: meta-omniinteractionaccessconfig
title: OmniInteractionAccessConfig
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omniinteractionaccessconfig.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
legacy_page_id: meta_omniinteractionaccessconfig.htm
fetched_at: 2026-11-25
---

# OmniInteractionAccessConfig

Represents configuration settings for access to Omnistudio FlexCard caching and data sources.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

OmniInteractionAccessConfig components have the suffix `.omniInteractionAccessConfig` and are stored in the `OmniInteractionAccessConfig` folder.

## Version

OmniInteractionAccessConfig components are available in API version 53.0 and later.

## Special Access Rules

OmniInteractionAccessConfig is available if your org has the Omnistudio platform license and related addon and user licenses.

## Fields

### configName

- **Field Type**: string

- **Description**: Not used.

### isAsyncCardCachingEnabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, enables asynchronous FlexCard caching.

- **Default value**: `false`

### isCardApexRemoteDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables remote Apex method calls for FlexCards.

- **Default value**: `false`

### isCardCacheDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables FlexCard caching.

- **Default value**: `false`

### isCardDataTfrmDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables Data Mapper data sources for FlexCards.

- **Default value**: `false`

### isCardIntegrationProcDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables Integration Procedure data sources for FlexCards.

- **Default value**: `false`

### isCardRestApiDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables REST calls for FlexCards.

- **Default value**: `false`

### isCardSoqlDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables SOQL queries for FlexCards.

- **Default value**: `false`

### isCardSoslDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables SOSL queries for FlexCards.

- **Default value**: `false`

### isCardStreamingApiDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables Streaming API calls for FlexCards.

- **Default value**: `false`

### isDataTfrmEncrpFieldsDisabled

- **Field Type**: boolean

- **Description**: Required. If set to `true`, disables Data Mapper field encryption for FlexCards.

- **Default value**: `false`

### masterLabel

- **Field Type**: string

- **Description**: Required. The name of the setting. The value is `Profile_`*ProfileId*, `User_`*UserId*, or `Org_Wide`.

### setupOwner

- **Field Type**: string

- **Description**: The ID of the profile, user, or org to which the settings apply.

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

The following is an example `package.xml` that references the previous definition.

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

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omniinteractionaccessconfig.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
