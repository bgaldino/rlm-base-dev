---
page_id: apex_class_commerceorders_RecordWithReferenceRequest.htm
title: RecordWithReferenceRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commerceorders_RecordWithReferenceRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commerceorders.htm
fetched_at: 2026-06-09
---

# RecordWithReferenceRequest Class

Contains constructors and properties to associate a record object with a reference
identifier.

## Namespace

[CommerceOrders](./apex_namespace_commerceorders.htm.md "The CommerceOrders namespace provides classes and methods to place orders with integrated pricing, configuration, and validation.")

## Example

```
CommerceOrders.RecordWithReferenceRequest orderRecordNode = new CommerceOrders.RecordWithReferenceRequest('refOrder', orderRecord);
```

- **[RecordWithReferenceRequest Constructors](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_commerceorders_RecordWithReferenceRequest_constructors)**  
  Learn more about the available constructors with the `RecordWithReferenceRequest` class.
- **[RecordWithReferenceRequest Properties](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_commerceorders_RecordWithReferenceRequest_properties)**  
  Learn more about the available properties with the `RecordWithReferenceRequest` class.

## RecordWithReferenceRequest Constructors

Learn more about the available constructors with the `RecordWithReferenceRequest` class.

The `RecordWithReferenceRequest` class includes these
constructors.

- **[RecordWithReferenceRequest(referenceId, record)](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_commerceorders_RecordWithReferenceRequest_ctor)**  
  Creates an instance of the `RecordWithReferenceRequest` class to associate a record object with a reference identifier by using the `referenceId` and `record` object properties.

### RecordWithReferenceRequest(referenceId, record)

Creates an instance of the `RecordWithReferenceRequest` class to associate a record object with a reference
identifier by using the `referenceId` and `record` object properties.

#### Signature

`public RecordWithReferenceRequest(String referenceId, commerceorders.RecordResource record)`

#### Parameters

referenceId
:   Type: String
:   Reference ID that maps to the subrequest response and can be used to reference the
    response in subsequent subrequests. You can reference the `referenceId` in either the body or URL of a subrequest. Use this syntax to
    include a reference: `@{referenceId.FieldName}`.
    See [referenceId property of a composite subrequest](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_rest.meta/api_rest/resources_composite_graph_composite_subrequest.htm "HTML (New Window)").

record
:   Type: [commerceorders.RecordResource](./apex_class_commerceorders_RecordResource.htm.md#apex_class_commerceorders_RecordResource "Contains constructors and properties to create a record object from field values of an order.")
:   Record object that’s defined using the `RecordResource`
    class.

## RecordWithReferenceRequest Properties

Learn more about the available properties with the `RecordWithReferenceRequest` class.

The `RecordWithReferenceRequest` class includes these
properties.

- **[record](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_commerceorders_RecordWithReferenceRequest_record)**  
  Set the `record` property to specify the record object that’s defined by using the `RecordResource` class.
- **[referenceId](./apex_class_commerceorders_RecordWithReferenceRequest.htm.md#apex_commerceorders_RecordWithReferenceRequest_referenceId)**  
  Set the `referenceId` property to specify the reference ID that maps to the subrequest response. This reference ID can be used to reference the response in subsequent subrequests.

### record

Set the `record` property to specify the record object
that’s defined by using the `RecordResource` class.

#### Signature

`public commerceorders.RecordResource record {get; set;}`

#### Property Value

Type: [commerceorders.RecordResource](./apex_class_commerceorders_RecordResource.htm.md#apex_class_commerceorders_RecordResource "Contains constructors and properties to create a record object from field values of an order.")

### referenceId

Set the `referenceId` property to specify the reference
ID that maps to the subrequest response. This reference ID can be used to reference the response
in subsequent subrequests.

#### Signature

`public String referenceId {get; set;}`

#### Property Value

Type: String
