---
article_id: ind.qocal_renew_expired_usage_based_assets.htm
title: Renew Expired Usage-Based Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renew_expired_usage_based_assets.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amending_rates_and_grants_on_usage_based_products.htm
fetched_at: 2026-09-04
---

# Renew Expired Usage-Based Assets

Continue a customer's subscription after a usage-based asset expires by setting a new renewal term and negotiating rates and grants.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To renew expired usage-based assets:	InitiateRenewal API permission set AND Sales Rep persona permissions
NOTE Renewal of expired usage-based assets is available in orgs with the Revenue Cloud Advanced license. If an org has the Revenue Cloud Advanced and Revenue Cloud Billing licenses, or if the Revenue Cloud Billing license is added later, you can't renew expired usage-based assets.

Confirm that the asset expired at the end of its term. A canceled asset isn't eligible for renewal.

When a customer wants to continue a usage-based product after its subscription ends, renew the expired asset instead of creating a new one. The renewal start date must be on or after the asset's lifecycle end date. It can be in the past, today, or in the future. No grace period applies when renewing an expired usage-based asset.

If a gap exists between the asset's lifecycle end date and the renewal start date, a zero-quantity Asset State Period is added for the gap.

NOTE When you renew an expired ramp usage-based asset, the renewed asset is non-ramped. Creating new ramp segments during late renewal isn't supported.

To renew assets through the Managed Asset Viewer, see Renew Assets with the Managed Asset Viewer.

From the App Launcher, find and select Accounts.
Select the customer's account, and then select the Assets tab.
Select the expired usage-based asset that you want to renew.
Select Renew.
On the Set Renewal Term prompt, select Override Renewal Term, and then enter a Renewal Term Start Date.

Set a date on or after the asset's lifecycle end date. Selecting a renewal start date overrides the existing subscription renewal term.

To save your changes, click Submit.

The renewal quote opens for the asset.

Review and negotiate the rates and grants for the new term, and then finalize the quote.

The renewed term begins on the renewal start date. The asset's usage entitlements and rate cards are updated for the new term.

No usage records are associated with zero-quantity Asset State Periods during gap periods. Consumption or rating of usage during a gap period isn't supported.

EXAMPLE

A customer's usage-based subscription ended on March 31, and the customer signs a new deal on May 15. You select the expired asset, click Renew, click Override Renewal Term, and then set the renewal start date to May 15. Because the renewal starts after the asset's lifecycle end date, a zero-quantity Asset State Period is added for the gap between the lifecycle end date and the renewal start date. The renewed term begins on May 15.

For rate and grant negotiation on usage-based products, see Usage-Based Assets.
