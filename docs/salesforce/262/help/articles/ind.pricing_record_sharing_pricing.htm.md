---
article_id: ind.pricing_record_sharing_pricing.htm
title: Configure Record Sharing for Salesforce Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_record_sharing_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Configure Record Sharing for Salesforce Pricing

For runtime users to access the data created by product designers or catalog admins, set up record sharing for all Salesforce Pricing objects. This configuration is crucial for the seamless execution of pricing processes within Salesforce.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create and edit sharing settings:	

Manage Sharing

From Setup, in the Quick Find box, enter Security, and then select Sharing Settings.
Click Edit.
Set Public Read Only as the organization-wide defaults for your users for all Pricing objects based on your security requirements.
Ensure that all Runtime users have Read access to these objects:
Price Book - View Only
Expression Set (for Pricing Procedures) - Public Read Only
Price Adjustment Schedule - Public Read Only
Save your changes.
NOTE Pricing API access is managed via permission sets, which grant read access to entities and allow execution of pricing logic. This makes sharing rules optional for API calls, though sharing rules are still needed for UI access. Run time users have Run Decision Matrices and Run Expression Sets permissions by default.

This completes the basic setup for Salesforce Pricing. To enable other features, see Understand Advanced Pricing Setup.
