---
page_id: sforce-api-objects-pricingprocessexecution
title: PricingProcessExecution
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocessexecution.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_pricingprocessexecution.htm
fetched_at: 2026-11-25
---

# PricingProcessExecution

Represents a record generated during the execution of a discovery or pricing procedure. Multiple procedures may be performed within a single API call, with each recorded in a Pricing API Execution record. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.

Possible values are:

- `BHD`—Bahraini Dinar

- `JPY`—Japanese Yen

- `USD`—U.S. Dollar

The default value is `USD`.

### ExecutionKey

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The unique execution ID generated each time a pricing API runs.

### ExecutionType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of execution defined internally within the pricing API.

Possible values are `Api_Execution`—Api Execution, `Discovery`, `Discovery_Line`—Discovery Line, `Pricing`, or `Pricing_Line`—Pricing Line.

The default value is `Pricing`.

### ExecutionTypeKey

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The unique execution type ID generated internally for procedure executions, such as pricing or discovery procedures.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed.

### Message

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The message generated upon running a pricing process.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The Salesforce ID of the sales representative who owns the pricing procedure resolution.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### Status

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Specifies the status of the execution type.

Possible values are `Failure`, `Partial_Success`—Partial Success, or `Success`.

The default value is `Success`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PricingProcessExecutionFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[PricingProcessExecutionHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[PricingProcessExecutionShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocessexecution.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
