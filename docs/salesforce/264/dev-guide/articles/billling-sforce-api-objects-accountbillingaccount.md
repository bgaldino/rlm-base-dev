---
page_id: billling-sforce-api-objects-accountbillingaccount
title: Billing Fields on AccountBillingAccount
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billling-sforce-api-objects-accountbillingaccount.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-extended-standard-object-fields
legacy_page_id: billling_sforce_api_objects_accountbillingaccount.htm
fetched_at: 2026-11-25
---

# Billing Fields on AccountBillingAccount

Standard fields extend the AccountBillingAccount object for use in Billing to represent information about default billing accounts. This object is available in API version 63.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need the Billing Admin permission set, Billing Operations User permission set, or Billing Customer Service User permission set access to this object.

**See Also**

- [*Energy and Utilities Cloud Developer Guide*: AccountBillingAccount](https://developer.salesforce.com/docs/atlas.en-us.eu_developer_guide.meta/eu_developer_guide/sforce_api_objects_accountbillingaccount.htm)

## Fields

### IsDefaultBillingAccount

**Type:** boolean

**Properties:** Defaulted on create, Filter, Group, Sort

**Description:** Indicates whether the account is the default billing account ( `true`) or not ( `false`).

The default value is `false`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billling-sforce-api-objects-accountbillingaccount.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
