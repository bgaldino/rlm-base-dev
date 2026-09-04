---
article_id: ind.qocal_ramp_schedule_with_trial_and_proration_segments.htm
title: Use the Create Ramp Schedule Guided Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_schedule_with_trial_and_proration_segments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_for_groups_considerations.htm
fetched_at: 2026-09-04
---

# Use the Create Ramp Schedule Guided Flow

The Create Ramp Schedule guided flow generates a full multi-segment deal structure in one step.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To create a ramp schedule:	

Create and Edit on QuoteLineGroup

AND

Sales rep persona


To open, edit, or create a flow in Flow Builder:	Manage Flow
Open a quote or order.
In the Sales Transaction Line Editor actions dropdown list, select Create Ramp Schedule.
Select the schedule type.
Annual: Generates 12-month segments. The minimum total duration is 12 months.
Custom: Divides total duration into a specified number of equal-length segments.
Annual and custom segment types can't coexist in the same schedule.
Optionally add a trial segment.
A trial segment is a fixed-duration trial period (in days or months) prepended before the main schedule. Trial duration is additive—it doesn't count toward the main schedule duration.
Optionally specify a prorated segment position (first or last) for cases where the total duration doesn't divide evenly into full periods. A ramp schedule can contain only one trial segment (as the first segment) and one prorated segment (as the first or last segment).
Review the generated segments, and revise the details as needed.
Edit dates. Changing the first segment's start date updates the Ramp Schedule Start Date. You can only change the start date for an annual or trial segment. You can edit the start and end dates for a custom segment.
Edit discounts and uplifts.
Before generating the ramp schedule, verify:
There are no errors, gaps, or overlapping segments.
The schedule has no more than 12 segments, excluding the trial segment.
Segment dates are contiguous—each segment starts exactly 1 day after the previous segment ends.
Click Create.
EXAMPLE
Annual Ramp with a Trial Segment
Number	Segment Name	Type	Duration	Start Date	End Date
1	Trial	TRIAL	45 Days	Oct 01, 2025	Nov 14, 2025
2	Year 1	ANNUAL	12 months	Nov 15, 2025	Nov 14, 2026
3	Year 2	ANNUAL	12 months	Nov 15, 2026	Nov 14, 2027
4	Year 3	ANNUAL	12 months	Nov 15, 2027	Nov 14, 2028
Annual Ramp with a Prorated Segment
Number	Segment Name	Type	Duration	Start Date	End Date
1	Year 1 - Prorated	PRORATED	4 months	Oct 01, 2025	Jan 31, 2026
2	Year 1	ANNUAL	12 months	Feb 01, 2026	Jan 31, 2027
3	Year 2	ANNUAL	12 months	Feb 01, 2027	Jan 31, 2028
4	Year 3	ANNUAL	12 months	Feb 01, 2028	Jan 31, 2029
Annual Ramp with Trial and Prorated Segments
Number	Segment Name	Type	Duration	Start Date	End Date
1	Trial	TRIAL	30 days	Oct 01, 2025	Oct 30, 2025
2	Year 1	ANNUAL	12 months	Oct 31, 2025	Oct 30, 2026
3	Year 2	ANNUAL	12 months	Oct 31, 2026	Oct 30, 2027
4	Year 3 - Prorated	PRORATED	1 month	Oct 31, 2027	Nov 29, 2027

After creating the ramp schedule, keep in mind:

To add products to any segment, use Browse Catalog from within the segment group. Products inherit the segment's Discount Percent and Uplift Percent.
To modify an existing schedule's dates or segment types after creation, use Edit Ramp Schedule. The Create Ramp Schedule flow only creates new, empty ramp schedule structures—it doesn't modify existing ramp schedules.
You can't clone a prorated segment. To extend a schedule that ends with a prorated segment, clone the last standard segment instead. The process automatically moves the prorated segment's dates forward.
