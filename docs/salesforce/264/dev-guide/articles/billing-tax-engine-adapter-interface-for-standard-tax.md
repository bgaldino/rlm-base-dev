---
page_id: billing-tax-engine-adapter-interface-for-standard-tax
title: TaxEngineAdapter Interface
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-tax-engine-adapter-interface-for-standard-tax.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-reference
legacy_page_id: billing_tax_engine_adapter_interface_for_standard_tax.htm
fetched_at: 2026-11-25
---

# TaxEngineAdapter Interface

Retrieves and evaluates the details from a tax engine to define tax details.

You can extend the TaxEngineAdapter interface to define a custom tax adapter based on your requirements. Use the custom tax adapter with Billing services to implement standard tax.

Create a custom object and associated fields to store tax details, such as tax rate for a country. For example, create a custom object named CountryTaxRate with Country_Code and Tax_Rate fields. Create records to define the details for these fields.

## Methods

- 

[`processRequest(requestType)`](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_interface_commercetax_TaxEngineAdapter.htm) — The `processRequest` method takes an instance of `TaxEngineContext` class and returns a response with the calculated tax details through the `TaxDetailsResponse` class or an error response through the `ErrorResponse` class.

- 

**[TaxEngineAdapter Example Implementation](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-apex-interface-taxengineadapter-example.html)**

Refer to the example implementation of the `TaxEngineAdapter` interface to accept information from a tax engine and evaluate the information to define tax details.

- 

**[Tax Mappings for Invoices and Credits](./billing-tax-contract-mappings-for-invoices-and-credits.md)**

You can extend and customize the existing tax interface by using custom metadata types and tax mappings. These customizations help you with unique business requirements such as the inclusion of specific data for accurate calculations and audits.

**See Also**

- [*Salesforce Help*: Tax Calculation for Invoices](https://help.salesforce.com/s/articleView?id=ind.billing_tax_configuration.htm)

- [*Billing Business APIs*: Tax Calculation (POST)](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_calculate_taxes.htm)

- [*Billing Standard Objects*: TaxEngineProvider, TaxEngine, TaxPolicy, and TaxTreatment](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_std_objects_parent.htm)

- [Tax Engine Reference Gateway Adapter](https://github.com/salesforce-misc/salesforce-tax-engine-reference-gateway-adapters)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/billing-tax-engine-adapter-interface-for-standard-tax.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
