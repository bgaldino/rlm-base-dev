---
article_id: ind.billing_invoice_risk_scoring_schedule_data_transform.htm
title: Schedule Data Transform for Scoring (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_schedule_data_transform.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Schedule Data Transform for Scoring (Pilot)

After successfully installing the Invoice Risk Scoring app, schedule the data transform to compute risk scores on your latest open invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create and configure Invoice Risk Scoring:	AI Accelerator User AND Scoring Framework Admin
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
From the Data 360 App Launcher, search for and select AI Models.
Locate and open your Invoice Risk Score model.
From More options, click Data Transforms.

The Invoice Risk Scoring app creates two data transforms.

Training Data Transform (InvoiceRiskTrainingBDT): Trains the AI model on historical settled invoices
Scoring Data Transform (InvoiceRiskScoringBDT): Scores open invoices with non-zero balance
Click Schedule to configure the schedule.
Save the changes.
