---
article_id: ind.billing_invoice_risk_scoring_ai_accelerator_use_case.htm
title: Create Use Case for AI Accelerator (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_ai_accelerator_use_case.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Create Use Case for AI Accelerator (Pilot)

After configuring the Scoring Framework and creating the Copy Field Enrichment, create and configure a machine learning use case in AI Accelerator. The AI Accelerator use case connects the trained Invoice Risk Score model to your Salesforce org so that risk predictions are accessible on invoice records.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To view enrichments in Setup:	View Setup
To create or update enrichments:	Customize Application AND Data Cloud User AND Write Access to Data Action AND Write Access to Data Space Definition
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
From Setup, in the Quick Find box, find and select AI Accelerator.
Click New to create a use case.
Use the more option to edit the use case to configure it.
Select Einstein on Data Cloud as the Prediction Platform.
The Invoice Risk Score model is built and trained in Data 360, so AI Accelerator looks for predictions there.
For Prediction, select Already Generated.
In the Scoring Field section, configure these fields.
	
Predicted Overdue	Predicted Date Invoice Overdue
Risk Level	Invoice Risk Score
These fields are the model outputs that surface on the Invoice record—the predicted overdue date and the High, Medium, or Low risk classification.
For Reference Record Field, select the InvoiceRiskScoringObject and set the field to Invoice ID.
This action links each Data 360 prediction row to the correct Invoice record.
Enter a Prediction Label Template.
A prediction label template is a display string that tells AI Accelerator how to present the prediction result to users on the Invoice record. It typically combines static text with dynamic field values.
In the Use Case Model section, select the Invoice Risk Score model created during Scoring Framework setup.
Save the changes.
