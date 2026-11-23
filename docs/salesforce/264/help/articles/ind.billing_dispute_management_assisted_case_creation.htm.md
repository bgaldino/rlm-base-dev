---
article_id: ind.billing_dispute_management_assisted_case_creation.htm
title: Raise Service Requests on Behalf of the Customer
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_dispute_management_assisted_case_creation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_manage_disputes.htm
fetched_at: 2026-11-23
---

# Raise Service Requests on Behalf of the Customer

Initiate billing disputes or inquiries on behalf of your customer directly from the Billing app.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To raise service requests on behalf of the customer:	
UnifiedCatalogAgentPsl permission set group
UnifiedCatalogAgent permission set
Omnistudio User permission set
Industry Service Excellence permission set
Billing Operations User permission set
Billing Customer Service User permission set

As a one-time setup task, configure the Action Launcher component to add the Billing service catalog.

In the Billing app, navigate to the customer’s account.
Click New Case on the Account record.
Select the appropriate service process template.
Complete the required fields and any supporting documents or linked invoices.
Submit the case.
A new billing case is created and associated with the customer’s account. Billing also records the intake method as Internal.

When you submit the case, your customer gets an email notification and can view the case details and status on the Cases tab of the self-service Billing portal. You can also route cases to specific service reps by setting up case assignment rules.

You can now proceed to resolve the case using the case resolution workflow.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_dispute_management_assisted_case_creation.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
