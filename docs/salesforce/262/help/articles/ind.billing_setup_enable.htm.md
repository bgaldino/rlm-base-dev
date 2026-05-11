---
article_id: ind.billing_setup_enable.htm
title: Turn On Billing in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_enable.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_setup.htm
fetched_at: 2026-05-11
---

# Turn On Billing in Agentforce Revenue Management

Enable Billing to start using Billing features.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To turn on Billing:	System Administrator profile with the Customize Application user permission
IMPORTANT You can’t turn on Billing when Subscription Management is enabled in your org.
From Setup, in the Quick Find box, enter Billing, and then select Billing Settings.
Turn on Billing.

To avoid facing access issues after turning on Billing and before setting up Billing features, assign the Billing Admin and Billing Operations User permission sets to users with the System Administrator profile.

NOTE

After turning on Billing, order activation succeeds only if the Order records have values for the Bill to Contact, Billing Address, and Shipping Address fields. Order activation fails if any of these values are missing.

SEE ALSO
Knowledge Article: Disable Subscription Management to use Billing in Revenue Cloud
Select Context Definition and Mapping for Create Billing Schedules for Orders API
Select Default Billing Treatment, Tax Treatment, and Legal Entity
Set Up Financial Accounting Features
