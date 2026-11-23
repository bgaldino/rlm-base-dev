---
article_id: ind.billing_payment_reconciliation_setup_ingestion_api.htm
title: Set Up the Ingestion API Connector
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_ingestion_api.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-11-23
---

# Set Up the Ingestion API Connector

Upload and save a JSON-formatted schema to create the output data lake objects (DLOs) for payment reconciliation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up Ingestion API connector:	

Billing Admin permission set

AND

Data Cloud Architect permission set

From Setup, in the Quick Find box, enter Data Cloud Setup Home, and then select it.
Navigate to the Connect Other Data Sources section, and under External Integrations, select Ingestion API.
Click New, enter PaymentReconciliation as the connector name, and save it.
On the details page of the connector, upload the schema, and save it.
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
For more information, see Set up Ingestion API connector.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_ingestion_api.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
