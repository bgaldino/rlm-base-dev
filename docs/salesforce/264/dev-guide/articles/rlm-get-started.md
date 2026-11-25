---
page_id: rlm-get-started
title: Get Started with Revenue Management Developer Resources
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/rlm-get-started.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Get Started with Revenue Management Developer Resources
legacy_page_id: rlm_get_started.htm
fetched_at: 2026-11-25
---

# Get Started with Revenue Management Developer Resources

Get a single, unified system to automate your CRM processes. Use the developer sources of Revenue Management to automate the backend work to support the end-to-end revenue solution.

Revenue Cloud is now Revenue Management. You may see references to Revenue Cloud in our application and documentation.

| Required Editions |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Unlimited**, and **Developer** Editions |

Revenue Management provides extensible and API-first business components of the product-to-cash processes. Learn more about the developer resources that are available for these components.

## Product Catalog Management

Create and manage an entire product portfolio with components such as attributes, product classifications, simple and bundled products, and rules.

- Use [standard objects](./pcm-std-objects-parent.md) and fields to manage products, rules, and catalogs.

- Use [business APIs](./product-catalog-management-business-api.md) to serve catalog definitions to users or applications.

- Use [metadata API](./pcm-metadata-api-parent.md) types to access and manage the metadata types, such as product specification type and product specification record types.

- Use [tooling API](./pcm-tooling-api-parent.md) objects to retrieve and manage smaller pieces of metadata types through SOQL capabilities. Use REST or SOAP to access metadata.

- Use [Product Discovery business APIs](./product-discovery-business-apis.md), which are composite APIs, to search products or to discover catalogs, products, and categories.

## Salesforce Pricing

Create a reliable pricing solution for your users through customized price adjustment schedules. Get accurate pricing for your entire product portfolio.

- Use [standard objects](./pricing-std-objects-parent.md) and fields to manage pricing processes such as product management, and the calculation and application of discounts.

- Use [business APIs](./pricing-business-apis.md) to get unified pricing experiences across product lines.

- Use [invocable actions](./pricing-invocable-actions-parent.md) to invoke the pricing Connect API by providing the pricing, context, and price waterfall details.

- Use [metadata API](./pricing-metadata-api-parent.md) types to work with the metadata associated with Flows and Salesforce Pricing settings.

- Use [tooling API](./pricing-tooling-api-parent.md) objects to retrieve and manage smaller pieces of metadata types through SOQL capabilities such as pricing action parameters, pricing procedure output map, and pricing recipe details. Use REST or SOAP to access metadata.

## Product Configurator

Customize the components and attributes of a product to meet the business requirement expectations.

- Use [standard objects](./prod-config-std-objects-parent.md) to manage product-related information.

- Use the [business APIs](./product-configurator-business-api-overview.md) to retrieve and update a product’s configuration from a configurator or to access configurator capabilities by integrating with any front-end application.

- Use [constraint modeling language](./cml-what-is-constraint-modeling-language.md) to enforce business logic declaratively, without the need for extensive code in a general-purpose programming language.

## Transaction Management

Manage subscription lifecycles from quotes and orders to contracts, assets, amendments, and renewals. Get insights into customer assets and see a consolidated list of all assets that belong to an account.

- Use [standard objects](./quote-and-order-capture-standard-objects.md) and fields to manage transactions and details of a customer asset. Use the QuoteSaveEvent [platform event](./quote-and-order-capture-platform-event.md) to notify subscribers after saving of a quote is processed.

- Use [business APIs](./qoc-business-apis.md) to place, clone, or supplement a sales transaction. You can also initiate amendment, renewal, or cancellation of assets by using APIs.

- Use [invocable actions](./qoc-invocable-actions-parent.md) to create and activate an order from a quote, or to initiate amendment, renewal, or cancellation of assets through invocable actions.

- Use [metadata API](./qoc-metadata-api-parent.md) types to work with the metadata associated with Flows.

- Use built-in [Apex classes and interfaces](./qoc-apex-reference.md) grouped by namespace.

## Usage Management

Ensure transparent, accurate, and efficient management of usage data and estimated usage amount.

- Use [standard objects](./usage-management-std-objects-parent.md) and fields to set up and manage consumption of usage-based products.

- Use [metadata API](./usage-management-metadata-api-parent.md) types to work with the metadata associated with Usage Management.

- Use [business APIs](./usage-management-business-apis.md) to get details of a usage-based product that’s associated with an asset, an order item, or a quote line item.

- Use [invocable actions](./usage-management-invocable-actions-parent.md) to invoke usage summaries, process consumption overages, and refresh usage entitlements.

## Rate Management

Quote and price products based on predefined rates for future use of the product or service.

- Use [standard objects](./rate-management-std-objects-parent.md) and fields to manage rates and discounts for a product’s resource consumption.

- Use [metadata API](./rate-management-metadata-api-parent.md) types to work with the metadata associated with Rate Management settings.

- Use [business APIs](./rate-management-business-api-overview.md) to get details of a rate plan and persisted rating waterfall.

- Use [invocable action](./rate-management-invocable-actions-parent.md) to invoke the rating service to rate the usage records.

## Dynamic Revenue Orchestrator

Get visibility into a product’s fulfillment journey. Also, get a view of the entire fulfillment design processes.

- Use [standard objects](./dynamic-revenue-orchestrator-std-objects-parent.md) to manage details of a product’s fulfillment.

- Use [invocable actions](./dynamic-revenue-orchestrator-invocable-actions-parent.md) to submit an order or a sales transaction to Dynamic Revenue Orchestrator for fulfillment.

- Use [metadata API](./dynamic-revenue-orchestrator-metadata-api-parent.md) types to work with the metadata associated with Flows.

- Use [callout](./dynamic-revenue-orchestrator-callouts-overview.md) step types to make ‌HTTP calls to an external system.

## Billing

Get an integrated and extensible subscription and usage-based billing solution. Automate processes such as payment processing, invoice generation, and usage-based billing.

- Use [standard objects](./billing-std-objects-parent.md) to manage billing and tax configurations, credit memos, and invoices.

- Use [platform events](./billing-pfrm-evnt-parent.md) types to know more about standard platform events.

- Use [invocable actions](./billing-invocable-actions-parent.md) to manage credit application, billing schedules, and invoices.

- Use [business APIs](./billing-business-api-overview.md) to manage credit application and to handle billing scenarios.

- Use built-in [Apex classes](./billing-apex-reference.md) to access the same capabilities that are available in the Billing Business APIs.

- Use [metadata API](./billing-metadata-api-parent.md) types to work with the metadata associated with Billing settings and Flows.

See the [RevenueManagementSettings](./meta-revenuemanagementsettings.md) metadata type to set up Revenue Management through configuration settings.

**See Also**

- [Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine.htm)

- [Context Service](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/context_service_overview.htm)

- [Salesforce Contracts](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/clm_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/rlm-get-started.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
