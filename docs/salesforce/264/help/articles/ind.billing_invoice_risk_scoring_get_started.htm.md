---
article_id: ind.billing_invoice_risk_scoring_get_started.htm
title: Get Started with Data 360 for Invoice Risk Score Predictions (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_get_started.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Get Started with Data 360 for Invoice Risk Score Predictions (Pilot)

Before you install and configure Invoice Risk Scoring, complete the prerequisites.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To access Data 360 setup:	Data Cloud Architect permission set
To create a custom data space:	Data Cloud Admin permission set
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
Turn on Data 360.

Data 360 is automatically provisioned when a Data 360 license is added to your Salesforce org. However, if auto provisioning isn't available or if you're working in a Developer Edition or sandbox org, you manually enable it. Data 360 can be enabled on a new or an existing Salesforce org.

Create a custom data space so that all the relevant Data 360 objects related to risk score data can be mapped to it.
Creating a custom data space is optional. To segregate your brand, region, or department data and services, create a custom data space. If you don't create a custom data space, all Data 360 objects are mapped to the default data space.
Deploy the Advanced Billing Bundle Data Kit and Common Billing Bundle Data Kit to Data 360 before configuring Invoice Risk Scoring.
From the App Launcher, find and select Data 360.
On the Data Streams tab, click New.
Select Salesforce CRM as the connected source, and then click Next.
In the Standard Data Bundles section, select Advanced Billing Bundle Data Kit and deploy it. Then select and deploy Common Billing Bundle Data Kit
Review the data fields and click Next.
Click Deploy.
If you have data in Data 360 in other orgs, you can import that data by setting up a CRM Salesforce Org connection.
