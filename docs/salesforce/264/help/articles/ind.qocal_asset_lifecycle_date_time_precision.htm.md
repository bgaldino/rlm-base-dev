---
article_id: ind.qocal_asset_lifecycle_date_time_precision.htm
title: Honor Precise Time Zones in Asset Lifecycle Start and End Dates
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_lifecycle_date_time_precision.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_manage_assets_in_revenue_lifecycle_management.htm
fetched_at: 2026-09-04
---

# Honor Precise Time Zones in Asset Lifecycle Start and End Dates

Specify exact time zone precision for asset lifecycle start and end dates to meet detailed contract requirements and manage complex global subscriptions. Time resolution makes sure that asset state periods (ASPs) and subsequent amend, renew, cancel, transfer, and swap operations start and end exactly as specified, providing parity for noncontiguous changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To specify time precision on quotes:	Create on Quotes
To specify time precision on orders:	PlaceOrder API permission set
IMPORTANT Set field-level security for the Start Time, End Time, and Start End Time Zone fields on the Quote Line Item and Order Product objects. You need the ManageAssets or CalmSObject permission set to set field-level security. Set Field-Level Security for a Field on All Profiles.

Standardized asset lifecycle processes honor the order line item (OLI) date and time when setting asset and ASP start and end dates during Order-to-Asset and Order-Product-to-Asset processes. By moving beyond the default 00:00:00 universal time-coordinated (UTC) setting, Revenue Management handles precise moments, such as a 12:00 AM PST start and 11:59 PM PST end.

During assetization, the line item time zone is stored on the ASP. When you amend, renew, or cancel an asset, the stored time zone is used to show the start and end dates and times instead of defaulting to UTC. This behavior keeps amendment and renewal dates aligned with the stored time zone and calculates the correct period boundary day.

Review these considerations for time precision.

All the line items in a transaction must have the same time zone.
Set the time zone on the quote or order line items to match the time zone on the ASP.
The pricing engine calculates prices by using UTC and doesn't support time precision.
Proration calculations use date precision only.
If you don't specify a start time, the start time defaults to 12:00:00 AM in the local time zone. If you don't specify an end time, the end time defaults to 11:59:59 PM in the local time zone.
If you don't specify a start or end time, the system defaults the time portion to 12:00 AM in the local time zone.
The system translates and stores all specified local times in UTC for disambiguation.
Each line item inherits its time zone from its source asset. When you amend, renew, or cancel multiple assets in a single action, use the same time zone for all the assets.
Set the Start End Time Zone field on a new sale to the customer's local time zone. The time zone is stored on the ASP and used for subsequent amendments, renewals, and cancellations.
Assets that are assetized before the time zone is stored on the ASP use UTC until they’re reassetized or you populate the time zone on the asset's existing ASPs.
In Setup, find and select Lightning App Builder.
Click Edit next to Order Record Page or Quote Record Page in the Lightning page list.
On the Components tab, find and select Transaction Line Editor, or drag it to the page if it isn't present.
On the right, click Select... next to Display Columns.
Move the Start Time, End Time, and Start End Time Zone fields from the Available section to the Selected section.
Click OK.
Save your changes.
Set field-level security for the Start End Time Zone field on the Asset State Period object.
Sync the context definition.

When field-level security is enabled for the Start End Time Zone field on the Asset State Period object, the sync updates the field mapping automatically. No manual mapping is required.

Initial Sale Example

A sales rep specifies a start time of 1/1/2025 9:00:00 PST and an end time of 12/31/2025 8:59:59 PST. The transaction system translates the time to 1/1/2025 17:00:00 UTC and 12/31/2025 16:59:59 UTC, respectively.

Amendment Example

An asset runs from 1/1/2025 17:00:00 UTC to 12/31/2025 16:59:59 UTC. A sales rep amends the asset with a start time of 2/1/2025 11:00 AM PST (2/1/2025 19:00:00 UTC). Upon assetization, the system creates consecutive ASPs.

The first ASP ends at 2/1/2025 18:59:59 UTC.
The new ASP starts exactly at 2/1/2025 19:00:00 UTC and ends at 12/31/2025 16:59:59 UTC.

Amendment Time Zone Example

A customer buys a yearly subscription with a start date and time of 1/1/2026 12:00 AM PST and an end date and time of 12/31/2026 11:59 PM PST. The time zone is stored on the ASP. When a sales rep initiates an amendment effective 7/1/2026, the amendment line items use the stored time zone instead of UTC. The amendment shows a start date and time of 7/1/2026 12:00 AM PT and an end date and time of 12/31/2026 11:59 PM PST.
