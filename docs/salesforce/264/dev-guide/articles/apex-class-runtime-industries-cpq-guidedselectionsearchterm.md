---
page_id: apex-class-runtime-industries-cpq-guidedselectionsearchterm
title: GuidedSelectionSearchTerm Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-guidedselectionsearchterm.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm
fetched_at: 2026-11-25
---

# GuidedSelectionSearchTerm Class

Represents a search term used in guided product selection. Contains the search term text and associated tags for filtering and searching products in Product Discovery.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[GuidedSelectionSearchTerm Constructor](#guidedselectionsearchterm-constructor)**

Learn more about the constructors that are available with the GuidedSelectionSearchTerm class.

- 

**[GuidedSelectionSearchTerm Properties](#guidedselectionsearchterm-properties)**

Contains properties to include search term details for guided product selection.

## GuidedSelectionSearchTerm Constructor

Learn more about the constructors that are available with the GuidedSelectionSearchTerm class.

The `GuidedSelectionSearchTerm` class includes these constructors.

- 

**[GuidedSelectionSearchTerm(apexObj)](#guidedselectionsearchtermapexobj)**

Constructor to create a GuidedSelectionSearchTerm instance from a ConnectApi CPQGuidedSelectionSearchTermOutputRepresentation object.

- 

**[GuidedSelectionSearchTerm()](#guidedselectionsearchterm)**

Default constructor to create an empty GuidedSelectionSearchTerm instance.

### GuidedSelectionSearchTerm(apexObj)

Constructor to create a GuidedSelectionSearchTerm instance from a ConnectApi CPQGuidedSelectionSearchTermOutputRepresentation object.

#### Signature

`public GuidedSelectionSearchTerm(ConnectApi.CPQGuidedSelectionSearchTermOutputRepresentation apexObj)`

#### Parameters

***apexObj***

Type: ConnectApi.CPQGuidedSelectionSearchTermOutputRepresentation

The ConnectApi guided selection search term representation object to convert to GuidedSelectionSearchTerm.

### GuidedSelectionSearchTerm()

Default constructor to create an empty GuidedSelectionSearchTerm instance.

#### Signature

`public GuidedSelectionSearchTerm()`

## GuidedSelectionSearchTerm Properties

Contains properties to include search term details for guided product selection.

The `GuidedSelectionSearchTerm` class includes these properties.

- 

**[tags](#tags)**

Get the list of tags.

- 

**[term](#term)**

Get the term value.

### tags

Get the list of tags.

#### Signature

`public List<String> tags {get; set;}`

#### Property Value

Type: List<String>

### term

Get the term value.

#### Signature

`public String term {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-guidedselectionsearchterm.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
