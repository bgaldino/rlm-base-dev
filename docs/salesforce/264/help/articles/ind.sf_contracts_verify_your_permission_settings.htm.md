---
article_id: ind.sf_contracts_verify_your_permission_settings.htm
title: Verify Permissions for Salesforce Contracts Analytics
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_verify_your_permission_settings.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_analytics_post-installation_steps.htm
fetched_at: 2026-10-13
---

# Verify Permissions for Salesforce Contracts Analytics

When you turn on CRM Analytics for your org, a default Analytics Integration User is created. This user accesses the data within Salesforce when the recipe is used to bring data in as datasets to CRM Analytics.

It's important that this user has the proper level of permissions to read the data that you're trying to pull from the org to CRM Analytics. For example, the integration user must have read access to all the objects from which to pull data. This user also needs read access to the fields within those objects. If you have trouble creating your app or can’t view data, modify either object or field permissions.
