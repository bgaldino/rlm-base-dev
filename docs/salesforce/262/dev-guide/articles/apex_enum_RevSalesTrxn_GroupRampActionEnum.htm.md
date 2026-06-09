---
page_id: apex_enum_RevSalesTrxn_GroupRampActionEnum.htm
title: GroupRampActionEnum Enum
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_enum_RevSalesTrxn_GroupRampActionEnum.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_RevSalesTrxn.htm
fetched_at: 2026-06-09
---

# GroupRampActionEnum Enum

Specifies the action ‌that you want to perform on group ramp segments. Additionally,
you can also convert a non-ramped group into a ramped group.

## Enum Values

The `RevSalesTrxn.GroupRampActionEnum` enum includes these values.

| Value | Description |
| --- | --- |
| `AddProducts` | Specifies to add rampable products to group ramp segments. |
| `DeleteProducts` | Specifies to delete ramped products. |
| `EditGroup` | Specifies to convert a non-ramped group into a group ramp segment, or edit group ramp segment attributes such as name and description, except the start and end dates. |
| `EditRampSchedule` | Specifies to edit details of the group ramp segments, including start and end dates. |
| `DeleteSegment` | Specifies to delete the first or last segment in a group ramp schedule. |
| `ConvertToNonRampedGroup` | Specifies to convert the first or last group ramp segment into a non-ramped group. |

To add or delete ramped line items from multiple group ramp segments, pass all the applicable
values in the `graph` request. To refer to Connect API
examples that specify actions to create ramp deals for groups, see [Group Ramp Action Input](./connect_requests_group_ramp_action_input.htm.md "Understand the sample request to specify group ramp actions during initial sale.").
