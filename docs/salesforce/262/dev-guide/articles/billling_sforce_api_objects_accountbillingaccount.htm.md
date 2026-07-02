---
page_id: billling_sforce_api_objects_accountbillingaccount.htm
title: Billing Fields on AccountBillingAccount
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billling_sforce_api_objects_accountbillingaccount.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-06-09
---

# Billing Fields on AccountBillingAccount

Standard fields extend the AccountBillingAccount object for use in
Billing to represent information about default billing accounts. This object is
available in API version 63.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`,
`getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need the Billing Admin permission set, Billing Operations User permission set, or
Billing Customer Service User permission set access to this object.

## Fields

| Field | Details |
| --- | --- |
| IsDefaultBillingAccount | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the account is the default billing account (`true`) or not (`false`).  The default value is `false`. |

#### See Also

- [*Energy and Utilities Cloud Developer Guide*: AccountBillingAccount](https://developer.salesforce.com/docs/atlas.en-us.262.0.eu_developer_guide.meta/eu_developer_guide/sforce_api_objects_accountbillingaccount.htm "Energy and Utilities Cloud Developer Guide: AccountBillingAccount - HTML (New Window)")
