---
article_id: ind.collections_setup_risk_scores.htm
title: Set Up Tableau Next App to Predict Risk Scores for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_risk_scores.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-06-21
---

# Set Up Tableau Next App to Predict Risk Scores for Collections and Recovery

A risk score for a collection plan predicts the likelihood of a borrower not repaying their outstanding debt. It helps businesses prioritize and tailor their collection efforts. A higher risk score typically indicates a lower probability of payment, while a lower score suggests a higher likelihood of repayment. Set up Data 360, add Data Cloud Salesforce Connector permissions, install, and configure a Tableau Next app by using the prebuilt Collections Risk Scoring template configuration type in the Scoring Framework setup. Schedule the prebuilt data transform to compute risk scores on latest collection plans. Create a Copy Field Enrichment to copy the risk score from a Data 360 object to the risk score field of the Collection Plan Salesforce object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Enable Financial Account Management Standard Objects for Collections and Recovery
To use the Financial Account and related standard objects, turn on Financial Account Management Standard Objects.
Get Started with Data 360 for Collections Risk Score Predictions
Complete the prerequisites before you install and configure a Tableau Next app that is used to predict risk scores for collections.
Add Data Cloud Salesforce Connector Permissions for Collections Risk Score Predictions
To ingest objects and fields into Data 360, add the View All Records and Read permissions to the Data Cloud Salesforce Connector permission set in your Salesforce org.
Import Collections and Recovery Data into Data 360
You can upload Collections data from your Salesforce Org into Data 360 by creating data streams. Collections Data Kit contains the prebuilt data streams that help you set up data streams.
Install and Configure the Tableau Next App for Collections Risk Score Predictions
Use the prebuilt Scoring Framework configuration template type, Collections Risk Score to install and configure a Tableau Next app. This app creates and trains the Einstein Predictive AI model, which can predict risk scores for collections.
Customize the Training and Scoring Data Transforms Used for Collections Risk Score Predictions
Customize the assets of the Tableau Next app that are created for predicting Collections risk scores according to your business requirements.
Create a Copy Field Enrichment to Copy Risk Score from Data Model Object
To copy risk score data from the Collection Plan Data Model Object to the risk score field in the Collection Plan Salesforce object, create a Copy Field Enrichment.
