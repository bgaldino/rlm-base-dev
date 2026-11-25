---
page_id: sforce-api-associated-objects-share
title: StandardObjectName Share
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-associated-objects-share.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Revenue Management Associated Objects
parent_page: sforce-api-associated-objects-list
legacy_page_id: sforce_api_associated_objects_share.htm
fetched_at: 2026-11-25
---

# *StandardObjectName* Share

*StandardObjectName* Share is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object.

The object name is variable and uses *StandardObjectName* Share syntax. For example, AccountBrandShare is a sharing entry on an account brand. For specific version information, see the standard object documentation.

You can only create, edit, and delete sharing entries for standard objects whose `RowCause` field is set to `Manual`. Sharing entries for standard objects with different `RowCause` values are created as a result of your Salesforce org’s sharing configuration and are read-only. For some sharing mechanisms, such as sharing sets, sharing entries aren’t stored at all.

**Note:**

While Salesforce currently maintains read-only sharing entries for multiple sharing mechanisms, it’s possible that we’ll stop storing certain share records to improve performance. As a best practice, don’t create customizations that rely on the availability of these sharing entries. Any changes to sharing behavior will be communicated before they occur.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

For specific special access rules, if any, see the documentation for the standard object. For example, for AccountBrandShare, see the special access rules for AccountBrand.

## Fields

### AccessLevel

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The level of access allowed. Values are `All` (owner), `Edit` (read/write), or `Read` (read only)

### ParentId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: ID of the parent record.

### RowCause

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Reason that the sharing entry exists.

### UserOrGroupId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: ID of the user or group that has been given access to the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-associated-objects-share.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
