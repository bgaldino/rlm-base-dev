---
article_id: ind.rm_create_a_tier_rate_card_entry.htm
title: Create a Rate Card Entry For Tier Rate Cards
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_create_a_tier_rate_card_entry.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Create a Rate Card Entry For Tier Rate Cards

Define different tiers of consumption for a usage resource and set a rate for each of these tiers. With tier-based adjusted rates, provide discounts to customers who have varying consumptions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create rate cards entries:	Rate Management Design Time
From the App Launcher, find and select Rate Management.
From the app navigation menu, select Rate Cards.
Open a rate card record of type tier.
Click Rate Card Entries, and then click New.
Search for and select a usage resource, a sellable product and select its product selling model.
Select the status.
Draft	Indicates that the rate card entry is open for modifications. This is the default value.
Active	Indicates that the rate card entry is in use for rating the usage-based products and you can make limited modifications, such as the status of the record.
Inactive	

Indicates that the rate card entry is not in use anymore.

Search for and select a unit of measure for the rate, such as currency or token.
Choose if the rate is negotiable or non-negotiable.
Set the date range, and then click Next.
Enter the Lower Bound and Upper Bound values.
These values represent the minimum and maximum consumption quantity for a usage resource.
IMPORTANT Values are inclusive and the tiers can’t overlap.
Select an adjustment type.
Percentage	Applies discounts on the usage resource’s consumption in percentage.
Amount	Applies a flat discount amount on the usage resource’s consumption.
Override	Overrides the net unit rate calculated for the usage resource.
Specify the adjustment value.
If the tier type is Percentage, the tier value is the percentage value of the discount, for example, 10%. If the tier type is Amount, the tier value is the flat amount of the discount, for example, $100.
To add more tier-based adjustment rates, click Add Tier.
Save your changes.
SEE ALSO
Create Usage Resources
