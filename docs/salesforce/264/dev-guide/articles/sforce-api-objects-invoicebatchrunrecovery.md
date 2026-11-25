---
page_id: sforce-api-objects-invoicebatchrunrecovery
title: InvoiceBatchRunRecovery
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoicebatchrunrecovery.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_invoicebatchrunrecovery.htm
fetched_at: 2026-11-25
---

# InvoiceBatchRunRecovery

Represents information about the recovery procedure of an invoice batch run. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`

## Special Access Rules

You need the Billing Admin permission set to access this object.

## Fields

### BatchJobId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The batch management job that’s used to track the progress of the invoice batch run.

This field is a relationship field.

- **Relationship Name**: BatchJob

- **Refers To**: BatchJob

### Comments

- **Type**: textarea

- **Properties**: Filter, Nillable, Sort, Update

- **Description**: Additional notes or comments for the invoice batch run recovery.

### CompletionTime

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the invoice batch run recovery finished processing.

### InvoiceBatchRunId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Required. A unique identifier of the invoice batch run that’s related to this recovery run.

This field is a relationship field.

- **Relationship Name**: InvoiceBatchRun

- **Relationship Type**: Master-detail

- **Refers To**: InvoiceBatchRun (the master object)

### InvoiceBatchRunRecoveryNumber

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. A unique identifier of the recovery process for the invoice batch run.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last accessed an invoice batch run recovery record indirectly, for example, through a list view or related record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp when the current user last viewed an invoice batch run recovery record. If this value is null, it’s possible that the user only accessed the invoice batch run recovery record or a related list view (`LastReferencedDate`), but not viewed the invoice batch run recovery record itself.

### StartTime

- **Type**: dateTime

- **Properties**: Filter, Sort

- **Description**: Required. The timestamp when the invoice batch run recovery started processing.

### Status

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Restricted picklist, Sort

- **Description**: Required. The final state of the recovery process for the invoice batch runs.

Valid values are `Completed`, `CompletedWithErrors`, `Failed`, or `Started`.

The default value is `Started`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-invoicebatchrunrecovery.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
