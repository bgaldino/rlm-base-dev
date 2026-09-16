---
article_id: ind.billing_configure_dunning_orchestration.htm
title: Orchestrate Your Dunning Strategy for Collections
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_configure_dunning_orchestration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_collections.htm
fetched_at: 2026-09-04
---

# Orchestrate Your Dunning Strategy for Collections

Automate the entire dunning journey—from sending email reminders to manual recovery on payment collections—by using the out-of-the-box Dynamic Revenue Orchestrator (DRO) templates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To initiate dunning orchestration:	

Billing Operations User permission set

OR

Billing Collections and Recovery Specialist permission set

How Dunning Orchestration Works

The dunning orchestration feature in Billing uses the Dynamic Revenue Orchestrator framework to manage and automate the dunning lifecycle. The orchestration plan that’s shipped out of the box, drives a structured sequence of reminders and escalations based on collection plan’s due dates and customer risk profiles.

When you set up dunning orchestration solution and turn on Automate Dunning Orchestration on the Billing Settings page, these components are installed in your Salesforce org.

Collections Dunning Orchestration Workspace: A DRO fulfillment workspace that contains the step definitions and step definition groups that define the dunning sequence. The fulfillment workspace includes two fulfillment scenarios that categorize accounts based on the risk score of the collection plan. The Fulfillment Workspace object includes these objects:Fulfillment Workspace Item, Fulfillment Scenario, Fulfillment Step Definition Group, Fulfillment Step Definition, and Fulfillment Step Dependency Definition.
BillingOrchPlanCtxMapping context mapping: The orchestration plan context mapping that maps the DRO engine to the BillingCollectionPlanContext standard context definition. It also enables the orchestration framework to access collection plan data and trigger automated workflows.
Email Templates: Early Reminder, Invoice Due Notice, and Suspension Notice. The dunning workflow uses these three email formats to send email reminders and notices to customers.

Your Salesforce org also includes an out-of-the-box screen flow named Orchestrate Dunning Reminders. The screen flow includes the Send Dunning Email invocable action that, when invoked, sends reminder and notice emails for upcoming and overdue invoices.

Billing Dunning Orchestration Workflow

The dunning orchestration follows a milestone-driven sequence where each fulfillment scenario contains milestones and automated tasks with step dependencies that control the timing and sequencing of actions. Before triggering the next action, each step waits for a specific date or day count, depending on the collection plan’s due date. The fulfillment scenarios are based on the collection plan’s risk score—Low, Medium, or High—populated in the Overdue Risk Indicator field of the Collection Plan record.

Low and Medium Risk Accounts: This orchestration sequence applies to collection plans with a Low or Medium risk score. The orchestration follows a gradual escalation path.
High Risk Accounts: This orchestration sequence applies to collection plans with a High risk score. The orchestration starts earlier and escalates faster.

For low and medium risk accounts, here’s the dunning orchestration sequence.

STEP	TIMING	ACTION
1	5 days before the collection plan due date	Early Reminder email: a friendly email to the customer with a list of all invoices, balances, and due dates
2	On the collection plan due date	Invoice Due Notice email: an email notice to the customer with a list of all unsettled or partially settled invoices, and total balance
3	7 days after the collection plan due date	Suspension Notice email: a suspension notice to the customer with details of all unsettled invoices and total balance
4	10 days after the collection plan due date	Call the customer and initiate manual recovery of payments.

For high risk accounts, here’s the dunning orchestration sequence.

STEP	TIMING	ACTION
1	10 days before the collection plan due date	Early Reminder email: a friendly email to the customer with a list of all invoices, balances, and due dates
2	5 days before the collection plan due date	Early Reminder email: a friendly email again to the customer with a list of all invoices, balances, and due dates
3	On the collection plan due date	Invoice Due Notice email: an email notice to the customer with a list of all unsettled or partially settled invoices, and total balance
4	3 days after the collection plan due date	Suspension Notice email: a suspension notice to the customer with details of all unsettled invoices and total balance
5	4 days after the collection plan due date	Call the customer and initiate manual recovery of payments.

The dunning orchestration is based on the collection plan’s due date, not individual invoice due dates. This means that your collections team can send a single, coordinated set of reminders per collection plan, including all associated invoices in each email. Also, all email reminders are sent at the collection plan level. If a collection plan has multiple invoices, each reminder email includes the invoice details, balance, and due date for all associated invoices.

Collection Plan Context Definition and Context Mapping

The BillingCollectionPlanContext is a standard Billing context definition that includes fields from the CollectionPlan object and its related CollectionPlanItem and Invoice objects. The dunning orchestration workflow uses the context definition to retrieve and process collection plan information. You can extend the context definition to add custom fields and attributes based on your business requirements.

Customize the Dunning Orchestration Workflow

You can customize the dunning orchestration workflow to suit your business needs and match your customer segments, to build a more effective dunning strategy.

Timing of the automated steps: Initiate tasks and reminders on specific days before or after the collection plan’s due date. The out-of-the-box workflow sends the email reminder 5 days before the due date, but you can adjust the timelines to suit your needs.
Email templates: Modify the email templates to match your messaging and branding needs.
Step definitions and sequences: Modify the step definitions, such as changing the actions or adding new steps to suit your dunning strategy.
Orchestration paths: Customize the timing and actions within each orchestration path to reflect your own escalation threshold and manual recovery process.
Execution profiles: Configure the execution rules in the fulfillment scenario to create new rules or update the existing rules and conditions with custom rules and logic. See Configure a Fulfillment Scenario, Define Conditions for a Fulfillment Step to Run, and Understand Execution Conditions for Order Fulfillment for more information.
Set Up Orchestrated Dunning for Collections
Configure and integrate out-of-the-box Dynamic Revenue Orchestrator templates into Billing to automate the entire dunning lifecycle.
Initiate and Monitor Dunning Orchestration
With the dunning orchestration solution set up and enabled on the Billing Settings page, you can initiate automated dunning on your collection plans.
