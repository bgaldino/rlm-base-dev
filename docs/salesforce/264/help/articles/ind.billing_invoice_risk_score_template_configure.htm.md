---
article_id: ind.billing_invoice_risk_score_template_configure.htm
title: Configure the Scoring Framework Template (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_score_template_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Configure the Scoring Framework Template (Pilot)

After you configure the scoring framework template, set up the predictive AI model by defining the data space, training data, risk score thresholds, and input features.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create and configure Invoice Risk Scoring:	AI Accelerator User AND Scoring Framework Admin
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
From Setup, in the Quick Find box, find and select Scoring Framework.
Open the Invoice Risk Scoring template.
Select the data space where you want to create the data stream for invoice risk scoring. Select default if you don't have any custom data space.
Select Invoice (STANDARD) as the Data Model Object.

This determines which invoice data the model uses for training and scoring.

Configure Risk Score Thresholds.

The thresholds determine how risk scores are categorized into Low, Medium, and High risk levels.

Set up the medium threshold value. The default value is 0.3.
NOTE Invoices with risk scores less than or equal to this value are classified as low risk. Invoices with risk scores greater than this value are classified as medium or high risk.
Set up the high threshold value. The default value is 0.7.
NOTE Invoices with risk scores greater than this value are classified as high risk. Invoices with risk scores between the medium and high thresholds are classified as medium risk.

For example, with the default thresholds set to Medium: 0.2 and High: 0.8, a risk score of 0.15 is classified as low risk. A risk score of 0.5 is classified as medium risk, while a risk score of 0.85 is classified as high risk.

If needed, configure the filter training and scoring data.
Select at least two fields from predefined fields or invoice custom fields that act as input for your scoring model.

Predefined fields are standard invoice fields optimized for risk prediction. Invoice custom fields are business-specific fields used for risk assessment.

NOTE Input features are invoice attributes used by the AI model to predict payment risk. Select features from predefined and custom fields that are strong indicators of payment behavior in your business, as more relevant features improve prediction accuracy.
If needed, use debug configuration settings to troubleshoot installation issues.

Enable Save Assets to keep successfully installed components if the installation fails. By default, all changes are rolled back if the installation fails.

Review and activate the framework.

The system starts creating the Invoice Risk Scoring app, which includes generating data transforms for training and scoring, training the AI model on historical invoice data, and deploying the model for scoring, with an expected duration of 15–20 minutes. During this process, it automatically runs model training, creates data transforms, and deploys the AI model for scoring readiness.

Verify Installation
From Setup, in the Quick Find box, find and select App Hub.
Check the installation status of your Invoice Risk Scoring app.
View the AI Model
From the Data 360 App Launcher, search for and select AI Models.
Locate and open your Invoice Risk Score model.
Review the model details: training status, model accuracy metrics, input features used, and last training date.
Troubleshooting
From Setup, in the Quick Find box, find and select App Install History.
Locate your Invoice Risk Scoring app installation attempt.
Review the failure details and error messages.
