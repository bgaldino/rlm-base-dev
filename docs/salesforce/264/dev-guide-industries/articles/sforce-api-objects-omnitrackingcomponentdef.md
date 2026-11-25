---
page_id: sforce-api-objects-omnitrackingcomponentdef
title: OmniTrackingComponentDef
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omnitrackingcomponentdef.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-standard-objects-parent
legacy_page_id: sforce_api_objects_omnitrackingcomponentdef.htm
fetched_at: 2026-11-25
---

# OmniTrackingComponentDef

Represents a FlexCard or OmniScript that is a member of an OmniTrackingGroup, which tracks user interactions in OmniAnalytics. This object is available in API version 60.0 and later.

**Note:**

This object is part of OmniStudio Standard, not OmniStudio for Vlocity.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

Using OmniAnalytics requires having an OmniStudio license and enabling OmniAnalytics in Setup.

## Fields

### ComponentType

- 

**Type**: picklist

- 

**Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- 

**Description**: The type of component for which user interactions are tracked.

- 

**Possible values**:

  - `Flexcard`

  - `Omniscript`

### ComponentVersion

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The version of the FlexCard or OmniScript.

### DeveloperName

- 

**Type**: string

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The unique name of the OmniTrackingComponentDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters.

**Note:**

When creating large sets of data, always specify a unique `DeveloperName` for each record. If no `DeveloperName` is specified, performance may slow while Salesforce generates one for each record.

**Note:**

Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field.

### Language

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The language for the OmniTrackingComponentDef.

### MasterLabel

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The unique master label of the OmniTrackingComponentDef. This internal label doesn’t get translated.

### OmniTrackingComponentDefKey

- **Type**: string

- **Properties**: Filter, Group, idLookup, Nillable, Sort

- **Description**: A UUID generated internally by Salesforce to uniquely identify an OmniTrackingComponentDef record across all orgs.

### OmniTrackingGroup

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Sort, Update

- 

**Description**: The ID of the related OmniTrackingGroup object.

This field is a relationship field.

- 

**Relationship Name**: OmniTrackingGroup

- 

**Relationship Type**: Lookup

- 

**Refers To**: OmniTrackingGroup

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-omnitrackingcomponentdef.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
