---
page_id: apex_class_RevSalesTrxn_GraphRequest.htm
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_GraphRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be
ingested. The list of records is specified in a key-value map format that contains field
values.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md "Create a sales transaction, such as a quote or an order, with integrated pricing and configuration. Additionally, update an order or a quote, and insert and delete order or quote line items to calculate the estimated tax.")

- **[GraphRequest Constructors](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_constructors)**  
  Learn more about the available constructors with the GraphRequest class.
- **[GraphRequest Properties](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_properties)**  
  Learn more about the available properties with the GraphRequest class.

## GraphRequest Constructors

Learn more about the available constructors with the GraphRequest class.

The `GraphRequest` class includes these constructors.

- **[GraphRequest(graphId, records)](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_ctor)**  
  Creates an instance of the GraphRequest class to assign the graph ID and a list of records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the GraphRequest class to assign the graph ID and a list of
records to be ingested.

#### Signature

`public GraphRequest(String graphId,
List<RevSalesTrxn.RecordWithReferenceRequest> records)`

#### Parameters

graphId
:   Type: String
:   ID of the graph.

records
:   Type: List<[revsalestrxn.RecordWithReferenceRequest](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_class_RevSalesTrxn_RecordWithReferenceRequest "Contains constructors and properties to associate a record object with a reference identifier.")>
:   List of records to be ingested.

## GraphRequest Properties

Learn more about the available properties with the GraphRequest class.

The `GraphRequest` class includes these properties.

- **[graphId](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_graphId)**  
  Set the `graphId` property to assign the ID value of the graph.

### graphId

Set the `graphId` property to assign the ID value of
the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String
