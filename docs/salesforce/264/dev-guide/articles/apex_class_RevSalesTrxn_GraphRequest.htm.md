---
page_id: apex_class_RevSalesTrxn_GraphRequest.htm
title: GraphRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_RevSalesTrxn_GraphRequest.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# GraphRequest Class

Contains constructors and properties to set the graph ID and a list of records to be
    ingested. The list of records is specified in a key-value map format that contains field
    values.

## Namespace

[RevSalesTrxn](./apex_namespace_RevSalesTrxn.htm.md)

- 
**[GraphRequest Constructors](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_constructors)**  

Learn more about the available constructors with the GraphRequest class.

- 
**[GraphRequest Properties](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_properties)**  

Learn more about the available properties with the GraphRequest class.

  

## GraphRequest Constructors

  
  
  
Learn more about the available constructors with the GraphRequest class.

    
      

The `GraphRequest` class includes these constructors.

    

    
  

- 
**[GraphRequest(graphId, records)](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_ctor)**  

Creates an instance of the GraphRequest class to assign the graph ID and a list of     records to be ingested.

### GraphRequest(graphId, records)

Creates an instance of the GraphRequest class to assign the graph ID and a list of
    records to be ingested.

#### Signature

`public GraphRequest(String graphId,
          List<RevSalesTrxn.RecordWithReferenceRequest> records)`

#### Parameters

**graphId**

: Type: String

: ID of the graph.

**records**

: Type: List<[revsalestrxn.RecordWithReferenceRequest](./apex_class_RevSalesTrxn_RecordWithReferenceRequest.htm.md#apex_class_RevSalesTrxn_RecordWithReferenceRequest)>

          
: List of records to be ingested.

## GraphRequest Properties

  
Learn more about the available properties with the GraphRequest class.

The `GraphRequest` class includes these properties.

- 
**[graphId](./apex_class_RevSalesTrxn_GraphRequest.htm.md#apex_RevSalesTrxn_GraphRequest_graphId)**  

Set the `graphId` property to assign the ID value of     the graph.

### graphId

  
Set the `graphId` property to assign the ID value of
    the graph.

#### Signature

`public String graphId {get; set;}`

#### Property Value

Type: String
