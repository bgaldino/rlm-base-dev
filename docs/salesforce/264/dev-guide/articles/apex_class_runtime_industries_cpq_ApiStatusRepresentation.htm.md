---
page_id: apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm
title: ApiStatusRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-11-23
---

# ApiStatusRepresentation Class

Stores details of the API request such as execution messages, status code, and status
message.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ApiStatusRepresentation Properties](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md#apex_runtime_industries_cpq_ApiStatusRepresentation_properties)**  
  Contains properties to include the API response details.

## ApiStatusRepresentation Properties

Contains properties to include the API response details.

The `ApiStatusRepresentation` class includes these
properties.

- **[messages](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md#apex_runtime_industries_cpq_ApiStatusRepresentation_messages)**  
  Get the status messages of the API execution.
- **[statusCode](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md#apex_runtime_industries_cpq_ApiStatusRepresentation_statusCode)**  
  Get the status code of the API execution.
- **[statusMessage](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md#apex_runtime_industries_cpq_ApiStatusRepresentation_statusMessage)**  
  Get the display label for the API status.

### messages

Get the status messages of the API execution.

#### Signature

`public List<ConnectApi.CpqMessageOutputRepresentation> messages {get; set;}`

#### Property Value

Type: List<ConnectApi.CpqMessageOutputRepresentation>

### statusCode

Get the status code of the API execution.

#### Signature

`public String statusCode {get; set;}`

#### Property Value

Type: String

### statusMessage

Get the display label for the API status.

#### Signature

`public String statusMessage {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
