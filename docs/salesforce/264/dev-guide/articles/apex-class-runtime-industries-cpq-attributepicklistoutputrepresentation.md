---
page_id: apex-class-runtime-industries-cpq-attributepicklistoutputrepresentation
title: AttributePickListOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-attributepicklistoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm
fetched_at: 2026-11-25
---

# AttributePickListOutputRepresentation Class

Stores details of an attribute picklist.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[AttributePickListOutputRepresentation Properties](#attributepicklistoutputrepresentation-properties)**

Contains properties to include details of an attribute picklist.

## AttributePickListOutputRepresentation Properties

Contains properties to include details of an attribute picklist.

The `AttributePickListOutputRepresentation` class includes these properties.

- 

**[description](#description)**

Get the description of the attribute picklist.

- 

**[id](#id)**

Get the ID of the attribute picklist.

- 

**[name](#name)**

Get the name of the attribute picklist.

- 

**[status](#status)**

Get the status of the attribute picklist.

- 

**[values](#values)**

Get the values of the attribute picklist.

- 

**[dataType](#datatype)**

Get the datatype value.

### description

Get the description of the attribute picklist.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the attribute picklist.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the attribute picklist.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### status

Get the status of the attribute picklist.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### values

Get the values of the attribute picklist.

#### Signature

`public List<runtime_industries_cpq.AttributePickListValueOutputRepresentation> values {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.AttributePickListValueOutputRepresentation](./apex-class-runtime-industries-cpq-attributepicklistvalueoutputrepresentation.md#attributepicklistvalueoutputrepresentation-class)>

### dataType

Get the datatype value.

#### Signature

`public String dataType {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-attributepicklistoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
