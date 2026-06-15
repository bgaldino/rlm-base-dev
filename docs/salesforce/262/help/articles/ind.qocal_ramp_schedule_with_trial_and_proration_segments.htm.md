---
article_id: ind.qocal_ramp_schedule_with_trial_and_proration_segments.htm
title: Create a Ramp Schedule with Trial or Prorated Segments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_schedule_with_trial_and_proration_segments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Create a Ramp Schedule with Trial or Prorated Segments

The Create Ramp Schedule guided flow generates a multi-segment deal structure from a single view, replacing error-prone manual cloning. You can configure annual or custom ramp schedules with an optional trial period and flexible prorated segment positioning in one step. Use this flow to close complex multi-year deals faster, align billing to customer fiscal calendars, and offer try-before-you-buy trial periods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create a ramp schedule:	

Create and Edit on QuoteLineGroup permission

AND

Sales rep persona permissions


To open, edit, or create a flow in Flow Builder:	Manage Flow

Before you begin:

In Setup, find and select Revenue Settings. Turn on Ramp Deals for Groups in Quotes and Orders. In Set Up Flow for Creating Ramp Schedules, provide the API name of the flow to use when creating a ramp schedule.

The Create Ramp Schedule flow is included as an active flow and the corresponding revenue setting is preset with the flow name.

In Setup, to use trial segments as an option, turn on Trial Segments for Group Ramp Schedules.
To customize this flow for your ramp schedule business needs, modify the provided flow by using the flow editor.
From Setup, in the Quick Find box, enter Flow, and then select Flows.
Click Create Ramp Schedule.
In the Flow Builder, click Save As New Flow.
Enter a label for the flow. The flow API name automatically populates.
To change the default configurations of the flow, edit the element, select the relevant component, and update the necessary attributes.
Save your changes.
In Accounts, open a quote or an order.
In the Sales Transaction Line Editor actions dropdown list, select Create Ramp Schedule.
Select the Ramp Schedule Configuration details.

Annual: Generates 12-month segments. Requires a minimum total duration of 12 months. Custom: Divides the total duration into a specified number of equal-length segments.

Annual and custom segment types can’t coexist in the same schedule.

(Optional) Specify trial segments.
Prepends a fixed-duration trial period in days or months at a configurable discount. The trial duration is additive. It doesn’t count towards the main schedule duration.
(Optional) Specify a prorated segment position.
A partial-duration segment created when the total duration doesn’t divide evenly into full segment periods. Placed as the first or last segment.
A ramp schedule can contain only one trial segment as the first segment and one prorated segment as the first or last segment.
Review the generated segments, and revise the details as needed.
The Preview page updates as you change ramp schedule values. Verify each segment before proceeding.
Edit dates. Changing the first segment's start date updates the Ramp Schedule Start Date. You can only change the start date for an annual or trial segment. You can edit the start and end dates for a custom segment.
Edit discounts and uplifts.
Before generating the ramp schedule, verify that all the information is correct.
Confirm that there are no errors in the preview table, no segment gaps, or overlapping segments.
Make sure that the ramp schedule contains no more than 12 segments, excluding the trial segment.
Check that segment dates are contiguous and that each segment starts exactly 1 day after the previous segment ends.
Click Create.
EXAMPLE
Annual Ramp with a Trial Segment
Number	Segment Name	Type	Duration	Start Date	End Date
1	Trial	TRIAL	45 Days	Oct 01, 2025	Nov 14, 2025
2	Year 1	ANNUAL	12 Months	Nov 15, 2025	Nov 14, 2026
3	Year 2	ANNUAL	12 Months	Nov 15, 2026	Nov 14, 2027
4	Year 3	ANNUAL	12 Months	Nov 15, 2027	Nov 14, 2028
Annual Ramp with a Prorated Segment
Number	Segment Name	Type	Duration	Start Date	End Date
1	Year 1 - Prorated	ANNUAL - PRORATED	4 Months	Oct 01, 2025	Jan 31, 2026
2	Year 1	ANNUAL	12 Months	Feb 01, 2026	Jan 31, 2027
3	Year 2	ANNUAL	12 Months	Feb 01, 2027	Jan 31, 2028
4	Year 3	ANNUAL	12 Months	Feb 01, 2028	Jan 31, 2029
Annual Ramp with Trial and Prorated Segments
Number	Segment Name	Type	Duration	Start Date	End Date
1	Trial	TRIAL	30 Days	Oct 01, 2025	Oct 30, 2025
2	Year 1	ANNUAL	12 Months	Oct 31, 2025	Oct 30, 2026
3	Year 2	ANNUAL	12 Months	Oct 31, 2026	Oct 30, 2027
4	Year 3 - Prorated	ANNUAL - PRORATED	1 Month	Oct 31, 2027	Nov 29, 2027

If you decide to make updates after creating the ramp schedule.

To add products to any segment, use Browse Catalog from within the segment group. Products inherit the segment's Discount Percent and Uplift Percent.
To modify an existing schedule's dates or segment types after creation, use the Edit Ramp Schedule page. The Create Ramp Schedule flow only creates new, empty ramp schedule structures. The flow doesn’t modify existing ramp schedules.
You can’t clone a prorated segment. To extend a schedule that ends with a prorated segment, clone the last standard segment instead. The process automatically moves the prorated segment's dates forward.
