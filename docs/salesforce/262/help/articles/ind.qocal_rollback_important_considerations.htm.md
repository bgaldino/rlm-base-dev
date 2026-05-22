---
article_id: ind.qocal_rollback_important_considerations.htm
title: Transaction Rollbacks Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_rollback_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Transaction Rollbacks Considerations

Understand the requirements and limitations of the rollback feature to reverse the most recent transaction on an asset. Familiarizing yourself with these rules ensures data integrity and helps you determine when a transaction is eligible for reversal.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Rollback Eligibility and Usage

Review these critical constraints and behaviors before initiating a rollback.

Timing Restrictions: You only roll back future-dated transactions that haven’t started. If the start date occurred in the past or occurs today, the system prohibits rolling back the last transaction.
Bundle Constraints: Rollback rules apply to child products within a bundle. If renewal or amendment of any child product has started, you can’t roll back the entire bundle transaction.
Transaction Scope: The system doesn’t support the partial rollback of a transaction.
Legacy Data: You can’t roll back assets created before the Salesforce Winter '26 release.
Sequence of Actions: The rollback action always applies to the most recent or last transaction. You can perform multiple rollbacks to undo transactions sequentially. After you roll back the last transaction, you can then roll back the next most recent transaction.
Action Restrictions: You can’t roll back a rollback transaction.
Unsupported Transaction Types: The system doesn’t support the rollback of initial sales, cancellations, or transfer transactions.
Feature Incompatibility: The system doesn’t support rollbacks for asset transactions involving ramps, usage-based products, or Dynamic Revenue Orchestration features.
