---
page_id: sforce_api_objects_valtfrm.htm
title: ValTfrm
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_valtfrm.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-06-09
---

# ValTfrm

Represents mappings between fields and attributes. Enrichment rules
are part of a decomposition rule, and are used to propagate data to fulfillment order
lines. This object is available in API version 61.0 and later.

![Important](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note_important.png&folder=revenue_lifecycle_management_dev_guide)

#### Important

Where
possible, we changed noninclusive terms to align with our company value of Equality. We
maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| InputDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date of value entry. |
| InputDatetime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The time of value entry. |
| InputNumber | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The value of input number. |
| InputPicklistValueId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The identifier of the input list of values.  This field is a relationship field.  Relationship Name  InputPicklistValue  Refers To  AttributePicklistValue |
| InputString | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value of input text. |
| IsInputBoolean | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates if a value was entered (`true`) or not (`false`).  The default value is `false`. |
| IsOutputBoolean | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates if there was an output value (`true`) or not (`false`).  The default value is `false`. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the related transformation group. |
| OutputDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The date of matched output. |
| OutputDatetime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The time of matched output. |
| OutputNumber | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The value of output number. |
| OutputPicklistValueId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The identifier of the output list of values.  This field is a relationship field.  Relationship Name  OutputPicklistValue  Refers To  AttributePicklistValue |
| OutputString | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The value of output text. |
| ValueTransformGroupId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The identifier of the related transformation group.  This field is a relationship field.  Relationship Name  ValueTransformGroup  Relationship Type  Master-detail  Refers To  ValTfrmGrp (the master object) |
