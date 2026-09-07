---
article_id: ind.um_create_usage_commitment_policy.htm
title: Create a Usage Commitment Policy
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_usage_commitment_policy.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_configure_usage_records.htm
fetched_at: 2026-09-07
---

# Create a Usage Commitment Policy

Define the set of rules that determine how commitments are applied to a usage resource.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create usage commitment policies:	Usage Management Designer
From the App Launcher, find and select Usage Commitment Policies.
Click New.
Enter a name for the policy.
Select a value that indicates the rate applicable after the initial commitment is fulfilled.
	
Bounded Object Rate	Bill overage at the rate defined on the object bound to the line item. Ideal when the commitment has a discounted rate and consumption over the commitment has a separately defined rate.
Lowest Commitment Rate	Bill overage at the lowest negotiated commitment rate after the customer consumes beyond the committed quantity. Ideal for a single unified tier structure where the commitment and overage rates are identical.
Save your changes.
EXAMPLE
Bounded Object Rate: A customer purchases a mobile data plan. The first 10 GB is included in their commitment at $1 per GB, which is the committed rate. If they consume 12 GB, the extra 2 GB is billed at the anchor product rate of $15 per GB. The $15 per GB rate is the standard retail rate on the bound asset. This model suits plans where committed usage is discounted, but overage carries a higher rate.
Lowest Commitment Rate: A customer purchases a cloud storage product with a standard rate of $10 per GB. They commit to 1,000 GB at a discounted rate of $8 per GB. If they consume 1,200 GB, the extra 200 GB is also billed at $8 per GB. Use the Lowest Commitment Rate when you want one consistent rate across both committed consumption and overage.
SEE ALSO
Create a Usage Overage Policy
Commitment Product Drawdowns
