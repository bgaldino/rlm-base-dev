---
article_id: ind.billing_payment_reconciliation_setup_document_ai.htm
title: Process Data by Using Document AI
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_payment_reconciliation_setup_document_ai.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payment_reconciliation_setup.htm
fetched_at: 2026-09-04
---

# Process Data by Using Document AI

Use Document AI to extract structured data from the ingested payment advice and payment proof documents. Document AI reads each document and writes the extracted values into an output data lake object (DLO), a structured table whose columns represent the fields that you want to capture. You define one output DLO for payment advice and one for payment proof, and Document AI populates them as it processes your documents. Edit or delete any fields or tables in a DLO as needed.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To process data by using Document AI:	

Data Cloud Architect permission set

To configure these output DLOs, complete both procedures, first for payment advice, then for payment proof. For more information, see Document AI and Create a Document Schema Configuration Manually.

Configure Output DLOs for Payment Advice
In the Data 360 app, click Process Content | Document AI | New.
Select the payment advice UDMO as the source object.
Select PDF and Image as the file types available for configuring the document schema.
In DLO configuration, create two tables with columns that represent the payment-level and invoice-level details from the payment advice document.
Payment Advice Output DLO Columns
PAYMENT-LEVEL DETAILS ON PAYMENT ADVICE	INVOICE-LEVEL DETAILS ON PAYMENT ADVICE
Payment Advice Id	Payment Advice Line Invoice Id
Payer Name	Payment Advice
Payment Amount	Invoice Number
Payment Date	Applied Amount
Reference Number	Gross Amount
Source Document	Deduction Amount
Transaction Description	Deduction Code
Payment Method	Created Date Time
Processing Status	Last Modified Date Time
Account	Invoice
View and publish your document schema.
Open the output DLOs to check the field-level mappings, and rebuild the schema if required.
Use the Query Editor to view the records.
Configure Output DLO for Payment Proof
In the Data 360 app, click Process Content | Document AI | New.
Select the payment proof UDMO as the source object.
Select PDF and Image as the file types available for configuring the document schema.
In DLO configuration, create a table with columns that represent the payment proof details from the payment proof document.
Payment Proof Output DLO Columns
DETAILS ON PAYMENT PROOF
Payment Proof Id
Transaction Reference Number
Payer Name
Payment Amount
Booking Date
Value Date
Statement Date
Source Document Name
Source Document URL
Credit Debit Indicator
Payment Description
Processing Status
Created Date Time
Last Modified Date Time
Proof Type
Account
View and publish your document schema.
Open the output DLO to check the field-level mappings, and rebuild the schema if required.
Use the Query Editor to view the records.
HOW DOCUMENT AI STRUCTURES A PAYMENT

Consider a single payment from Acme Corp. Acme sends a remittance advice (a type of payment advice) to pay two open invoices with one $10,000 ACH payment, and Acme’s bank issues a statement that confirms the deposit. Document AI extracts data from both documents into their output DLOs. Because the two documents describe the payment differently, their schemas differ too.

Because one payment advice can pay several invoices, the payment advice output DLO uses two related tables: one for the payment-level details and one for the invoice-level records.

Sample payment advice

Payment Advice Extraction
PAYMENT ADVICE DETAILS	CONFIGURATION OF THE OUTPUT DLO
Payer Acme Corp, a $10,000 ACH payment dated March 15, 2026, with reference number ACME-RA-20260315.	One record in the payment-level table: Payer Name, Payment Amount, Payment Date, Reference Number, and Payment Method.
Invoice INV-1001, with $6,000 applied and no deduction.	One record in the invoice-level table: Payment Advice Invoice Number, Applied Amount, and Gross Amount.
Invoice INV-1002, with $4,000 applied against a $4,200 gross amount and a $200 early-payment deduction (code EARLYPAY).	A second record in the invoice-level table, including Deduction Amount and Deduction Code.

A payment proof confirms a single payment that the bank received, so its output DLO uses one table, with one record per confirmed transaction.

Sample payment proof

Payment Proof Extraction
PAYMENT PROOF DETAILS	CONFIGURATION OF THE OUTPUT DLO
An incoming credit from Acme Corp for $10,000.	Payer Name, Payment Amount, and Credit Debit Indicator.
Transaction reference TXN-88231, described as ACH CREDIT ACME CORP.	Transaction Reference Number and Payment Description.
A booking date and value date of March 18, 2026, on a statement dated March 31, 2026.	Booking Date, Value Date, and Statement Date.
The source file AcmeBank_Statement_Mar2026.pdf.	Source Document Name and Source Document URL.

Together, these two output DLOs give payment reconciliation the structured data that it needs to later match Acme’s payment advice against the bank’s payment proof and the open invoices.
