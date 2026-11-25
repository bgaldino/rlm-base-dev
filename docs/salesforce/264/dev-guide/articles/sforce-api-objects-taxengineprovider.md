---
page_id: sforce-api-objects-taxengineprovider
title: TaxEngineProvider
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-taxengineprovider.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-std-objects-parent
legacy_page_id: sforce_api_objects_taxengineprovider.htm
fetched_at: 2026-11-25
---

# TaxEngineProvider

Represents general information about a service that manages a tax engine. Tax engine providers have a one-to-many relationship with tax engines, where the tax engine record represents a specific configuration of a tax engine that can be assigned to multiple order items. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Special Access Rules

You need the Tax Admin permission set to access this object.

## Fields

### ApexAdapterId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the Apex adapter used by the tax provider. This field is unique within your organization.

This field is a relationship field.

- **Relationship Name**: ApexAdapter

- **Refers To**: ApexClass

### CustomMetadataTypeApiName

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The API name of the custom metadata type that defines field mappings for tax callout requests and responses. The custom metadata type name is referenced by the tax engine provider to identify the metadata configuration to use. Available in API version 65.0 and later.

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Additional details about the tax engine provider.

### DeveloperName

- **Type**: string

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: Required. The API name for the tax engine provider record.

### Language

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The language used by the tax engine provider. Values appear based on their language codes in Salesforce, such as `da` for Danish or `th` for Thai.

### MasterLabel

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The label used for the tax engine’s API in Salesforce.

### NamespacePrefix

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The Apex namespace prefix of the API used for the tax engine.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-taxengineprovider.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
