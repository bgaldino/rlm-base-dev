---
page_id: sforce_api_objects_legalentity.htm
title: LegalEntity
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_legalentity.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-06-09
---

# LegalEntity

Represents the way an organization is structured. An organization can
be a single legal entity or it can comprise more than one legal entity. This object is
available in API version 62.0 and later.

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

## Special Access Rules

You need the Accounts Receivables Admin permission set to access this object.

## Fields

| Field | Details |
| --- | --- |
| CompanyName | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the company that this legal entity represents. |
| Description | Type  textarea  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Additional details about the legal entity. |
| EmailTemplateId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  A template that's used to send emails for the legal entity. This field is available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  EmailTemplate  Refers To  EmailTemplate |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed a legal entity indirectly, for example, through a list view or related record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed a legal entity. If this value is null, it’s possible that the user only accessed the legal entity or a related list view (LastReferencedDate), but not viewed the legal entity itself. |
| LegalEntityAddress | Type  address  Properties  Filter, Nillable  Description  The address of the company that this legal entity represents. See [Address Compound Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/compound_fields_address.htm) for details on compound address fields. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the legal entity. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Required. The ID of the record owner.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ShouldAttachInvoiceDocToEmail | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether to attach the invoice PDF document to the email that's sent for the legal entity (`true`) or not (`false`). This field is available in API version 65.0 and later.  The default value is `false`. |
| Status | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The status of the legal entity.  Valid values are:  - `Active` - `Inactive` |
