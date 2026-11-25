---
page_id: sforce-api-objects-bindingobjectcustomext
title: BindingObjectCustomExt
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bindingobjectcustomext.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_bindingobjectcustomext.htm
fetched_at: 2026-11-25
---

# BindingObjectCustomExt

Represents the external or custom target object that’s bound to the entitlements granted with the sellable product. This object is available in API version 64.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

- 

This object is available in Revenue Management when Rate Management is enabled.

- 

Users with any Rate Management permission set (Admin, Manager, Designtime, Runtime) can view records. Only Admins can create, edit, and delete records.

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when this record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the binding custom object record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner of the product usage grant.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bindingobjectcustomext.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
