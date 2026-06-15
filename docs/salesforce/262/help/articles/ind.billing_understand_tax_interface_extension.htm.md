---
article_id: ind.billing_understand_tax_interface_extension.htm
title: Tax Interface Extension
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_understand_tax_interface_extension.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Tax Interface Extension

Handle tax calculation needs that go beyond standard integrations, capture the right data for audits, and adapt to new requirements through configuration instead of custom code.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Why Do You Need Extended Tax Callout?

Extend your tax callout to solve some of these common challenges with the existing tax interface.

Your third-party tax provider requires specific data for accurate calculations that isn't included in the standard tax request. For example, a customer's tax identification number or a product's material type.
You want to capture and store detailed information from the tax provider's response for auditing, reporting, or customer-facing documents. For example, you want to save a specific tax jurisdiction code or an exemption reason on an invoice line.
Your business needs to adapt to changing tax regulations or expand into new regions that have unique data requirements, and you want to avoid custom code development.
How Extended Tax Interface Works

Salesforce uses these features to extend the existing tax interface.

Custom Metadata Type and Mappings: This acts as the central blueprint for your customizations to extend the existing tax interface. You create one main custom metadata type to hold all your mapping definitions. Within your custom metadata type, you create individual records for each custom field you want to add. Each mapping record tells the system which Salesforce field to use, what to name the field in the API call, and whether it's part of the request, the response, or both. See Custom Metadata Types.
Tax Engine Provider: This is your configured connection to your tax provider. You associate your custom metadata type directly to your tax engine provider. The system extends the tax interface by using the field mappings from the custom metadata type. See Configure a Tax Engine.
Tax Engine Adapter: The Apex adapter for your tax engine must be able to process the incoming custom fields in the request and add the custom fields to the response. See Tax Engine Adapter.
