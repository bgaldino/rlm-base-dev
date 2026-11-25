---
page_id: apex-class-runtime-industries-cpq-guidedselectionsearchtermlist
title: GuidedSelectionSearchTermList Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-guidedselectionsearchtermlist.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm
fetched_at: 2026-11-25
---

# GuidedSelectionSearchTermList Class

Contains a list of search terms used in guided product selection. This class is used to pass multiple search terms for filtering and searching products in Product Discovery.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[GuidedSelectionSearchTermList Constructor](#guidedselectionsearchtermlist-constructor)**

Learn more about the constructor that’s available with the GuidedSelectionSearchTermList class.

- 

**[GuidedSelectionSearchTermList Properties](#guidedselectionsearchtermlist-properties)**

Contains properties to include a list of search terms for guided product selection.

## GuidedSelectionSearchTermList Constructor

Learn more about the constructor that’s available with the GuidedSelectionSearchTermList class.

The `GuidedSelectionSearchTermList` class includes this constructor.

- 

**[GuidedSelectionSearchTermList()](#guidedselectionsearchtermlist)**

Default constructor to create an empty GuidedSelectionSearchTermList instance.

### GuidedSelectionSearchTermList()

Default constructor to create an empty GuidedSelectionSearchTermList instance.

#### Signature

`public GuidedSelectionSearchTermList()`

## GuidedSelectionSearchTermList Properties

Contains properties to include a list of search terms for guided product selection.

The `GuidedSelectionSearchTermList` class includes these properties.

- 

**[searchTerms](#searchterms)**

Get the list of searchterm.

### searchTerms

Get the list of searchterm.

#### Signature

`public List<runtime_industries_cpq.GuidedSelectionSearchTerm> searchTerms {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.GuidedSelectionSearchTerm](./apex-class-runtime-industries-cpq-guidedselectionsearchterm.md#guidedselectionsearchterm-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-guidedselectionsearchtermlist.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
