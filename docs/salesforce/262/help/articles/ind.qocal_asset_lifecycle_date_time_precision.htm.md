---
article_id: ind.qocal_asset_lifecycle_date_time_precision.htm
title: Honor Precise Time Zones in Asset Lifecycle Start and End Dates
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_lifecycle_date_time_precision.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Honor Precise Time Zones in Asset Lifecycle Start and End Dates

Specify exact time zone precision for asset lifecycle start and end dates to meet detailed contract requirements and manage complex global subscriptions. Time resolution makes sure that asset state periods (ASPs) and subsequent amendments start and end exactly as specified, providing parity for noncontiguous changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To specify time precision on quotes:	Create on Quotes
To specify time precision on orders:	PlaceOrder API permission set
IMPORTANT Set field-level security for the Start Time, End Time, and Start End Time Zone fields on the Quote Line Item and Order Product objects. See Set Field-Level Security for a Field on All Profiles.

Standardized asset lifecycle processes honor the order line item (OLI) date and time when setting asset and ASP start and end dates during Order-to-Asset and Order-Product-to-Asset processes. By moving beyond the default 00:00:00 UTC setting, Revenue Management handles precise moments, such as a 12:00 AM PST start and 11:59 PM PST end.

Review these considerations for time precision.

The pricing engine calculates prices by using universal time-coordinated (UTC) and doesn’t support time precision.
Proration calculations use date precision only, not time precision.
If you don’t specify a start or end time, the system defaults the time portion to 12:00 AM in the local time zone.
The system translates and stores all specified local times in UTC for disambiguation.
In Setup, find and select Lightning App Builder.
Click Edit next to Order Record Page or Quote Record Page in the Lightning Pages list.
On the Components tab, find and select Transaction Line Editor, or drag it to the page if it isn’t present.
On the right, click Select... next to Display Columns.
Move the Start Time, End Time, and Start End Time Zone fields from the Available section to the Selected section.
Click OK.
Save your changes.

Initial Sale Example

A sales rep specifies a start time of 1/1/2025 9:00:00 PST and an end time of 12/31/2025 8:59:59 PST. The transaction system translates the time to 1/1/2025 17:00:00 UTC and 12/31/2025 16:59:59 UTC respectively.

Amendment Example

An asset runs from 1/1/2025 17:00:00 UTC to 12/31/2025 16:59:59 UTC. A sales rep amends the asset with a start time of 2/1/2025 11:00 AM PST (2/1/2025 19:00:00 UTC). Upon assetization, the system creates consecutive ASPs.

The first ASP ends at 2/1/2025 18:59:59 UTC.
The new ASP starts exactly at 2/1/2025 19:00:00 UTC and ends at 12/31/2025 16:59:59 UTC.
