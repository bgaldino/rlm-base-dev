---
page_id: apex-class-runtime-industries-cpq-additionalcontextdata
title: AdditionalContextData Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-additionalcontextdata.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_AdditionalContextData.htm
fetched_at: 2026-11-25
---

# AdditionalContextData Class

Contains properties to include a list of additional context data nodes. These nodes are used along with the context definition nodes for data hydration.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[AdditionalContextData Properties](#additionalcontextdata-properties)**

Set the AdditionalContextData class property to specify a list of additional nodes for data hydration.

## AdditionalContextData Properties

Set the AdditionalContextData class property to specify a list of additional nodes for data hydration.

The `AdditionalContextData` class includes this property.

- 

**[additionalContextData](#additionalcontextdata)**

Include a list of additional nodes that are used along with the context definition nodes for data hydration. The maximum number of supported nodes is 10.

### additionalContextData

Include a list of additional nodes that are used along with the context definition nodes for data hydration. The maximum number of supported nodes is 10.

#### Signature

`public List<runtime_industries_cpq.ContextDataInput> additionalContextData {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ContextDataInput](./apex-class-runtime-industries-cpq-contextdatainput.md#contextdatainput-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-additionalcontextdata.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
