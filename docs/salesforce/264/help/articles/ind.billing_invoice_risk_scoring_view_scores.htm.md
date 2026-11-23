---
article_id: ind.billing_invoice_risk_scoring_view_scores.htm
title: View Invoice Risk Scores (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_view_scores.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_score.htm
fetched_at: 2026-11-23
---

# View Invoice Risk Scores (Pilot)

After configuring Invoice Risk Scoring, you can view the predicted risk scores and risk levels on invoice records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To view invoice risk scores:	

Billing Admin permission set

AND

Billing Operations User permission set

NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.

Use the AI Accelerator Card component to view risk scores on invoice records. After your Billing Admin adds the component to the Invoice record page in the Lightning App Builder, select the use case definition and model name, and then set the threshold score to 0.

Invoice includes two fields for displaying risk score predictions.

Risk Score: A numeric value representing the likelihood of delayed or non-payment. Higher scores indicate greater risk.
Risk Level: A text value that categorizes the risk as Low, Medium, or High. The thresholds that you configured during setup determine the risk level.
From the App Launcher, find and select Invoices.
Open the invoice record that you want to review.
Review the risk score information displayed for the invoice record.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_view_scores.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
