---
article_id: ind.billing_invoice_risk_scoring_features_overview.htm
title: Overview of Features and Assets of Invoice Risk Scoring (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_features_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_score.htm
fetched_at: 2026-09-04
---

# Overview of Features and Assets of Invoice Risk Scoring (Pilot)

Review key input features and assets involved in the installation and configuration of Invoice Risk Scoring via the Scoring Framework configuration template type.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
Standard Invoice Fields

The Invoice Risk Scoring template includes predefined invoice fields that are used to train and score the predictive AI model.

FIELD	DESCRIPTION
Billing Account	Account associated with the invoice
Total Amount	Total invoice amount
Payment Term Item Period	Payment term duration (for example, Net 30 = 30 days)
Net Credit Memo Applied Amount	Net credit memo amount applied to the invoice
Net Credit Applied Amount	Net credits applied to the invoice
Settlement Date	Actual or expected settlement date
Posted Date	Invoice posted date
Due Date	Invoice due date
Derived Days Invoice Overdue	Calculated overdue days based on settlement status
NOTE The model uses only invoice header-level fields. Invoice line-level fields aren't included in scoring.
Predefined Fields

Created specifically for this model, these fields are useful for score predictions.

FIELD	DESCRIPTION
Account Annual Revenue	Annual revenue of the billing account
Account Primary Industry	Industry classification of the account
Net Credits to Invoice Amount Ratio	Ratio of credits applied to invoice amount
Net Payments to Invoice Amount Ratio	Ratio of payments applied to invoice amount
Invoice Amount to Account Revenue Ratio	Ratio of invoice amount to annual revenue
Account Average Days Overdue	Historical average overdue days for the account
Invoice Overdue	Indicates whether the invoice is overdue
NOTE Dynamic fields such as Days Invoice Overdue and Days Invoice Open aren't used directly because they change daily for open invoices. Instead, the model uses Derived Days Invoice Overdue for consistent scoring.
Risk Score Calculation

The risk score is calculated by using invoice due dates, posted dates, and AI predicted days overdue of the invoice values.

Invoices already overdue or with invalid date ranges receive a fixed score of 0.99.
Predicted late payments can produce scores greater than 1.0, which are treated as high risk.
Default Risk Level Thresholds
RISK LEVEL	THRESHOLD
Low	≤ 0.3
Medium	> 0.3 and ≤ 0.7
High	> 0.7 or ≥ 0.99
AI Explainability

Each score includes explainability details showing:

The top 3 factors influencing the score
Impact value of each factor
