---
article_id: ind.qocal_considerations_usage_selling.htm
title: Usage Selling Assets Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_usage_selling.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Usage Selling Assets Considerations

Understand the limitations and behaviors of usage-based assets before setting up or selling usage products. Reviewing these requirements ensures accurate grant management, consumption tracking, and account binding throughout the asset lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Usage Asset Lifecycle Behaviors

When you manage usage-based assets, the system applies specific rules to rates and resource grants.

Amended Rates: The rate for an amended asset changes to reflect the new terms.
Unused Grants: The system forfeits any unused resource grants when you renew or cancel the asset.
Grant Proration: The system supports proration for these scenarios.
Amendments: The amendment process prorates new grants amended mid-term for the remaining duration.
Refreshes: The refresh process prorates new grants.
Cancellations: The cancellation process prorates grants for the remaining duration based on the cancellation date.
Consumption Object Updates for Same-Day Cancellations

When you create and cancel assets within the same day, associated consumption objects remain active. Update the following fields to prevent continuous summary generation and rating failures caused by missing rate card entries.

CONSUMPTION OBJECT	FIELD UPDATES
Usage Entitlement Account	Set the end date and time to match the start date and time.
Usage Entitlement Bucket	Set the end date and time to match the start date and time.
Transaction Usage Entitlement	Set the end date and time to match the start date and time.
Liability Summary	Set status to Invoiced.
Usage Ratable Summary	Set status to Rated and rate to zero.
Usage Summary	Set status to Liable Summary Complete.
Grant Binding Requirements

The transaction system prioritizes accounts for grant binding based on the specified hierarchy.

1. Opportunity Account
If present, the system uses the opportunity account even if an account for quote exists.
2. Account for Quote
If the opportunity account is missing, the system uses the account specified in the Account for Quote field.
3. Binding Failure
Grant binding fails if both the opportunity account and account for quote are missing.
NOTE

If you disable the Create Quotes Without a Related Opportunity setting, the Account for Quote field is unavailable. Binding fails in this scenario even if an opportunity is linked to the quote.
