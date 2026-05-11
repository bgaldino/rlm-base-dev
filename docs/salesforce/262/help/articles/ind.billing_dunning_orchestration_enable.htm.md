---
article_id: ind.billing_dunning_orchestration_enable.htm
title: Set Up Orchestrated Dunning for Collections
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_dunning_orchestration_enable.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Set Up Orchestrated Dunning for Collections

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Set Up Orchestrated Dunning for Collections

Configure and integrate out-of-the-box Dynamic Revenue Orchestrator templates into Billing to automate the entire dunning lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To install and configure the Dynamic Revenue Orchestrator feature and the Dunning Orchestration solution by using Salesforce Go:	Billing Admin permission set
Configure the Dynamic Revenue Orchestrator feature in Salesforce Go. Skip this step if it’s already configured.
From Setup, in the Quick Find box, enter Salesforce Go, and then select Salesforce Go.
Go to the Features tab and filter by Revenue Cloud to view and set up Dynamic Revenue Orchestrator.
Turn on Dynamic Revenue Orchestrator, and then in the Unlock Advanced Functionality section, turn on Future-Dated Steps to configure steps to execute at a future date and time.
To monitor the installation status, in Setup, find and select Jobs, and then click Bulk Data Load Jobs.
The setup can take a few minutes. We recommend that you wait until the configuration is complete before you proceed further.
In Setup, find and select Billing Settings, and then turn on Automate Dunning Orchestration.
This action creates the BillingOrchPlanCtxMapping orchestration plan context mapping record with orchestration type as Billing. The context mapping corresponds to the BillingCollectionPlanContext context definition and maps to the CollectionPlan object.
Install the Dunning Orchestration solution in Salesforce Go.
From Setup, in the Quick Find box, enter Salesforce Go, and then select Salesforce Go.
Go to the Initial Setup tab and filter by Revenue Cloud and Data Pack category.
View and install Dunning Orchestration Solution.
This step can take a few minutes.
The solution installs a dunning orchestration fulfillment workspace and three email templates. For more information, see Configure Dunning Orchestration.

Your Billing Operations User or Collections and Recovery Specialist is now ready to initiate dunning orchestration on your collection plans.

NOTE After it’s installed, you can’t uninstall the Salesforce Go solutions.
SEE ALSO
Turn on Future-Dated Steps
