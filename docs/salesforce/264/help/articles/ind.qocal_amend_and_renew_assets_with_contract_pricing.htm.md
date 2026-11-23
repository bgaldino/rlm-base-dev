---
article_id: ind.qocal_amend_and_renew_assets_with_contract_pricing.htm
title: Apply Contract Pricing When Amending or Renewing
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_amend_and_renew_assets_with_contract_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_advanced_amendment_and_renewal_features.htm
fetched_at: 2026-11-23
---

# Apply Contract Pricing When Amending or Renewing

Apply negotiated contract prices or discounts to amendments and renewals to ensure sales reps honor original customer agreements. Maintaining contracts with contract-based pricing includes these negotiated rates in all subsequent lifecycle transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To use contract pricing:	Salesforce Pricing Design Time User
To amend assets:	Amend Assets and Sales Rep permission group
To renew assets:	Renew Assets and Sales Rep permission group
IMPORTANT Refresh the decision table for contract pricing after activating a contract that contains contract item prices or price adjustment schedules.

When you initiate an amendment or renewal from a contract, the system creates a quote associated with that contract. All quote line products use the contract's item prices and price adjustment schedules unless the asset-level pricing source specifies otherwise. If the contract includes a specified renewal term, the system renews assets in the renewal quote for a length equal to that term.

From App Launcher, find and select Contracts.
From the Contract List view, select a contract.
On the Assets tab of the contract, select the assets that you want to amend or renew.
Select Amend or Renew.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_amend_and_renew_assets_with_contract_pricing.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
