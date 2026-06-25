---
article_id: ind.collections_editions_permissions.htm
title: Editions and Permissions for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_editions_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections.htm
fetched_at: 2026-06-21
---

# Editions and Permissions for Collections and Recovery

Review the supported products, editions, and permissions for Collections. Then learn how your product handles permissions and how to assign them.

REQUIRED EDITIONS
User Interface

Collections and Recovery is available in Lightning Experience.

Editions
Available in: Lightning Experience
Financial Services Cloud: Enterprise, and Unlimited Editions
Automotive Cloud: Enterprise, Unlimited, and Developer Editions
Collections Permissions

To set up and use Collections, Salesforce admins and users need these permission sets. Typically, a Salesforce admin assigns these permission sets.

PERMISSION SET NAME	DESCRIPTION
Collections and Recovery Admin	Set up and manage Collections
Collections and Recovery Specialist	Create promise to pay records, view collection plan details, update the status of collections, generate and send payment links, and view and edit the source of cases created for collection plans
Collections and Recovery for European Union Operating Zone Admin	Gives European Union Operating Zone admins the required permissions to set up and manage collections
Collections and Recovery for European Union Operating Zone Specialist	Gives European Union Operating Zone users access to create promise to pay records, view collection plan details, update the status of collections, generate and send payment links, and view and edit the source of cases created for collection plans
Industry Service Excellence	
Configure Action Launcher Deployment
Enable Timeline

Industry Sales Excellence OR Industry Service Excellence	Access Financial Account and related Standard Objects
Basic CSV Data Import	Import CSV data into a single Salesforce object
CSV Advanced Data Import	Import CSV data into multiple Salesforce objects simultaneously
Omnistudio User	Access and view the information shown in Omnistudio components configured in the Collections console app, such as Omniscripts and Flexcards
Additional Permissions

Salesforce admins need these permission sets to set up additional Collections features.

PERMISSION SET NAME	DESCRIPTION
Omnistudio Admin	Customize the Omnistudio components configured in the Collections console app, such as Omniscripts and Flexcards.
Context Service Admin	
Turn on Context Definition
Clone and customize context definitions

Rule Engine Designer	
Turn on Industries Cloud Common Decision Tables Access
Create, update, and delete decision matrices and matrix versions

Rule Engine Runtime	Use decision matrices in Business Rules Engine
Actionable Event Orchestration Designer	
Turn on Actionable Event Orchestration
Clone and customize the expression set template
Create an actionable event orchestration

Actionable Event Orchestration Runtime	Run an actionable event orchestration
Actionable Segmentation	
Create and activate actionable list definitions and actionable lists
Create and configure actionable lists

Data Pipelines Base User	
Create and activate actionable list definitions and actionable lists
Create and configure actionable lists
Refresh datasets periodically by using flows

Query for Data Pipelines	Create and activate actionable list definitions and actionable lists


Financial Services Cloud Extension OR FSC Foundation OR FSC Service OR FSC Sales

	Access Financial Account and related standard objects
MuleSoft Administrator	Access MuleSoft Direct Integrations
Data Cloud Admin AND Marketing Cloud Admin	Configure automatic payment status notifications
Data Cloud Admin AND Marketing Cloud Admin	To create and manage collection campaigns
Industries Visit	To create and manage customer visit records on the Collections and Recovery portal
Data Cloud Admin	To create a custom data space
Data Cloud Admin	To configure Data 360 Salesforce Connector permissions
Data Cloud Admin	To create data streams
Data Cloud Admin	To customize the Tableau Next app assets
Data Cloud Architect	To access Data 360 Setup
Payments Admnistrator	To set up Salesforce Pay Now
AI Accelerator User AND Einstein for Financial Services	To create and configure Tableau Next app
Customizing Permissions

You can customize this feature, for instance, by adding fields and creating a custom permission set. To remove user permissions from the default permission set, create a muting permission set. Then, use permission set groups to assign users the default permission set in addition to your custom permission sets. This approach ensures users always have the latest default permissions, and is an alternative to cloning permission sets.

SEE ALSO
Salesforce Help:Manage Permission Set Assignments
