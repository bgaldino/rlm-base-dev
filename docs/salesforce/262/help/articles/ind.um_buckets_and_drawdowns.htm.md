---
article_id: ind.um_buckets_and_drawdowns.htm
title: Buckets and Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_buckets_and_drawdowns.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Buckets and Drawdowns

A bucket acts as a digital wallet that holds a customer's available grants or entitlements. Consumption Management creates usage entitlement buckets after the product is sold and assetized. When usage summaries are created, Consumption Management performs a drawdown to deduct the consumed units from these buckets. If the usage exceeds the available bucket balance, the remaining quantity is accounted as overage.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Usage Entitlement Bucket Balance-Related Fields

The Usage Entitlement Bucket object provides these fields to help you track available balances.

FIELD	DESCRIPTION
Total As of Balance	Aggregated total of all grants available as of the current date.
Bucket Balance	Balance available at an individual (child) bucket level.
Total Provisional Balance	Aggregated balance used during daily rating to reflect in-progress drawdowns.
Provisional Balance	Temporary balance at the individual bucket level while the daily rating is in progress.
Parent and Child Buckets

The parent bucket represents the combined total balance of a specific resource across the binding target, which can be an account, an anchor asset, a contract, or a custom object. Child buckets represent the actual specific grants tied to an individual grant action, such as a new purchase, a grant renewal, a grant refresh, or grant rollover, or an amendment.

Drawdown Orders

If a customer has multiple child buckets for the same resource, you must define the order of buckets that consumption management uses for drawdown. Use the Drawdown Order field in the associated Product Usage Grant record. The field provides these valid values.

Expiring First—draws from the bucket that is closest to its expiration date. This is the default value.
Granted First—draws from the oldest bucket, based on the earliest start date.
Granted Last—draws from the newest bucket, based on the most recent start date.
How to Determine the Resulting Bucket Balance

To determine the expected bucket balance after the consumption is processed, evaluate the bucket balance before usage, the consumption date, and any active lifecycle changes like amendments, renewals, or cancellations. You must also account for the quantity being rated and the balance status—provisional or finalized. The resulting balance reflects the net remaining grants after the drawdown is applied.

Anchor Product Drawdowns
An anchor product is the base purchase, such as a basic mobile plan that offers 4,000 text messages. When this anchor product is sold, the initial entitlement of 4,000 text messages is granted and is placed into a child bucket.
Pack Product Drawdowns
Pack products are add-ons purchases that supplement an existing anchor product, such as adding a temporary international roaming pack or extra data.
Commitment Product Drawdowns
In a commitment product, the customer commits to consuming a specific quantity, token amount, or monetary spend in exchange for discounted rates. Commitments are applied by associating the commitment product with an anchor product.
Token Commitment Drawdowns
The consumption process for token commitments uses a two-step rating procedure. The process in the first step converts usage to tokens, and then in the second step, tokens to currency.
Token Commitment Drawdown Use Cases
The relationship between commitments and anchors, and how their consumption is processed varies depending on the binding target and the number of active products.
Consumption Proration Calculations
Proration is used to ensure that customers are only billed or granted resources for the fraction of a billing period that a product was active. Consumption Management uses a proration engine that performs the calculation and provides accurate billing.
