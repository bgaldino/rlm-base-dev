---
page_id: sforce_api_objects_assessmentreason.htm
title: AssessmentReason
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentreason.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentReason

Represents the reasons for an assessment such as the associated coverage
information. This object is available in API version 63.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the record was last referenced. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date when the record was last viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the record. |
| ParentAssessmentId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The parent assessment record that this assessment record belongs to.  This field is a relationship field.  Relationship Name  ParentAssessment  Relationship Type  Master-detail  Refers To  Assessment (the master object) |
| ReferenceRecordId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The reason for the assessment.  This field is a polymorphic relationship field.  Relationship Name  ReferenceRecord  Refers To  ClinicalServiceRequest, MedicationRequest |
| ReferenceValue | Type  textarea  Properties  Create, Nillable, Update  Description  The assessment reason in JSON format when there is no Salesforce record to be added as the reference record. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentReasonChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentReasonFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentReasonHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
