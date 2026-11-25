---
page_id: billing-sforce-api-objects-assetactionsource
title: Billing Fields on AssetActionSource
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-assetactionsource.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-extended-standard-object-fields
legacy_page_id: billing_sforce_api_objects_assetactionsource.htm
fetched_at: 2026-11-25
---

# Billing Fields on AssetActionSource

Standard fields extend the AssetActionSource object for use in Billing to represent information about the billing term.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`

## Special Access Rules

You need the Revenue Cloud Billing license, and the Billing Admin permission set or the Billing Operations User permission set to access this object.

## Fields

### BillingTerm

**Type:** int

**Properties:** Defaulted on create, Filter, Group, Nillable, Sort

**Description:** The number of billing frequency units to combine into a billing period item. Available in API version 68.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-sforce-api-objects-assetactionsource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
