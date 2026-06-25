---
page_id: sforce_api_objects_assessmentquestion.htm
title: AssessmentQuestion
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentquestion.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentQuestion

Stores the questions required for an assessment. This object is
available in API version 55.0 and later.

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
| ActiveVersionId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the active version of the assessment question.  This is a relationship field.  Relationship Name  ActiveVersion  Relationship Type  Lookup  Refers To  AssessmentQuestionVersion |
| DataType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The data type of the assessment question.  Possible values are:  - `Checkbox` - `Currency` - `Date` - `DateTime` - `Decimal` - `Disclosure` - `EditBlock`—Edit   Block - `Email` - `File` - `Formula` - `Integer` - `Multiselect`—Multi-select - `Radio` - `RadioGroup`—Radio   Group - `Select` - `Telephone` - `Text` - `TextArea`—Text   Area - `TextBlock`—Text   Block - `Time` - `URL` |
| Description | Type  textarea  Properties  Filter, Nillable, Sort  Description  The description for the assessment question. This text is not rendered on the assessment. |
| DeveloperName | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  Required. The unique name of the object in the API. This name can contain only underscores and alphanumeric characters, and must be unique in your org. It must begin with a letter, not include spaces, not end with an underscore, and not contain two consecutive underscores. In managed packages, this field prevents naming conflicts on package installations. |
| DisplayTextCategory | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the category of the display text when the data type is Text Block.  Possible values are:  - `Instruction` - `Legal` - `Security` |
| FormulaResponseDataType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the data type of the question response calculated by a formula.  Possible values are:  - `Boolean` - `Currency` - `Date` - `Decimal` - `Integer` - `Text` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| QuestionCategory | Type  picklist  Properties  Create, Filter, Group, Sort, Update  Description  Required. Stores the question category.  Possible values are:  - `Demographic` - `Financial` |
| QuestionText | Type  textarea  Properties  Filter, Nillable, Sort  Description  Required. The label for the assessment question that appears on the assessment. |
| RelatedQuestionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Identifies the ID of the related question. Used to define a question hierarchy.  This is a relationship field.  Relationship Name  RelatedQuestion  Relationship Type  Lookup  Refers To  AssessmentQuestion |
| ShouldExcludeFromMetadata | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates whether the assessment question record should be excluded from metadata (true) or not (false).  The default value is `false`. |
| ShouldHideInDesigner | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort  Description  Indicates whether the assesment question record should be hidden in OmniScript designer (true) or not (false).  The default value is `false`. |
| SourceSystemName | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Specifies the source system name from where the content of the assessment question was retrieved.  Possible values are:  - `MCG` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentQuestionChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentQuestionFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentQuestionHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssessmentQuestionShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
