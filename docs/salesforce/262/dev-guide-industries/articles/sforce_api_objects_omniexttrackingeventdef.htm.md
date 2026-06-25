---
page_id: sforce_api_objects_omniexttrackingeventdef.htm
title: OmniExtTrackingEventDef
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_omniexttrackingeventdef.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_standard_objects_parent.htm
fetched_at: 2026-06-25
---

# OmniExtTrackingEventDef

Represents a format for FlexCard or OmniScript user interaction data that a
third-party Analytics system such as Google Analytics can accept. This object is
available in API version 60.0 and later.

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

Using OmniAnalytics requires having an OmniStudio license and enabling OmniAnalytics in
Setup.

## Fields

| Field | Details |
| --- | --- |
| ComponentType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  The type of component for which user interactions are tracked.  Possible values are:  - `Flexcard` - `Omniscript` |
| Description | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A description of the OmniExtTrackingEventDef. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique name of the OmniExtTrackingEventDef in the API. This name can contain only underscores and alphanumeric characters and must be unique in your organization. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. Limit: 80 characters. Note Note When creating large sets of data, always specify a unique DeveloperName for each record. If no DeveloperName is specified, performance may slow while Salesforce generates one for each record.  Note Note Only users with View DeveloperName OR View Setup and Configuration permission can view, group, sort, and filter this field. |
| InclusionRule | Type  textarea  Properties  Create, Nillable, Update  Description  A true-or-false condition that determines whether an event is sent to the third-party Analytics system. |
| Language | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The language for the OmniExtTrackingEventDef. |
| MasterLabel | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The unique master label of the OmniExtTrackingEventDef. This internal label doesn’t get translated. |
| OmniExtTrackingDef | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The ID of the related OmniExtTrackingDef object.  This field is a relationship field.  Relationship Name  OmniExtTrackingDef  Relationship Type  Lookup  Refers To  OmniExtTrackingDef |
| OmniExtTrackingEventDefKey | Type  string  Properties  Filter, Group, idLookup, Nillable, Sort  Description  A UUID generated internally by Salesforce to uniquely identify an OmniExtTrackingEventDef record across all orgs. |
| PayloadTemplate | Type  textarea  Properties  Create, Nillable, Update  Description  The payload template structure with placeholders for runtime data. This is used at runtime to generate the actual payload to be sent to the external Analytics service. |
