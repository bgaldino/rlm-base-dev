---
article_id: ind.billing_tax_lines_import.htm
title: Import External Tax Lines into Billing
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_lines_import.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Import External Tax Lines into Billing

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Import External Tax Lines into Billing

Bring in the tax amounts calculated by an external system for draft invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To export and import Invoice Line Tax records:	Billing Admin OR Billing Operations User permission set
Create draft invoices for order products having Is Taxable set to false on tax treatments.
See Create Tax Policies and Treatments and Generate Invoices in Agentforce Revenue Management.
Use a data extraction tool to export the required Invoice Line fields.
The external tax system uses this data to calculate taxes.
Import the calculated Invoice Line Tax records into Billing.
The external tax system must provide a CSV file that includes the mandatory fields such as TaxTransactionNumber, TaxAmount, TaxRate, TaxName, TaxCode, TaxEffectiveDate, InvoiceLine, TaxDocumentNumber, TaxExemptAmount, and TaxProcessingStatus. The TaxProcessingStatus field in your import CSV file must be set to Posted. See Prepare a CSV File for Import.
Verify that the imported invoice line taxes are associated with the correct invoice lines.
You can modify or delete the imported invoice line taxes before posting the invoice.
Post the corresponding invoices.
EXAMPLE

Here's a sample CSV file for invoice line tax. Make sure to include the mandatory fields along with any additional fields you need.

INVOICELINEID	LEGALENTITYID	TAXAMOUNT	TAXCODE	TAXDOCUMENTNUMBER	TAXEXEMPTAMOUNT	TAXNAME	STARTDATE	ENDDATE
5TVSG0000007l0b4AA	0fwSG000000TwwfYAC	50	PA020111	3ttDU00000002Fr_Debit-4wADU0000002aH22AI	0	T1234	2025-03-21	2025-03-31
5TVSG0000007l0c4AA	0fwSG000000TwwfYAC	30	PA020111	3ttDU00000002Fr_Debit-4wADU0000002aH22AI	0	T1234	2025-03-21	2025-03-31
