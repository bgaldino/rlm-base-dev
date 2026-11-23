---
article_id: ind.billing_payment_reconciliation_setup_deploy_data_kit.htm
title: Deploy the Payment Reconciliation Data Kit
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_deploy_data_kit.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-11-23
---

# Deploy the Payment Reconciliation Data Kit

The Payment Reconciliation data kit bundles the data model objects, batch data transforms, data actions, and a data action target that reconcile your payments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up payment reconciliation and deploy data kits:	

Billing Admin permission set

AND

Data Cloud Architect permission set

In Data Cloud Setup, click Data Kits, and select Payment Reconciliation.
Deploy the Payment Advice Account Reconciliation and Payment Proof Account Reconciliation bundles.
On the Deploy page, under Connector name, select PaymentReconciliation.
Select the connector twice, first for the Payment Advice Account Reconciliation bundle and then for the Payment Proof Account Reconciliation bundle.
Check the deployment status in the Deployment History tab.
The deployment can take a few minutes. Confirm that the deployment is completed successfully before you run any payment reconciliation.

After the data kit is deployed, you’re ready to run payment reconciliation and review the results.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_deploy_data_kit.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
