---
page_id: sforce_api_objects_caseproceeding.htm
title: CaseProceeding
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_caseproceeding.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Collections and Recovery
parent_page: collections_standard_objects.htm
fetched_at: 2026-06-25
---

# CaseProceeding

Represents a legal and formal demand for the enforcement of an individual’s
rights against another party in a court of justice. This object is available in API
version 64.0 and later.

## Special Access Rules

This is a standard
object and is available with Collections and Recovery permission set in API version 64.0
and later.

## Fields

| Field | Details |
| --- | --- |
| AddressId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Address of the location where the case proceeding is being conducted.  This field is a relationship field.  Relationship Name  Address  Relationship Type  Lookup  Refers To  Address |
| ApplicationId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The relationship between case proceeding and a business license application or an individual application.  This field is a polymorphic relationship field.  Relationship Name  Application  Relationship Type  Lookup  Refers To  BusinessLicenseApplication, IndividualApplication |
| CaseFilingDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The data and time when the case proceeding was initiated. |
| CaseId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The case associated with the case proceeding record.  This field is a relationship field.  Relationship Name  Case  Relationship Type  Lookup  Refers To  Case |
| Description | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The description of the case proceeding record. |
| EndDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the case proceeding was completed. |
| ExternalCaseIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier of the related case in an external system. |
| ExternalIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier for this case proceeding. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the case proceeding record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the case proceeding record owner.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| RelatedCaseProceedingId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of a case proceeding related to this case proceeding.  This field is a relationship field.  Relationship Name  RelatedCaseProceeding  Relationship Type  Lookup  Refers To  CaseProceeding |
| StartDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time from when the case proceeding began. |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Specifies the status of the case proceeding.  Possible values are:  - `Completed` - `Planned` |
| SubType | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The subtype of the case proceeding.  Possible values are:  - `Appeal` - `Disposition` - `Review Hearing` |
| TotalLegalExpenses | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  Total legal proceeding expenses for the case associated with a collection plan. |
| Type | Type  picklist  Properties  Create, Filter, Group, Sort, Update  Description  The type of case proceeding.  Possible values are:  - `Board Proceeding` - `Court Action` - `Mediation` - `Warrant Request` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

[CaseProceedingFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "StandardObjectNameFeed is the model for all feed objects associated with standard objects. These objects represent the posts and feed-tracked changes of a standard object.")
:   Feed tracking is available for the object.

[CaseProceedingHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object.")
:   History is available for tracked fields of the object.

[CaseProceedingOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm "StandardObjectNameOwnerSharingRule is the model for all owner sharing rule objects associated with standard objects. These objects represent a rule for sharing a standard object with users other than the owner.")
:   Sharing rules are available for the object.

[CaseProceedingShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.")
:   Sharing is available for the object.
