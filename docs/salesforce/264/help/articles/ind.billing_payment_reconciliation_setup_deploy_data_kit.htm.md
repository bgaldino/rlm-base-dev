---
article_id: ind.billing_payment_reconciliation_setup_deploy_data_kit.htm
title: Deploy the Payment Reconciliation Data Kit
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_deploy_data_kit.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-09-04
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
On the Deploy page, under Connector name, select Payment Reconciliation Ingestion API.
Select the connector twice—once for the Payment Advice Account Reconciliation bundle and once for the Payment Proof Account Reconciliation bundle.
Check the deployment status in the Deployment History tab.
The deployment can take a few minutes. Confirm that the deployment is completed successfully before you run any payment reconciliation.

After the data kit is deployed, you’re ready to run payment reconciliation and review the results.
