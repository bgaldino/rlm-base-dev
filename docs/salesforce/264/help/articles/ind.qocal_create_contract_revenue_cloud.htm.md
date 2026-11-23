---
article_id: ind.qocal_create_contract_revenue_cloud.htm
title: Create a Contract and Application Usage Assignment
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_contract_revenue_cloud.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_contract_management_essentials.htm
fetched_at: 2026-11-23
---

# Create a Contract and Application Usage Assignment

Set up a contract to centralize the management of your customers' assets and establish negotiated pricing by assigning a Revenue Cloud lifecycle usage tag.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create contracts:	CreateContract API permission set

Before you begin, establish the base contract details—such as the account name and start date—to streamline the record creation process.

From the App Launcher, find and select Contracts.
Click New and enter the contract details—including account name, start date, and status.
Save your work.
Go to the Related tab.
In the Application Usage Assignments section, click New.
Enter RevenueLifecycleManagement for the Application Usage Type.
Save your changes.
Select the Details tab, edit the Status field, and select Activated.
IMPORTANT Revenue Lifecycle Management (RLM) application usage assignment (AUA) is the only type supported for Revenue Cloud contracts. Operations including amendments, renewals, cancellations, transfers, and swapping of assets require the RLM AUA to use contracts.

After activating your contract, you can link specific products by creating asset contract relationships or begin negotiating rates by managing contract prices and discounts.

Create asset contract relationships
Manage contract prices and discounts

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_contract_revenue_cloud.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
