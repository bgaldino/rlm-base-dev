---
page_id: billing_tax_engine_adapter_interface_for_standard_tax.htm
title: TaxEngineAdapter Interface
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_tax_engine_adapter_interface_for_standard_tax.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_reference.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# TaxEngineAdapter Interface

Retrieves and evaluates the details from a tax engine to define tax
        details.

        

You can extend the TaxEngineAdapter interface to define a custom tax adapter based on
            your requirements. Use the custom tax adapter with Billing services to implement
            standard tax.

        

Create a custom object and associated fields to store tax details, such as tax rate for a
            country. For example, create a custom object named CountryTaxRate with Country_Code and
            Tax_Rate fields. Create records to define the details for these fields.

    

- 
**[TaxEngineAdapter Methods](./apex_commercetax_TaxEngineAdapter_methods.htm.md)**  

Learn more about the available methods with the `TaxEngineAdapter` class.

- 
**[TaxEngineAdapter Example Implementation](./billing_apex_interface_TaxEngineAdapter_Example.htm.md)**  

Refer to the example implementation of the `TaxEngineAdapter` interface to accept information from a tax engine and         evaluate the information to define tax details.

- 
**[Tax Mappings for Invoices and Credits](./billing_tax_contract_mappings_for_invoices_and_credits.htm.md)**  

You can extend and customize the existing tax interface by using custom metadata types     and tax mappings. These customizations help you with unique business requirements such as the     inclusion of specific data for accurate calculations and audits.

#### See Also

- [*Salesforce Help*: Tax Calculation for Invoices](https://help.salesforce.com/s/articleView?id=ind.billing_tax_configuration.htm&language=en_US)

- [*Billing Business APIs*: Tax Calculation (POST)](./connect_resources_calculate_taxes.htm.md)

- [*Billing Standard Objects*: TaxEngineProvider, TaxEngine, TaxPolicy, and
       TaxTreatment](./billing_std_objects_parent.htm.md)

- [Tax Engine Reference Gateway Adapter](https://github.com/salesforce-misc/salesforce-tax-engine-reference-gateway-adapters)
