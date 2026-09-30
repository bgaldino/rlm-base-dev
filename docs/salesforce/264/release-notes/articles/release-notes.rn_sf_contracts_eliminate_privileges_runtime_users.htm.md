---
article_id: release-notes.rn_sf_contracts_eliminate_privileges_runtime_users.htm
title: Protect Sensitive Setup Data by Removing Elevated Permissions from Runtime Users
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_sf_contracts_eliminate_privileges_runtime_users.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_contracts.htm
fetched_at: 2026-09-30
---

# Protect Sensitive Setup Data by Removing Elevated Permissions from Runtime Users

Your runtime users can now perform contract lifecycle operations without the View Setup and Configuration permission. Previously, they needed this elevated permission to access org-level setup data for contract lifecycle tasks, such as creating and editing documents in the Microsoft 365 Word add-in, creating contracts from quotes, and managing electronic signatures. The user experience remains unchanged while sensitive setup configuration data stays protected.

Where: This change applies to Lightning Experience in Enterprise, Performance, and Unlimited editions of Agentforce Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Advanced license or with the Salesforce Contracts license.
