---
article_id: ind.billing_invoice_preview_procedure_plan_create.htm
title: Generate Invoice Previews with the Invoice Preview API
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_procedure_plan_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate Invoice Previews with the Invoice Preview API

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Generate Invoice Previews with the Invoice Preview API

To generate preview invoices by using the Invoice Preview API, create and activate a custom procedure plan definition for the object that you want to preview invoices for. The Invoice Preview API uses the procedure plan to generate invoice previews.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create and update custom procedure plan definitions:	Context Service Admin permission set
To generate invoice previews by using the API:	

You must have one of these permission sets:

Billing Admin
Billing Operations User
Billing Customer Service
IMPORTANT

From Summer ’25 and onwards, you will not be able to sync existing context definitions that were either cloned or extended from the standard BillingContext context definition. To fix this issue, use the Context Attribute Mapping API to delete duplicate BSGEntitiesMapping attribute mappings.

BillingTransactionSource attribute of the BillingSchedule node to Reference attribute of the BillingSchedule object.
BillingTransactionItemSource attribute of the BillingSchedule node to the ReferenceItem attribute of the BillingSchedule object.
SEE ALSO
Create a Custom Procedure Plan Definition
Create a Custom Procedure Plan
Create a custom procedure plan definition.
Select Billing as the process type.
Select the object that you want to preview invoices for as the primary object.
Select the extended BillingContext context definition as the context definition.
Update and activate the procedure plan definition.
Open the procedure plan definition and select a read context mapping for the primary object.
Activate the procedure plan definition.
To generate invoice previews for any billing transaction, use the Invoice Preview API.
Preview Invoices for Quotes

To use the standalone Billing Schedules API and Invoice API for quotes, create context definition, a context mapping and a procedure plan.

Extend the BillingContext Context Definition.
Map the Billing Transaction, Billing Transaction Item, Billing Transaction Item Detail, and Billing Transaction Item Relationship nodes and fields to Quote, Quote Line, Quote Line Detail, and Quote Line Relationship objects and fields.
See Add Context Mapping.
Activate the context definition.
Create a custom procedure plan.
To generate invoice previews for quotes, use the Invoice Preview API.
