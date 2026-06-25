---
page_id: sforce_api_objects_omnitrackinggroup.htm
title: OmniTrackingGroup
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_omnitrackinggroup.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_standard_objects_parent.htm
fetched_at: 2026-06-25
---

# OmniTrackingGroup

Represents a group of FlexCard and OmniScript components that have their user
interactions tracked together in OmniAnalytics. This object is available in API
version 60.0 and later.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This object is part of OmniStudio Standard, not OmniStudio for Vlocity.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=industries_reference)

#### Important

Where possible, we changed noninclusive terms to align with our
company value of Equality. We maintained certain terms to avoid any effect on customer
implementations.

## Supported Calls

`create()`,
`delete()`,
`describeSObjects()`,
`query()`,
`retrieve()`,
`update()`,
`upsert()`

## Special Access Rules

Using OmniAnalytics requires having an
OmniStudio license and enabling OmniAnalytics in Setup.

## Fields

| Field | Details |
| --- | --- |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A description of the OmniTrackingGroup. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the OmniTrackingGroup in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record.  Note Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| EndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date when the OmniTrackingGroup became inactive. |
| GroupType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies whether this OmniTrackingGroup sends tracking data to a third-party Analytics system such as Google Analytics.  Possible values are:  - `External`—A   third-party Analytics system is used. - `Internal`—No   third-party Analytics system is used. |
| IsActive | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Specifies whether the OmniTrackingGroup is active.  The default value is `false`. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language for the OmniTrackingGroup. |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique master label of the OmniTrackingGroup. This internal label doesn’t get translated. |
| MaxAgeInDays | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The maximum number of days the group and its analytics data is active beyond which the data is deleted. |
| OmniExtTrackingDef | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the related OmniExtTrackingDef object. Required if GroupType is set to `External`.  This field is a relationship field.  Relationship Name  OmniExtTrackingDef  Relationship Type  Lookup  Refers To  OmniExtTrackingDef |
| OmniTrackingGroupKey | Type  string  Properties  Filter, Group, idLookup, Nillable, Sort  Description  A UUID generated internally by Salesforce to uniquely identify an OmniTrackingGroup record across all orgs. |
| StartDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date when the OmniTrackingGroup became active. |
