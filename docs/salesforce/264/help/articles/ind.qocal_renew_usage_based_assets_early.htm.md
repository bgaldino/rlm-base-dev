---
article_id: ind.qocal_renew_usage_based_assets_early.htm
title: Renew Usage-Based Assets Early
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renew_usage_based_assets_early.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_amending_rates_and_grants_on_usage_based_products.htm
fetched_at: 2026-09-04
---

# Renew Usage-Based Assets Early

Change pricing on an active usage-based asset before the asset's end date by setting a new renewal term and negotiating rates and grants.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
For early renewal of usage-based assets:	InitiateRenewal API permission set AND Sales Rep persona permissions
NOTE Early renewal of usage-based assets is available in orgs with the Revenue Cloud Advanced license. If an org has the Revenue Cloud Advanced and Revenue Cloud Billing licenses, or if the Revenue Cloud Billing license is added later, you can't renew usage-based assets early.

Confirm that the asset is active and uses a term-defined product selling model. Early renewal is available for assets that use the Anchor, Pack, and Commitment usage models, but not for assets that use the one-time or evergreen product selling model.

Early renewal replaces an active asset's current term with a new term instead of creating a new asset. The renewal start date must be in the future and on or before the asset's end date. Early renewal ends the current term on the day before the renewal start date and begins the renewed term on the renewal start date.

You can renew a single asset from the account's Assets tab or renew multiple assets from the Managed Asset Viewer. To renew assets through the Managed Asset Viewer, see Renew Assets with the Managed Asset Viewer.

From the App Launcher, find and select Accounts.
Select the customer's account, and then select the Assets tab.
Select the active usage-based asset that you want to renew.
Select Renew.
On the Set Renewal Term prompt, select Override Renewal Term, and then enter a Renewal Term Start Date and a Renewal Term End Date.

Set a start date in the future, on or before the asset's end date. Set an end date on or after the renewal term start date. Selecting a renewal term start date overrides the existing subscription renewal term.

To save your changes, click Submit.

The renewal quote opens for the asset.

Review and negotiate the rates and grants for the new term, and then finalize the quote.
Activate the renewal order to create the renewed asset.

The current term ends and the renewed term begins on the renewal start date. The asset's usage entitlements and rate cards are updated for the new term.

EXAMPLE

A customer's usage-based subscription runs from January 1, 2026, through December 31, 2026. On April 1, 2026, you renew the asset early to apply new rates. You select the active asset, select Renew, select Override Renewal Term, and then set the renewal start date to April 1, 2026. The current term ends on March 31, 2026, and the renewed term runs from April 1, 2026, through March 31, 2027.

For rate and grant negotiation on usage-based products, see Usage-Based Assets.

To renew a usage-based asset after its term ends, see Renew Expired Usage-Based Assets.
