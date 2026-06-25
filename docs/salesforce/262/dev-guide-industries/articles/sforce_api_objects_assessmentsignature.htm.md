---
page_id: sforce_api_objects_assessmentsignature.htm
title: AssessmentSignature
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentsignature.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentSignature

Stores the respondent’s signature during an assessment. This object is
available in API version 57.0 and later.

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
| AssessmentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The assessment that's associated with the signature.  This field is a relationship field.  Relationship Name  Assessment  Relationship Type  Lookup  Refers To  Assessment |
| DateTime | Type  dateTime  Properties  Create, Filter, Sort, Update  Description  The date and time of signature. |
| DigitalSignatureId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The digital signature that's associated with the assessment signature record.  This field is a relationship field.  Relationship Name  DigitalSignature  Relationship Type  Lookup  Refers To  DigitalSignature |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of this assessment signature record. |
| OmniscriptIdentifier | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Identifier of signature instance in OmniScript Form. |
| Place | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The location at the time of signature. |
| SignedBy | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  The name of the individual who signed the assessment. |
| SignedInitial | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The initial used when signing the assessment. |
| SigneeId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The user or contact who signed the assessment.  This field is a polymorphic relationship field.  Relationship Name  Signee  Relationship Type  Lookup  Refers To  Contact, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentSignatureChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentSignatureFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentSignatureHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssessmentSignatureOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)
:   Sharing rules are available for the object.

[AssessmentSignatureShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
