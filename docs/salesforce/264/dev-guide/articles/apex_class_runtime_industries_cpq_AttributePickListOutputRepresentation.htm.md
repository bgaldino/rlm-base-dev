---
page_id: apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm
title: AttributePickListOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-11-23
---

# AttributePickListOutputRepresentation Class

Stores details of an attribute picklist.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[AttributePickListOutputRepresentation Properties](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_properties)**  
  Contains properties to include details of an attribute picklist.

## AttributePickListOutputRepresentation Properties

Contains properties to include details of an attribute picklist.

The `AttributePickListOutputRepresentation` class includes
these properties.

- **[description](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_ricpq_AttributePickListOR_description)**  
  Get the description of the attribute picklist.
- **[id](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_id)**  
  Get the ID of the attribute picklist.
- **[name](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_name)**  
  Get the name of the attribute picklist.
- **[status](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_status)**  
  Get the status of the attribute picklist.
- **[values](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_values)**  
  Get the values of the attribute picklist.
- **[dataType](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_dataType)**  
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

Type: List<[runtime\_industries\_cpq.AttributePickListValueOutputRepresentation](./apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation "Stores details of an attribute picklist value.")>

### dataType

Get the datatype value.

#### Signature

`public String dataType {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
