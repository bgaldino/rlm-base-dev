---
page_id: sforce-api-objects-quotelinegroup
title: QuoteLineGroup
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotelinegroup.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_quotelinegroup.htm
fetched_at: 2026-11-25
---

# QuoteLineGroup

Stores the group information for line items in a quote. It also stores the aggregated line field information (subtotal). It contains a parent-child relationship to quote. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The description of the group.

### Discount

- **Type**: percent

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The optional discount percentage, specified by the sales representative at the group level.

### DiscountAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The optional discount amount, specified by the sales representative at the group level.

### EndDate

- **Type**: date

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The end date of the group ramp segment.

### IsRamped

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates whether the group is a group ramp segment, which is a period in a group ramp deal with specific prices and volume. The default value is `false`.

### Margin

- **Type**: percent

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The optional margin percentage, specified by the sales representative at the group level.

### MarginAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The optional margin amount, specified by the sales representative at the group level. This amount can also be considered as the summary margin amount calculated by subtracting the total cost from the summary subtotal.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the group.

### ParentQuoteLineGroupId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the parent group for a nested quote line group. This field is a relationship field.

- **Relationship Name**: ParentQuoteLineGroup

- **Refers To**: QuoteLineGroup

### QuoteId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the related quote. This field is a relationship field.

- **Relationship Name**: Quote

- **Relationship Type**: Master-detail

- **Refers To**: Quote (the master object)

### SegmentType

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The duration type of the segment. Possible values are `Custom` or `Yearly`.

### SortOrder

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

### StartDate

- **Type**: date

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The start date of the group ramp segment.

### SummarySubtotal

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The aggregated subtotal amount of nested group lines.

### SummaryTotalAmount

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The aggregated total amount of nested group lines before any discounts are applied.

### TotalAdjustment

- **Type**: percent

- **Properties**: Filter, Nillable, Sort

- **Description**: The total discount percentage applied at the group level. This percentage is calculated by using the formula: (Summary Total Amount - Summary Subtotal) / Summary Total Amount.

### TotalAdjustmentAmount

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The total discount amount at the group level. This amount is calculated by subtracting the summary subtotal from the summary total amount.

### TotalCost

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The aggregated total cost of nested group lines.

### TotalMargin

- **Type**: percent

- **Properties**: Filter, Nillable, Sort

- **Description**: The summary margin percentage at the line item level. This percentage is calculated by using the formula: (Summary Subtotal - Total Cost) / Summary Subtotal.

### TotalMarginAmount

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The summary margin amount calculated at the group level.

### Type

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The type of quote line group. Possible values are `AssetDowngrade`, `AssetSwap`, `AssetUpgrade`, `CPQQuoteGroup`—CPQ Line Grouping, or `RampScheduleGroup`. The default value is `CPQQuoteGroup`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotelinegroup.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
