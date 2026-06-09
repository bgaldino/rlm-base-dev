---
page_id: quote_and_order_capture_fields_on_order_item_group.htm
title: Transaction Management Fields on Order Item Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_item_group.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Transaction Management Fields on Order Item Group

Standard and custom fields extend the standard Order Item Group object
for use in Transaction Management.

## Special Access Rules

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Item Group](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_orderitemgroup.htm) for fields on the Salesforce platform
object.

## Fields

| Field | Details |
| --- | --- |
| Discount | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The optional discount percentage, specified by the sales representative at the group level. Available in API version 65.0 and later. |
| DiscountAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The optional discount amount, specified by the sales representative at the group level. Available in API version 65.0 and later. |
| EndDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The end date of the group.  If the IsRamped field is set to `true`, Transaction Management sets this date as the end date of all the line items in the group that have the Term-Defined product selling model.  Available in API version 65.0 and later. |
| IsRamped | Type  boolean  Properties  Create, Defaulted on Create, Filter, Group, Sort, Update  Description  Indicates whether the group is a group ramp segment, which is a period in a group ramp schedule with specific products, quantities, and discounts.  You can use this field from Revenue Cloud only when the **Ramp Deals for Groups in Quotes and Orders** setting is turned on.  The default value is `false`.  Available in API version 65.0 and later. |
| Margin | Type  percent  Properties  Create, Filter, Nillable, Sort, Update  Description  The optional margin percentage, specified by the sales representative at the group level. Available in API version 65.0 and later. |
| MarginAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The optional margin amount, specified by the sales representative at the group level. This amount can also be considered as the summary margin amount calculated by subtracting the total cost from the summary subtotal. Available in API version 65.0 and later. |
| ParentOrderItemGroupId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the parent group for a nested quote line group. Available in API version 65.0 and later.  This field is a relationship field.  Relationship Name  ParentOrderItemGroup  Refers To  OrderItemGroup |
| SegmentType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The duration type of the segment. You can use this field from Revenue Cloud only when the **Ramp Deals for Groups in Quotes and Orders** setting is turned on.  Valid values are:  - `Custom`—Available in API version 65.0 and   later. - `Prorated`—Available in API version 67.0   and later. - `Trial`—Available in API version 67.0 and   later. - `Yearly`—Available in API version 65.0 and   later. |
| StartDate | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The start date of the group.  If the IsRamped field is set to `true`, Transaction Management sets this date as the start date of all the line items in the group.  Available in API version 65.0 and later. |
| SummaryTotalAmount | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The aggregated total amount of nested group lines before any discounts are applied. Available in API version 65.0 and later. |
| TotalAdjustment | Type  percent  Properties  Filter, Nillable, Sort  Description  The total discount percentage applied at the group level. This percentage is calculated by using the formula: (Summary Total Amount - Summary Subtotal) / Summary Total Amount. Available in API version 65.0 and later. |
| TotalAdjustmentAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The total discount amount at the group level. This amount is calculated by subtracting the summary subtotal from the summary total amount. Available in API version 65.0 and later. |
| TotalCost | Type  currency  Properties  Filter, Nillable, Sort  Description  The aggregated total cost of nested group lines. Available in API version 65.0 and later. |
| TotalMargin | Type  percent  Properties  Filter, Nillable, Sort  Description  The summary margin percentage at the line item level. This percentage is calculated by using the formula: (Summary Subtotal Total Cost) / Summary Subtotal. Available in API version 65.0 and later. |
| TotalMarginAmount | Type  currency  Properties  Filter, Nillable, Sort  Description  The summary margin amount calculated at the group level. Available in API version 65.0 and later. |
