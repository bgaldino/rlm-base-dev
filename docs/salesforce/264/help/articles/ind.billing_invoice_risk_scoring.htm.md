---
article_id: ind.billing_invoice_risk_scoring.htm
title: Set Up Invoice Risk Scoring to Predict Risk Scores for Invoices (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_setup_additional_features.htm
fetched_at: 2026-09-04
---

# Set Up Invoice Risk Scoring to Predict Risk Scores for Invoices (Pilot)

A risk score for an invoice predicts the likelihood that payment for an open invoice is delayed beyond its due date. The score estimates the probability of late payment based on patterns and signals such as historical payment behavior, invoice aging, outstanding balances, customer payment trends, dispute history, and other relevant account characteristics.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.

The risk score helps billing and finance teams identify invoices potentially requiring closer monitoring, and it helps them prioritize collection efforts. A higher risk score indicates a greater likelihood of overdue payments, while a lower score suggests payment is more likely on or before the due date.

By incorporating risk scores into collections workflows, organizations can improve collection efficiency, reduce overdue receivables, and better manage cash flow. For example, organizations can route invoices with higher risk scores to specialized collection plans, assign invoices to collection reps for proactive outreach, or include them in targeted reminder campaigns before the due date. Lower-risk invoices can follow standard collection processes so teams focus their efforts on accounts that require immediate attention.

Get Started with Data 360 for Invoice Risk Score Predictions (Pilot)
Before you install and configure Invoice Risk Scoring, complete the prerequisites.
Add Data Cloud Salesforce Connector Permissions for Invoice Risk Scoring (Pilot)
To ingest invoice objects and fields into Data 360, add the View All Records and Read permissions to the Data Cloud Salesforce Connector permission set in your Salesforce org.
Turn On Legacy AI Model Creation (Pilot)
Legacy AI Model Creation allows the system to create predictive AI models with the appropriate runtime configuration required for invoice risk scoring.
Turn On Predictive Risk Scoring for Invoices (Pilot)
To view the invoice risk scores and levels, turn on predictive risk score for invoices.
Configure Scoring Framework (Pilot)
Use the prebuilt Scoring Framework configuration template type to install and configure the scoring app. This app creates and trains the Predictive AI model to project invoice risk levels.
Configure the Scoring Framework Template (Pilot)
After you configure the scoring framework template, set up the predictive AI model by defining the data space, training data, risk score thresholds, and input features.
Schedule Data Transform for Scoring (Pilot)
After successfully installing the Invoice Risk Scoring app, schedule the data transform to compute risk scores on your latest open invoices.
Create a Copy Field Enrichment to Copy Risk Score from Data Model Object (Pilot)
The Invoice Risk Scoring app computes risk scores in Data 360.
Create Use Case for AI Accelerator (Pilot)
After configuring the Scoring Framework and creating the Copy Field Enrichment, create and configure a machine learning use case in AI Accelerator. The AI Accelerator use case connects the trained Invoice Risk Score model to your Salesforce org so that risk predictions are accessible on invoice records.
