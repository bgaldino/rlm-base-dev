---
article_id: ind.sf_contracts_salesforce_contracts_troubleshooting_guide.htm
title: Salesforce Contracts Troubleshooting Reference
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_salesforce_contracts_troubleshooting_guide.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
fetched_at: 2026-10-13
---

# Salesforce Contracts Troubleshooting Reference

Tips for troubleshooting user access and permissions related to Salesforce Contracts.

ISSUE	WHAT IT MEANS	HOW TO FIX IT
The Compare Contracts window keeps loading continuously for a non-admin user.	The non-admin user's custom profile or permission set doesn't have the required access to the Generated Documents object or the Reference Object field. This issue occurs when a custom profile or permission set is used instead of the out-of-the-box standard profile or permission set.	In the non-admin user's profile or permission set, grant Read access to the Generated Documents object and Read access to the Reference Object field. After assigning this access, retry the Compare Contracts page. If the issue persists, contact Salesforce support.
Microsoft 365 Integration Troubleshooting Guide
Tips for troubleshooting issues that may occur when you integrate Microsoft 365 with Salesforce Contracts.
