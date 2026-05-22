---
article_id: ind.qocal_select_fields_for_the_line_editor.htm
title: Select Fields for the Line Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_select_fields_for_the_line_editor.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Select Fields for the Line Editor

Select line-level fields, group fields, and related record fields in the Display Columns to manage which fields appear in the line editor.

Line-level fields, such as Quantity, Description, and Total Price, appear as individual columns in the editor.
Group fields, such as [Quote Line Group] Subtotal or [Order Line Group] Subtotal, appear only when a quote or order includes groups. If a transaction isn’t grouped, these fields don’t appear in the editor.
Fields from related records, such as [Account] Name, appear as individual columns in the editor. If the related record doesn’t exist, the column shows empty cells that you can’t edit.
NOTE If you add custom fields to the Transaction Line Editor or Sales Transaction Line Editor columns, add those fields to the context definition used for sales transactions. Otherwise, changes made to those fields in the editor aren’t saved when you save your changes.

If you’re using Transaction Line Editor, select both Discount (Percentage) and Discount (Amount) fields in the Display Columns. When both fields are present, the editor merges them into a single Discount column.

If you’re using Sales Transaction Line Editor, configure the Adjustment Type column. See Adjustment Type column.

IMPORTANT If you want the product and group names to appear in Sales Transaction Line Editor, add [Product] Product Name and [Quote Line Group] Quote Line Group Name or [Order Line Group] Order Line Group Name fields to the Display Columns. We recommend you to place the [Product] Product Name field as the first column in the editor.
Merged Columns in Sales Transaction Line Editor

When you add a group field and its corresponding line field to the Display Columns, Sales Transaction Line Editor automatically merges them into a single column. This behavior improves data visibility across group and line levels. The merging applies only to standard fields.

The merged column uses the line-level field name as the header and appears in the position of the first selected field in the Display Columns. When you view groups, the editor shows values from the group record. When you view line items, the editor shows values from the line record.

By default, these group-level and line-level fields merge into a single column when you add them to the Display Columns in Sales Transaction Line Editor.

QUOTELINEITEM FIELD	QUOTELINEGROUP FIELD	ORDERITEM FIELD	ORDERITEMGROUP FIELD
Product.Name	Name	Product.Name	Name
NetTotalPrice	SummarySubtotal	NetTotalPrice	SummarySubtotal
SortOrder	SortOrder	SortOrder	SortOrder
Description	Description	Description	Description
StartDate	StartDate	ServiceDate	ServiceDate
EndDate	EndDate	EndDate	EndDate
SegmentType	SegmentType	SegmentType	SegmentType
TotalLineAmount	SummaryTotalAmount	TotalLineAmount	SummaryTotalAmount
TotalCost	TotalCost	TotalCost	TotalCost
TotalAdjustment	TotalAdjustment	TotalAdjustment	TotalAdjustment
TotalAdjustmentAmount	TotalAdjustmentAmount	TotalAdjustmentAmount	TotalAdjustmentAmount
TotalMargin	TotalMargin	TotalMargin	TotalMargin
TotalMarginAmount	TotalMarginAmount	TotalMarginAmount	TotalMarginAmount
QuoteLineGroup	ParentQuoteLineGroup	OrderItemGroup	ParentOrderItemGroup
NOTE If a field supports both group-line merging and Adjustment Type merging, the Adjustment Type merge takes precedence. The field appears in the Adjustment Type column instead of merging with its related group or line field.
