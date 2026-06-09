---
page_id: sforce_api_objects_taxengineinteractionlog.htm
title: TaxEngineInteractionLog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_taxengineinteractionlog.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# TaxEngineInteractionLog

Represents a record of a communication with an external tax engine following
a tax calculation request.  This object is available in API version 62.0 and later.

## Supported Calls

`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`

## Special Access Rules

You need the Tax Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| Description | Type  textarea  Properties  Filter, Nillable, Sort  Description  Additional details about the tax engine interaction log. |
| DocumentCode | Type  string  Properties  Filter, Group, Nillable, Sort  Description  Document code of the transaction for which the tax engine integration log was captured. |
| EffectiveDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The date that the tax engine request takes effect. This date is available for reference and bookkeeping only and doesn’t have any impact on tax calculation. |
| InteractionHttpStatusCode | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The HHTP result code of the external callout made to a third-party tax engine provider. Refer to your third-party tax engine provider’s documentation for details about the specific codes returned. |
| InteractionType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  Indicates the type of request made to the tax engine.  Valid value is:  - `CalculateTax` |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a tax engine interaction log record indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a tax engine interaction log record. If this value is null, it’s possible that the user only accessed the tax engine interaction log record or a related list view (`LastReferencedDate`), but not viewed the tax engine interaction log record itself. |
| ReferenceEntity | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The record on which tax was calculated. |
| RequestBody | Type  base64  Properties  Nillable  Description  The content of the tax calculation API request. |
| RequestContentType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of data passed in the request. For example, `application/html` or `text/csv`. |
| RequestLength | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The character length of text within the request body. |
| RequestName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the request. |
| RequestTaxTransactionType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of tax transaction request sent to the tax engine provider. Available in API version 65.0 and later.  Valid values are:  - `Credit` - `Debit` - `VoidOrCredit` - `VoidOrDebit` |
| ResponseContentType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The method used to deliver the tax calculation API response, such as `application/html` or `text/vnd.salesforce.quip-template`. |
| ResponseLength | Type  int  Properties  Filter, Group, Nillable, Sort  Description  The character length of text within the response body. |
| ResponseName | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The name of the response from the tax engine. |
| ResponseTaxTransactionType | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The type of tax transaction response received from the tax engine provider. Available in API version 65.0 and later.  Valid values are:  - `Credit` - `Debit` - `Void` |
| ResultCode | Type  picklist  Properties  Filter, Group, Nillable, Restricted picklist, Sort  Description  The code describing the result of the request.  Valid values are:  - `AdapterException` - `ReferenceDocumentCodeMissing` - `Success` - `TaxEngineError` - `ValidationError` |
| TaxEngineId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  The ID of the tax engine used in the tax calculation process.  This field is a relationship field.  Relationship Name  TaxEngine  Refers To  TaxEngine |
| TaxEngineInteractionLogNumber | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  A system-generated number for a log entry. |
