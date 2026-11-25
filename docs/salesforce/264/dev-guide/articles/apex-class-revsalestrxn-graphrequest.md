---
page_id: apex-class-revsalestrxn-graphrequest
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-graphrequest.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_class_RevSalesTrxn_GraphRequest.htm
fetched_at: 2026-11-25
---

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be ingested. The list of records is specified in a key-value map format that contains field values.

## Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

- 

**[GraphRequest Constructors](#graphrequest-constructors)**

Learn more about the available constructors with the GraphRequest class.

- 

**[GraphRequest Properties](#graphrequest-properties)**

Learn more about the available properties with the GraphRequest class.

## GraphRequest Constructors

Learn more about the available constructors with the GraphRequest class.

The `GraphRequest` class includes these constructors.

- 

**[GraphRequest(graphId, records)](#graphrequestgraphid-records)**

Creates an instance of the GraphRequest class to assign the graph ID and a list of records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the GraphRequest class to assign the graph ID and a list of records to be ingested.

#### Signature

`public GraphRequest(String graphId, List<RevSalesTrxn.RecordWithReferenceRequest> records)`

#### Parameters

***graphId***

Type: String

ID of the graph.

***records***

Type: List<[revsalestrxn.RecordWithReferenceRequest](./apex-class-revsalestrxn-recordwithreferencerequest.md#recordwithreferencerequest-class)>

List of records to be ingested.

## GraphRequest Properties

Learn more about the available properties with the GraphRequest class.

The `GraphRequest` class includes these properties.

- 

**[graphId](#graphid)**

Set the `graphId` property to assign the ID value of the graph.

### graphId

Set the `graphId` property to assign the ID value of the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-graphrequest.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
