---
article_id: ind.um_create_usage_grant_rollover_policy.htm
title: Create Usage Grant Rollover Policy
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_usage_grant_rollover_policy.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Create Usage Grant Rollover Policy

Each grant provided with the product has a validity period. Usage grant rollover policies define whether the usage resource’s grants expire or can be rolled over after the initial validity period is completed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create usage grant rollover policies:	Usage Management Designer
From the App Launcher, find and select Usage Grant Rollover Policies.
Click New.
Enter a name and a unique identifier code.
If the grant units associated with the usage resource can be rolled over, select Rollover Allowed.
If you select Rollover Allowed, specify these values:
If ‌grants must expire after a specific number of rollovers, select Allow Rollover Expiry.
Enter the number of rollovers post when the rolled over grants are considered expired.
Select a status.
	
Draft	Indicates that this record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record is not in use.
Save your changes.
