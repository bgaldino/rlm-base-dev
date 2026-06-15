---
article_id: ind.qocal_ramp_deals_asset_considerations.htm
title: Ramped Asset Management Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals_asset_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Ramped Asset Management Considerations

Familiarize yourself with specific requirements for amending, renewing, or canceling ramped assets to manage multi-segment deals effectively. These considerations ensure data consistency and help you navigate system limitations across different ramp configuration settings.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Ramp Configuration Settings and Behaviors

Ramped asset management depends on your organization's specific revenue settings.

SETTING CONFIGURATION	AMENDMENT & TRANSACTION BEHAVIOR	SEGMENT MANAGEMENT


Single Ramp Schedule Per Transaction

Ramp Deals for Groups - ON
Multiple Ramp Schedules - OFF
	Amend multiple ramped assets in a single transaction only if the start and end dates of all their asset state period (ASP) records match.	The transaction system prohibits the addition or deletion of ramp segments during asset amendments.


Multiple Ramp Schedules Per Transaction

Ramp Deals for Groups - ON
Multiple Ramp Schedules - ON
	

Amend multiple ramped and nonramped assets in one transaction, even if their ASP start and end dates don't match.

Transaction Management groups assets into a ramp schedule when the asset lifecycle and all ASP dates match.

	

You can't add or delete segments for existing assets.

You can create group ramp schedules on amendment, renewal, and cancellation quotes or orders to generate other ramp deals.

Automatic Segment Generation and Renewals
Transaction Management automatically creates groups in the resulting quote or order when you amend or cancel ramped assets while the Ramp Deals for Groups in Quotes and Orders setting is active.
You can’t change the start and end dates of these auto-generated segments to amend existing assets.
During the renewal of a ramped asset, the price uplift from the final segment becomes the renewal uplift.
Feature Limitations

You can’t use these capabilities when amending, renewing, or canceling ramped assets:

Lot-based renewal
Asset transfer
Early renewal
Roll back the most recent amendment
