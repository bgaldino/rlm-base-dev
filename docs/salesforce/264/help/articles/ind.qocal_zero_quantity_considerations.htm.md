---
article_id: ind.qocal_zero_quantity_considerations.htm
title: Zero-Quantity Quote Detail Lines Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_zero_quantity_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-09-04
---

# Zero-Quantity Quote Detail Lines Considerations

Zero-quantity quote detail lines appear when the lifecycle transaction state must be preserved even though the effective quantity for a period equals zero.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

These instances create zero-quantity detail lines.

When an amendment changes an attribute and reduces the quantity from the current value to zero.
When an amendment shortens or extends the duration of an asset lifecycle.
When you override the default renewal term and specify a custom start date instead of waiting for automatic renewal creation. In this case, the transaction sets the quantity to zero for the renewal period to represent a pause state rather than a complete cancellation.
How to Interpret Zero-Quantity Detail Lines
Amendment and renewal transactions can create detail lines that preserve lifecycle history across original and updated periods.
Cancellation and repricing lines represent different lifecycle states, including valid zero-quantity periods.
A zero-quantity period alone doesn't mean that the asset is permanently cancelled.
Assetization records these transitions in asset state and action source data to maintain transaction continuity.
