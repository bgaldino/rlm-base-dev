---
article_id: ind.billing_invoice_risk_scoring_copy_field_enrichment.htm
title: Create a Copy Field Enrichment to Copy Risk Score from Data Model Object (Pilot)
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_risk_scoring_copy_field_enrichment.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_risk_scoring.htm
fetched_at: 2026-09-04
---

# Create a Copy Field Enrichment to Copy Risk Score from Data Model Object (Pilot)

The Invoice Risk Scoring app computes risk scores in Data 360.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To view enrichments in Setup:	View Setup
To create or update enrichments:	Customize Application AND Data Cloud User AND Write Access to Data Action AND Write Access to Data Space Definition
NOTE Invoice Risk Scoring is a pilot or beta service that is subject to the Beta Services Terms at Agreements - Salesforce.com or a written Unified Pilot Agreement if executed by Customer, and applicable terms in the Product Terms Directory. Use of this pilot or beta service is at the Customer's sole discretion.
NOTE If you enabled enhanced security data spaces, you also need the Customize Data Actions on the Dataspace Scope permission.

Create a Data 360 Copy Field Enrichment to copy the risk score from the Invoice Risk Scoring Data Model Object to the risk score field of the Invoice object in your Salesforce org.

From Setup, in the Quick Find box, find and select Copy Field.
On the Data 360 Copy Field Enrichments page, click New.
Configure the copy fields.
Data Space: The data space that you selected during Scoring Framework setup
Data 360 Object: Specify the name created during Invoice Risk Scoring installation. The object follows the naming pattern <AppName> InvoiceRiskScoringObject. For example, if you named the app IRS, the Data Model Object name is IRS InvoiceRiskScoringObject.
Target Object: Invoice
Data 360 Copy Fields: Invoice Risk Level
Map the invoice risk level to the invoice overdue risk indicator field.
Save the changes and start the sync.

After creating the enrichment, start the sync operation to begin copying risk score data from Data 360 to Salesforce Invoice records. The initial sync can take a few minutes depending on the number of invoices. Then, open an invoice record in posted status with a non-zero balance and verify that the risk score and risk level fields are populated.

The copy field enrichment runs on a schedule that aligns with your scoring data transform schedule. If you score invoices daily, schedule the enrichment to run shortly after the scoring completes.
