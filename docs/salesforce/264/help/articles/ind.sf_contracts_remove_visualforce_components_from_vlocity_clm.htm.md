---
article_id: ind.sf_contracts_remove_visualforce_components_from_vlocity_clm.htm
title: Remove Visualforce Components from Vlocity Contract Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_remove_visualforce_components_from_vlocity_clm.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_salesforce_contracts_in_vlocity_managed_packages.htm
fetched_at: 2026-11-23
---

# Remove Visualforce Components from Vlocity Contract Lifecycle Management

For Salesforce Contracts to use Lighting Web Components when you generate and maintain contract documents, you must remove the document generation Visualforce component from the Vlocity Contract’s page layout.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

You can use any page layout. Make sure that the ContractDocumentNewDisplay (Scrollbars) Visualforce component is removed.

USER PERMISSIONS NEEDED	 
To remove Visualforce components:	CLM Admin User
From Setup, click Object Manager.
In the Quick Find box, enter contract, and then click Contract.
Click Page Layouts.
Open the page layout that you plan to assign to the contract record type.
For example, Contract (Vlocity 14).
Click Visualforce Pages.
In the Contract Documents section, remove ContractDocumentNewDisplay (Scrollbars).
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_remove_visualforce_components_from_vlocity_clm.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
