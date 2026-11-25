---
page_id: apex-class-runtime-industries-cpq-catalogoutputrepresentation
title: CatalogOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-catalogoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm
fetched_at: 2026-11-25
---

# CatalogOutputRepresentation Class

Contains properties to store details of a catalog definition.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[CatalogOutputRepresentation Properties](#catalogoutputrepresentation-properties)**

Contains properties to include details of a catalog definition.

## CatalogOutputRepresentation Properties

Contains properties to include details of a catalog definition.

The `CatalogOutputRepresentation` class includes these properties.

- 

**[catalogCode](#catalogcode)**

Get the unique ID associated with the catalog.

- 

**[catalogType](#catalogtype)**

Get the category of an entry in the catalog, which is customizable. For example, catalog types, such as sellable products, services, parts, technical services, or technical resources.

- 

**[customFields](#customfields)**

Get details of the custom fields associated with a catalog.

- 

**[description](#description)**

Get the description of the catalog.

- 

**[effectiveEndDate](#effectiveenddate)**

Get the date and time from when the catalog isn’t available to the end users.

- 

**[effectiveStartDate](#effectivestartdate)**

Get the date and time from when the catalog is available to the end users.

- 

**[id](#id)**

Get the ID of the catalog.

- 

**[name](#name)**

Get the name of the catalog.

- 

**[numberOfCategories](#numberofcategories)**

Get the number of categories in the catalog.

- 

**[status](#status)**

Get the status of the catalog.

### catalogCode

Get the unique ID associated with the catalog.

#### Signature

`public String catalogCode {get; set;}`

#### Property Value

Type: String

### catalogType

Get the category of an entry in the catalog, which is customizable. For example, catalog types, such as sellable products, services, parts, technical services, or technical resources.

#### Signature

`public String catalogType {get; set;}`

#### Property Value

Type: String

### customFields

Get details of the custom fields associated with a catalog.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> customFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### description

Get the description of the catalog.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### effectiveEndDate

Get the date and time from when the catalog isn’t available to the end users.

#### Signature

`public String effectiveEndDate {get; set;}`

#### Property Value

Type: String

### effectiveStartDate

Get the date and time from when the catalog is available to the end users.

#### Signature

`public String effectiveStartDate {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the catalog.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the catalog.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### numberOfCategories

Get the number of categories in the catalog.

#### Signature

`public Integer numberOfCategories {get; set;}`

#### Property Value

Type: Integer

### status

Get the status of the catalog.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-catalogoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
