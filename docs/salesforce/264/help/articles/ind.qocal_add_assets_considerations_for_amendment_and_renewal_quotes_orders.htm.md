---
article_id: ind.qocal_add_assets_considerations_for_amendment_and_renewal_quotes_orders.htm
title: Add Assets Considerations for Amendment and Renewal Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_add_assets_considerations_for_amendment_and_renewal_quotes_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle_considerations.htm
fetched_at: 2026-09-04
---

# Add Assets Considerations for Amendment and Renewal Quotes and Orders

Before you add assets to an amendment or renewal quote or order, understand how the Contract lookup field affects which assets are eligible to appear in the Add Assets modal.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Advanced license.
When the Contract field on the quote or order is populated, the Add Assets modal shows only assets related to that contract through an Asset Contract Relationship (ACR). Assets that exist on the account but lack an ACR to the specified contract don't appear in the modal, even if they're otherwise eligible.
When the Contract field is blank, the Add Assets modal retrieves all eligible assets at the account level, regardless of ACR.
