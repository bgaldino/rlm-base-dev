---
page_id: apex-class-runtime-industries-cpq-apistatusrepresentation
title: ApiStatusRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-apistatusrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm
fetched_at: 2026-11-25
---

# ApiStatusRepresentation Class

Stores details of the API request such as execution messages, status code, and status message.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ApiStatusRepresentation Properties](#apistatusrepresentation-properties)**

Contains properties to include the API response details.

## ApiStatusRepresentation Properties

Contains properties to include the API response details.

The `ApiStatusRepresentation` class includes these properties.

- 

**[messages](#messages)**

Get the status messages of the API execution.

- 

**[statusCode](#statuscode)**

Get the status code of the API execution.

- 

**[statusMessage](#statusmessage)**

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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-apistatusrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
