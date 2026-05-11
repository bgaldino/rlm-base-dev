---
article_id: ind.billing_invoice_generation.htm
title: Generate Invoices in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_generation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate Invoices in Agentforce Revenue Management

Schedule invoice runs to generate invoices from billing schedules or generate invoices directly from accounts or orders. Create standalone invoices or import invoices from an external system.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Invoice Data Model in Agentforce Revenue Management
The Invoice data model depicts the objects and their relationships to configure billing criteria, billing periods, and payment due dates for generating billing schedules and invoices aligned with your sales models. This data model also depicts integrating with saved payment methods to store customer payment methods, sequence policies to configure automated sequential numbering for your invoices, and email templates to send emails for invoices.
Automated Invoice Generation with Invoice Batch Runs
Schedule invoice batch runs to automate invoice generation. These runs use Data Processing Engine to generate invoices.
Generate Invoices for Accounts or Orders
Generate all the pending invoices of your customers in one go and on-demand. You can also generate consolidated invoices on-demand based on the invoice group type of the related billing schedules.
Create Standalone Invoices or Import External Invoices
Use the Invoice Ingestion API to create standalone invoices by providing the required details to import invoices from an external system. You can also use the API to generate invoices from debit memos.
Manage Invoices by Using APIs or Flow Actions
Use APIs or Flow actions to generate and update invoices, recover the latest generated invoices for billing schedules, void posted invoices, and send emails with posted invoices.
Void Invoices
Simplify invoice corrections by voiding posted invoices directly from the Invoice record.
Generated Invoice Details
View the relationship between invoice lines in invoice line bundles generated for billing schedule group bundles. For amended billing schedules, eliminate manual calculations by automatically generating consolidated invoices. The amounts on invoice lines that are generated for amended, canceled, and renewed assets are matched to the corresponding billing schedule amounts, ensuring accuracy. The invoice lines generated for usage resources contain the consumed quantity and the applied overage charges. The invoice lines generated for orders with quantities in decimals inherit the same quantity and unit of measure.
