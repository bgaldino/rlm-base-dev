---
article_id: ind.collections_risk_score_assign_connector_permissions.htm
title: Add Data Cloud Salesforce Connector Permissions for Collections Risk Score Predictions
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_risk_score_assign_connector_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_risk_scores.htm
fetched_at: 2026-06-21
---

# Add Data Cloud Salesforce Connector Permissions for Collections Risk Score Predictions

To ingest objects and fields into Data 360, add the View All Records and Read permissions to the Data Cloud Salesforce Connector permission set in your Salesforce org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To configure Data Cloud Salesforce Connector permissions:	Data Cloud Admin
From Setup, in the Quick Find box, enter Permission Sets, and then select Permission Sets.
Select the Data Cloud Salesforce Connector permission set.
The Data Cloud Salesforce Connector permission set is available only after you connect your org to Data 360. For deployed orgs that weren’t updated recently, the permission set is listed as Salesforce CDP Salesforce Connector Integration, Customer Data Platform Salesforce Connector Integration, or Customer 360 Audiences Salesforce Connector Integration.
From Apps, select Object Settings.
Select the object that you want to ingest into Data 360.
To change the object permissions, click Edit.
Enable the Read and View All Records permissions for these objects.
OBJECT NAME
Account
Contact
Collection Plan
Collection Plan Item
Collection Plan Reason
Financial Account
Financial Account Party
Party Financial Asset
Financial Account Balance
To enable the Set up and manage collections, and Manage Financial Services Standard Objects system permissions in the Data Cloud Salesforce Connector permission set, follow these steps:
From Setup, in the Quick Find box, enter Permission Sets, and then select Permission Sets.
Select the Data Cloud Salesforce Connector permission set.
The Data Cloud Salesforce Connector permission set is available only after you connect your org to Data 360. For deployed orgs that weren’t updated recently, the permission set is listed as Salesforce CDP Salesforce Connector Integration, Customer Data Platform Salesforce Connector Integration, or Customer 360 Audiences Salesforce Connector Integration.
From Apps, select System Permissions.
Enable Set up and manage collections, and Manage Financial Services Standard Objects system permissions.
