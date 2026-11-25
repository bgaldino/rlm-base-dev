---
page_id: billing-sforce-api-objects-expressionset
title: Billing Fields on ExpressionSet
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-expressionset.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-extended-standard-object-fields
legacy_page_id: billing_sforce_api_objects_expressionset.htm
fetched_at: 2026-11-25
---

# Billing Fields on ExpressionSet

Standard fields extend the ExpressionSet object for use in Billing. These fields represent information about an expression set that performs a series of calculations by using lookups and user-defined variables and constants to calculate taxes. This object is available in API version 66.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### UsageType

**Type:** picklist

**Properties:** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

**Description:** Required. The Revenue Standard Tax Calculation value that’s using the expression set to calculate taxes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-expressionset.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
