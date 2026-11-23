---
article_id: ind.sf_contracts_setup_digital_experience_sites.htm
title: Set Up Digital Experience Sites for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_setup_digital_experience_sites.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-11-23
---

# Set Up Digital Experience Sites for Salesforce Contracts

Configure Experience Cloud sites so that external partners and customers can view contract documents, check e-signature status, and access signed contracts.

Salesforce Contracts supports two types of external user access through Digital Experience sites:

Partner Community Users
Partners can generate and manage contract documents, transition contract states, and submit contracts for e-signature through a Digital Experience site.
Customer Community Plus Users
Customers can view shared contract documents, download signed contracts, review documents in Microsoft 365, and check e-signature status through a Digital Experience site.
Set Up Salesforce Contracts Partner Community User
Perform these tasks to set up the partner user in Salesforce Contracts.
Set Up Salesforce Contracts Customer Community Plus User
Tasks to set up the customer community plus user in Salesforce Contracts.
FLS Requirements for Contract Document Generation
Contract document generation reads and writes fields on several objects during hydration, persistence, and locking. Without Field-Level Security (FLS) on the required fields, generation silently fails or produces incomplete documents. After you set up the community user, grant FLS on the user's profile or on a permission set assigned to them.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_setup_digital_experience_sites.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
