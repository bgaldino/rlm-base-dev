---
article_id: ind.um_create_usage_aggregation_policy.htm
title: Create Usage Aggregation Policy
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_usage_aggregation_policy.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Create Usage Aggregation Policy

Define the method used to aggregate consumption of a usage resource over a period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create usage aggregation policies:	Usage Management Designer
From the App Launcher, find and select Usage Aggregation Policies.
Click New.
Enter a name and a unique identifier code.
Select an accumulation method.
Sum	Aggregates all events in the specified accumulation period.
Peak	Finds the entry with the maximum consumption within the specified accumulation period.
Select a usage accumulation period.
Select a status.
	
Draft	Indicates that this record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record is not in use.
Save your changes.
