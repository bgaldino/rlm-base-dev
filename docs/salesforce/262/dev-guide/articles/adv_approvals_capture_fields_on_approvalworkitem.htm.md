---
page_id: adv_approvals_capture_fields_on_approvalworkitem.htm
title: Advanced Approvals Fields on Approval Work Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/adv_approvals_capture_fields_on_approvalworkitem.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approval_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Advanced Approvals Fields on Approval Work Item

Standard and custom fields extend the standard Approval Work Item
object for use in Advanced Approvals.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `update()`

## Special Access Rules

This object is available in Enterprise, Performance, Unlimited, and Developer Editions
for users with access to the Approval Submission object.

## Fields

| Field | Details |
| --- | --- |
| ApprovalChainName | Type  string  Properties  Filter, Group, Nillable, Sort, Update  Description  The name of the related approval chain. This field is populated when there are multiple approval chains that are run in parallel. This field is only available with Advanced Approvals enabled. |
| CurrencyIsoCode | Type  picklist  Properties  Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Available only for organizations with the multicurrency feature enabled. Contains the ISO code for any currency allowed by the organization.  Valid values are:  - `AED`—UAE   Dirham - `AUD`—Australian   Dollar - `BRL`—Brazilian   Real - `CAD`—Canadian   Dollar - `EUR`—Euro - `GBP`—British   Pound - `INR`—Indian   Rupee - `JPY`—Japanese   Yen - `SEK`—Swedish   Krona - `USD`—U.S.   Dollar  The default value is `USD`. |
| IsAutoReviewed | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the approval work item is eligible for smart approval (true) or not (false).  The default value is `false`. |
| IsEligibleForSmartApproval | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the approval work item is eligible for smart approval (`true`) or not (`false`).  The default value is `false`. |
| SmartApprovalBasisWorkItemId | Type  reference  Properties  Filter, Group, Nillable, Sort, Update  Description  The previous approval work item used as a reference for the auto-approval evaluation.  This field is a relationship field.  Relationship Name  SmartApprovalBasisWorkItem  Refers To  ApprovalWorkItem |
