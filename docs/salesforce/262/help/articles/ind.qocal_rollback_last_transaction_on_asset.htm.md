---
article_id: ind.qocal_rollback_last_transaction_on_asset.htm
title: Roll Back the Last Transaction for an Asset
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_rollback_last_transaction_on_asset.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Roll Back the Last Transaction for an Asset

To reverse the most recent future-dated amendment or renewal due to errors or changes in customer plans, use the Rollback feature. This action restores the asset to its original state, eliminating the need for complicated manual workarounds.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To roll back the last transaction for an asset:	InitiateAmend user permission

The Rollback feature reverts an asset to its previous state by creating a counteracting transaction. It preserves a complete history of all transactions to ensure data integrity through a ledger-style approach.

For example, if you renew a subscription but require a quantity adjustment first, roll back the renewal, amend the quantity, and then process the corrected renewal.

Go to the Accounts or Contracts page containing the asset.
On the Assets tab, in the Managed Asset Viewer, select the asset for the transaction reversal.
Select Rollback.
The rollback process generates a new quote or order to reverse the previous transaction. You can't edit the transaction lines on this new record to perform another complete reversal.
Activate the generated rollback quote or order.
A new quote or order appears with an Amend action type and a Rollback subtype.
Your asset returns to its state before the rolled-back transaction.
Asset Action, Asset Action Source, and Asset State Period records update automatically to reflect the reversal. .
A new asset action provides a Rolledback Asset Action lookup link to the original reversed action.

Review the asset history to confirm the rollback processed correctly. Check the asset action related to the asset for a new record with type Amend and subtype Rollback. Verify that this record points to the reversed asset action and that the asset state matches its condition before the rollback transaction.
