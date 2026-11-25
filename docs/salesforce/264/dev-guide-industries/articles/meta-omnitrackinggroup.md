---
page_id: meta-omnitrackinggroup
title: OmniTrackingGroup
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omnitrackinggroup.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-metadata-api-parent
legacy_page_id: meta_omnitrackinggroup.htm
fetched_at: 2026-11-25
---

# OmniTrackingGroup

Represents a group of FlexCard and OmniScript components that have their user interactions tracked together in OmniAnalytics.

**Note:**

This metadata type is part of Omnistudio Standard, not Omnistudio for Vlocity.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/metadata.htm) metadata type and inherits its `fullName` field.

## File Suffix and Directory Location

OmniTrackingGroup components have the suffix `.OmniTrackingGroup` and are stored in the `OmniTrackingGroups` folder.

## Version

OmniTrackingGroup components are available in API version 60.0 and later.

## Special Access Rules

Using OmniAnalytics requires having an Omnistudio license and enabling OmniAnalytics in Setup.

## Fields

### description

- **Field Type**: string

- **Description**: A description of the OmniTrackingGroup.

### developerName

- 

**Field Type**: string

- 

**Description**: Required. The unique name of the OmniTrackingGroup in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters.

**Note:**

When creating large sets of data, always specify a unique `DeveloperName` for each record. If no `DeveloperName` is specified, performance may slow while Salesforce generates one for each record.

**Note:**

Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field.

### endDate

- **Field Type**: date

- **Description**: The date when the OmniTrackingGroup became inactive.

### groupType

- 

**Field Type**: OmniTrackingGroupType (enumeration of type string)

- 

**Description**: Required.

Specifies whether this OmniTrackingGroup sends tracking data to a third-party Analytics system such as Google Analytics.

Values are:

  - `External`—A third-party Analytics system is used.

  - `Internal`—No third-party Analytics system is used.

### isActive

- 

**Field Type**: boolean

- 

**Description**: Required.

Specifies whether the OmniTrackingGroup is active.

### masterLabel

- 

**Field Type**: string

- 

**Description**: Required.

The unique master label of the OmniTrackingGroup. This internal label doesn’t get translated.

### maxAgeInDays

- **Field Type**: int

- **Description**: The maximum number of days the group and its analytics data is active beyond which the data is deleted.

### omniExtTrackingDef

- **Field Type**: string

- **Description**: The ID of the related OmniExtTrackingDef object. Required if `GroupType` is set to `External`.

### omniTrackingComponentDefs

- **Field Type**: [OmniTrackingComponentDef[]](#omnitrackingcomponentdef)

- **Description**: The OmniTrackingComponentDef objects related to this OmniTrackingGroup.

### omniTrackingGroupKey

- **Field Type**: string

- **Description**: A UUID generated internally by Salesforce to uniquely identify an OmniTrackingGroup record across all orgs.

### startDate

- **Field Type**: date

- **Description**: The date when the OmniTrackingGroup became active.

## OmniTrackingComponentDef

Represents a FlexCard or OmniScript that is a member of an OmniTrackingGroup, which tracks user interactions in OmniAnalytics.

### componentType

- 

**Field Type**: OmniAnalyticsComponentType (enumeration of type string)

- 

**Description**: Required.

The type of component for which user interactions are tracked.

Values are:

  - `Flexcard`

  - `Omniscript`

### componentVersion

- 

**Field Type**: double

- 

**Description**: Required.

The version of the FlexCard or OmniScript.

### developerName

- 

**Field Type**: string

- 

**Description**: Required. The unique name of the OmniTrackingComponentDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters.

**Note:**

When creating large sets of data, always specify a unique `DeveloperName` for each record. If no `DeveloperName` is specified, performance may slow while Salesforce generates one for each record.

**Note:**

Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field.

### masterLabel

- 

**Field Type**: string

- 

**Description**: Required.

The unique master label of the OmniTrackingComponentDef. This internal label doesn’t get translated.

### omniTrackingComponentDefKey

- **Field Type**: string

- **Description**: A UUID generated internally by Salesforce to uniquely identify an OmniTrackingComponentDef record across all orgs.

### omniTrackingGroup

- **Field Type**: string

- **Description**: The ID of the related OmniTrackingGroup object.

## Declarative Metadata Sample Definition

The following is an example of an OmniTrackingGroup component.

```
<?xml version="1.0" encoding="UTF-8"?>
<OmniTrackingGroup xmlns="http://soap.sforce.com/2006/04/metadata">
    <developerName>Purchase_Tracking</developerName>
    <groupType>Internal</groupType>
    <isActive>true</isActive>
    <masterLabel>Purchase_Tracking</masterLabel>
    <omniTrackingComponentDefs>
        <componentType>Omniscript</componentType>
        <componentVersion>2</componentVersion>
        <developerName>Purchase_Funnel</developerName>
        <masterLabel>Purchase_Funnel</masterLabel>
    </omniTrackingComponentDefs>
</OmniTrackingGroup>
```

The following is an example `package.xml` that references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>OmniTrackingGroup</name>
    </types>
    <version>60.0</version>
</Package>
```

## Wildcard Support in the Manifest File

### Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the `package.xml` manifest file. For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/file_based_zip_file.htm).

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/meta-omnitrackinggroup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
