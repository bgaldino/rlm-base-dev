---
page_id: sforce-api-objects-omniexttrackingdef
title: OmniExtTrackingDef
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omniexttrackingdef.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-standard-objects-parent
legacy_page_id: sforce_api_objects_omniexttrackingdef.htm
fetched_at: 2026-11-25
---

# OmniExtTrackingDef

Represents a connection between an OmniTrackingGroup in OmniAnalytics and a third-party Analytics system such as Google Analytics. This object is available in API version 60.0 and later.

**Note:**

This object is part of OmniStudio Standard, not OmniStudio for Vlocity.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

Using OmniAnalytics requires having an OmniStudio license and enabling OmniAnalytics in Setup.

## Fields

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: A description of the OmniExtTrackingDef.

### DeveloperName

- 

**Type**: string

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The unique name of the OmniExtTrackingDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters.

**Note:**

When creating large sets of data, always specify a unique `DeveloperName` for each record. If no `DeveloperName` is specified, performance may slow while Salesforce generates one for each record.

**Note:**

Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field.

### IsActive

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Specifies whether the OmniExtTrackingDef is active.

- **Default value**: `true`

### Language

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The language for the OmniExtTrackingDef.

### MasterLabel

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The unique master label of the OmniExtTrackingDef. This internal label doesn’t get translated.

### OmniExtTrackingDefKey

- **Type**: string

- **Properties**: Filter, Group, idLookup, Nillable, Sort

- **Description**: A UUID generated internally by Salesforce to uniquely identify an OmniExtTrackingDef record across all orgs.

### TrackingFrameworkInformation

- **Type**: textarea

- **Properties**: Create, Update

- **Description**: JSON data containing information about an external service, such as the API call and input parameter names.

### TrackingServiceProvider

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: The third-party Analytics system to which user interaction data is sent.

- 

**Default value**: `Google`

- 

**Possible values**:

  - `Google`

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omniexttrackingdef.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
