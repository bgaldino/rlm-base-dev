---
article_id: ind.billing_payment_reconciliation_setup_ingestion_api.htm
title: Set Up the Ingestion API Schema
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_ingestion_api.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-09-04
---

# Set Up the Ingestion API Schema

Upload and save a JSON-formatted schema to create the output data lake objects (DLOs) for payment reconciliation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up Ingestion API connector:	

Billing Admin permission set

AND

Data Cloud Architect permission set

Upload and save this schema. For more information, see Set up Ingestion API connector.
openapi: 3.0.3
info:
  title: Ingestion API Schema
  description: Ingestion API schema for payment reconciliation.
  version: "1.0.0"
paths: {}
components:
  schemas:
    PaymentAdviceAccountRecile:
      type: object
      properties:
        Id:
          type: string
        PaymentAdviceId:
          type: string
        AccountId:
          type: string
        AccountName:
          type: string
        MatchScoreNumber:
          type: number
        PayerName:
          type: string
        AccountReviewStatus:
          type: string
        ReviewedById:
          type: string
        ReviewedDateTime:
          type: string
          format: date-time
        RejectionReasonText:
          type: string
    PaymentProofAccountRecile:
      type: object
      properties:
        Id:
          type: string
        PaymentProofId:
          type: string
        AccountId:
          type: string
        AccountName:
          type: string
        MatchScoreNumber:
          type: number
        PayerName:
          type: string
        AccountReviewStatus:
          type: string
        ReviewedById:
          type: string
        ReviewedDateTime:
          type: string
          format: date-time
        RejectionReasonText:
          type: string
