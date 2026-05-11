---
article_id: ind.billing_tax_calculation_results.htm
title: Tax Calculation Process
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_calculation_results.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Tax Calculation Process

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Tax Calculation Process

Understand the tax calculation process for invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Billing schedules generated for order products inherit tax treatment from the order products. When invoices are generated from billing schedules, the Calculate Tax API is triggered. This API then uses the tax engine specified for the billing schedules' tax treatment to calculate the applicable taxes. Estimated tax is calculated for draft invoices. Actual tax is calculated for posted invoices.

After the tax is calculated, tax details appear on the Invoice Line Tax records. Several fields, such as the ones that drive the calculation and the status of the calculation process, are updated. This table provides a comprehensive list of fields that are populated during and after the tax calculation.

INVOICE LINE TAX FIELD	DESCRIPTION
Tax Amount	The total tax for the related invoice line. This amount is aggregated to the Tax Amount field of the Invoice Line object, which in turn is aggregated to the Total Tax field on the parent Invoice object.
Tax Code	The tax code is used to calculate the tax rate for the related invoice line.
Tax Document Number	The record in the external tax engine that corresponds to the related invoice line.
Tax Effective Date	The date that’s used to calculate the tax amount.
Tax Exempt Amount	The amount that's exempted from tax.
Tax Name	The name of the applied tax.
Tax Rate	The percentage value that’s used for calculating tax.
Tax Transaction Number	The record in the external tax engine that corresponds to the transaction that's related to the invoice line.
NOTE Use a tax system or a tax vendor that supports certificate management, including certificate validation, compliance with state registrations, lifecycle tracking, and audit trails for tax exemption scenarios. When managing exemption certificates, maintain a matching key between Billing records and the tax system.
For account-level exemptions, use the Account ID as the reference key.
For product-level exemptions, use the Product Code from the Product2 record.

During tax calculation, Billing sends account and product information in the tax request. The tax system uses these identifiers to evaluate and apply the appropriate exemption certificates.

SEE ALSO
Revenue Cloud Developer Guide: Tax Calculation API
