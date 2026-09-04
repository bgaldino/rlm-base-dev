---
article_id: ind.billing_invoice_risk_scoring_connector_permissions.htm
title: Add Data Cloud Salesforce Connector Permissions for Invoice Risk Scoring (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_connector_permissions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Add Data Cloud Salesforce Connector Permissions for Invoice Risk Scoring (Pilot)

To ingest invoice objects and fields into Data 360, add the View All Records and Read permissions to the Data Cloud Salesforce Connector permission set in your Salesforce org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To configure Data Cloud Salesforce Connector permissions:	Data Cloud Admin permission set
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
From Setup, use the Quick Find box to find and select Permission Sets.
Click the required permission set to edit it, then open System Permissions under the App section.
Add the Manage Billing, Manage Billing Access, View All Data, and View All Fields (Global) system permissions for the Data Cloud Salesforce Connector permission set.
NOTE The Data Cloud Salesforce Connector permission set is available only after you connect your Salesforce org to Data Cloud. For deployed orgs that haven't been updated recently, the permission set is listed as Salesforce CDP Salesforce Connector Integration, Customer Data Platform Salesforce Connector Integration, or Customer 360 Audiences Salesforce Connector Integration.
Add the Manage Billing Access system permission to the Customer 360 Data Platform Integration permission set.
Edit the Data Cloud Data Space Management app permission for the Data Cloud Architect permission set to include the required data space.
