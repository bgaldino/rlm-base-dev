---
article_id: ind.billing_payment_reconciliation_setup.htm
title: Set Up Payment Reconciliation
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation.htm
fetched_at: 2026-09-04
---

# Set Up Payment Reconciliation

Set up payment reconciliation by preparing your payment data in Data 360 and deploying the payment reconciliation data kit that Billing uses to match payments against your invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up payment reconciliation and deploy data kits:	

Billing Admin permission set

AND

Data Cloud Architect permission set

Establish Data Connection with Data 360
Billing uses unstructured Data 360 connectors to ingest unstructured data in payment documents such as payment advice documents and payment proof documents.
Process Data by Using Document AI
Use Document AI to extract structured data from the ingested payment advice and payment proof documents. Document AI reads each document and writes the extracted values into an output data lake object (DLO), a structured table whose columns represent the fields that you want to capture. You define one output DLO for payment advice and one for payment proof, and Document AI populates them as it processes your documents. Edit or delete any fields or tables in a DLO as needed.
Create a Custom Batch Data Transform
After Document AI parses your payment advice and payment proof files, convert the numeric and text fields that represent currency and date values into the currency and date data types that payment reconciliation requires.
Create a Vector Search Index
Enhance the searchability of your data by creating a vector search index on the Account object.
Set Up the Ingestion API Schema
Upload and save a JSON-formatted schema to create the output data lake objects (DLOs) for payment reconciliation.
Deploy the Payment Reconciliation Data Kit
The Payment Reconciliation data kit bundles the data model objects, batch data transforms, data actions, and a data action target that reconcile your payments.
