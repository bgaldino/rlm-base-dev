---
page_id: apex-class-revsalestrxn-recordwithreferencerequest
title: RecordWithReferenceRequest Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-recordwithreferencerequest.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: apex-namespace-revsalestrxn
legacy_page_id: apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm
fetched_at: 2026-11-25
---

# RecordWithReferenceRequest Class

Contains constructors and properties to associate a record object with a reference identifier.

## Namespace

[RevSalesTrxn](./apex-namespace-revsalestrxn.md)

## Example

```
RevSalesTrxn.RecordWithReferenceRequest quoteLineItemRecords = new RevSalesTrxn.RecordWithReferenceRequest('refQuoteItem',quoteLineItemRecord);
```

- 

**[RecordWithReferenceRequest Constructors](#recordwithreferencerequest-constructors)**

Learn more about the available constructors with the RecordWithReferenceRequest class.

- 

**[RecordWithReferenceRequest Properties](#recordwithreferencerequest-properties)**

Learn more about the available properties with the RecordWithReferenceRequest class.

## RecordWithReferenceRequest Constructors

Learn more about the available constructors with the RecordWithReferenceRequest class.

The `RecordWithReferenceRequest` class includes these constructors.

- 

**[RecordWithReferenceRequest(referenceId, record)](#recordwithreferencerequestreferenceid-record)**

Creates an instance of the RecordWithReferenceRequest class to associate a record object with a reference identifier by using the referenceId and record object properties.

### RecordWithReferenceRequest(referenceId, record)

Creates an instance of the RecordWithReferenceRequest class to associate a record object with a reference identifier by using the referenceId and record object properties.

#### Signature

`public RecordWithReferenceRequest(String referenceId, RevSalesTrxn.RecordResource record)`

#### Parameters

***referenceId***

Type: String

Reference ID that maps to the subrequest response and can be used to reference the response in subsequent subrequests. You can reference the referenceId in either the body or URL of a subrequest. Use this syntax to include a reference: @{referenceId.FieldName}. See [referenceId property of a composite subrequest](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_composite_graph_composite_subrequest.htm).

***record***

Type: [RevSalesTrxn.RecordResource](./apex-class-revsalestrxn-recordresource.md#recordresource-class)

Record object that’s defined using the `RecordResource` class.

## RecordWithReferenceRequest Properties

Learn more about the available properties with the RecordWithReferenceRequest class.

The `RecordWithReferenceRequest` class has these properties.

- 

**[record](#record)**

Set the record property to specify the record object that’s defined by using the RecordResource class.

- 

**[referenceId](#referenceid)**

Set the referenceId property to specify the reference ID that maps to the subrequest response. This reference ID can be used to reference the response in subsequent subrequests.

### record

Set the record property to specify the record object that’s defined by using the RecordResource class.

#### Signature

`public RevSalesTrxn.RecordResource record {get; set;}`

#### Property Value

Type: [RevSalesTrxn.RecordResource](./apex-class-revsalestrxn-recordresource.md#recordresource-class)

### referenceId

Set the referenceId property to specify the reference ID that maps to the subrequest response. This reference ID can be used to reference the response in subsequent subrequests.

#### Signature

`public String referenceId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-revsalestrxn-recordwithreferencerequest.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
