---
article_id: ind.sf_contracts_salesforce_contracts_troubleshooting_guide.htm
title: Salesforce Contracts Troubleshooting Reference
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_salesforce_contracts_troubleshooting_guide.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
fetched_at: 2026-11-23
---

# Salesforce Contracts Troubleshooting Reference

Tips for troubleshooting user access and permissions related to Salesforce Contracts.

ISSUE	WHAT IT MEANS	HOW TO FIX IT
The Compare Contracts window keeps loading continuously for a non-admin user.	The non-admin user's custom profile or permission set doesn't have the required access to the Generated Documents object or the Reference Object field. This issue occurs when a custom profile or permission set is used instead of the out-of-the-box standard profile or permission set.	In the non-admin user's profile or permission set, grant Read access to the Generated Documents object and Read access to the Reference Object field. After assigning this access, retry the Compare Contracts page. If the issue persists, contact Salesforce support.
The error "Document was not generated. Retry generating the document or cancel the document check out." appears when a user tries to generate a contract document.	The user has the Query Non Vetoed Files app permission enabled. This permission blocks contract document generation.	Remove the Query Non Vetoed Files permission from each permission set, permission set group, or profile that grants it to the user. To find these, from Setup open the user's record page, and click View Summary. Search for Query Non Vetoed Files and use Access Granted By drop down to find each permission set, permission set group, or profile that grants it. Disable the Query Non Vetoed Files permission and then retry generating the document. See knowledge article Understanding the "Query Non Vetoed Files" Permission and Salesforce File Access Issues.
Microsoft 365 Integration Troubleshooting Guide
Tips for troubleshooting issues that may occur when you integrate Microsoft 365 with Salesforce Contracts.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_salesforce_contracts_troubleshooting_guide.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
