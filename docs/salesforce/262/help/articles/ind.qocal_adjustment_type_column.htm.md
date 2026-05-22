---
article_id: ind.qocal_adjustment_type_column.htm
title: Adjustment Type Column
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_adjustment_type_column.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Adjustment Type Column

The Adjustment Type column merges multiple adjustment fields into a single column so that sales reps can make pricing adjustments more efficiently.

Supported Fields

The Adjustment Type column supports editable currency and percent fields from both quote and order line items and their associated groups. Fields of other data types aren’t supported and don’t appear in this column.

To include a field in the Adjustment Type column, add the field to the Display Columns and select the same field in Select Fields to Group and Display in the Adjustment Type column. Only add fields that are editable and designed for pricing adjustments.

NOTE In Lightning App Builder, don’t select Start Date or End Date in the field selection for the Adjustment Type column. If these fields are included, editing an adjustment type can reset the start and end dates on ramped quote lines.
IMPORTANT Don’t add read-only or calculated fields (such as Total Adjustment) to the Adjustment Type column. When you include non-editable fields, the system attempts to set values on these fields during pricing, which causes errors. If you encounter pricing errors after adding a field to the Adjustment Type column, remove any non-editable fields from the field selection list.
Default Adjustment Fields
Discount Amount
Discount (Percentage)
Margin Amount
Margin (Percentage)
Unit Cost

These adjustment types are available on Quote Line Items, Quote Line Groups, Order Line Items, and Order Item Groups objects.

NOTE You can add custom currency or percent fields to the Adjustment Type column, but verify that the fields are editable. Don't add read-only, calculated, or formula fields.
