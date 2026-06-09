---
page_id: rlm_get_started.htm
title: Get Started with Revenue Cloud Developer Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Get Started with Revenue Cloud Developer Resources
fetched_at: 2026-06-09
---

# Get Started with Revenue Cloud Developer Resources

Get a single, unified system to automate your CRM processes. Use the developer sources
of Revenue Cloud to automate the backend work to support the end-to-end revenue
solution.

|  |
| --- |
| Available in: Lightning Experience |
| Available in: **Enterprise**, **Unlimited**, and **Developer** Editions |

Revenue Cloud provides extensible and API-first business components of the product-to-cash
processes. Learn more about the developer resources that are available for these
components.

## Product Catalog Management

Create and manage an entire product portfolio with components such as attributes, product
classifications, simple and bundled products, and rules.

- Use [standard objects](./pcm_std_objects_parent.htm.md "The Product Catalog Management data model provides objects and fields to manage products, rules, and catalogs.")
  and fields to manage products, rules, and catalogs.
- Use [business APIs](./product_catalog_management_business_api.htm.md "Use primitive APIs of Product Catalog Management that serve catalog definitions to users or applications.") to
  serve catalog definitions to users or applications.
- Use [metadata API](./pcm_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types
  to access and manage the metadata types, such as product specification type and product
  specification record types.
- Use [tooling API](./pcm_tooling_api_parent.htm.md "Tooling API exposes metadata used in developer tooling that you can access through REST or SOAP. Tooling API’s SOQL capabilities for many metadata types allow you to retrieve smaller pieces of metadata.")
  objects to retrieve and manage smaller pieces of metadata types through SOQL capabilities.
  Use REST or SOAP to access metadata.
- Use [Product Discovery
  business APIs](./product_discovery_business_apis.htm.md "Use the Product Discovery Business APIs, which are composite APIs, to search products or to discover catalogs, products, and categories during the product browsing experience."), which are composite APIs, to search products or to discover
  catalogs, products, and categories.

## Salesforce Pricing

Create a reliable pricing solution for your users through customized price adjustment
schedules. Get accurate pricing for your entire product portfolio.

- Use [standard objects](./pricing_std_objects_parent.htm.md "The Salesforce Pricing data model provides objects and fields to manage pricing processes, such as product management and calculation and application of discounts.") and fields to
  manage pricing processes such as product management, and the calculation and application
  of discounts.
- Use [business APIs](./pricing_business_apis.htm.md "Perform pricing request, create context instance, sync pricing data, and manage pricing recipes and pricing waterfall details by using Salesforce Pricing Business APIs.") to get unified pricing
  experiences across product lines.
- Use [invocable actions](./pricing_invocable_actions_parent.htm.md "Learn more about the standard invocable actions available with Salesforce Pricing.")
  to invoke the pricing Connect API by providing the pricing, context, and price waterfall
  details.
- Use [metadata API](./pricing_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types to work with
  the metadata associated with Flows and Salesforce Pricing settings.
- Use [tooling API](./pricing_tooling_api_parent.htm.md "Tooling API exposes metadata used in developer tooling that you can access through REST or SOAP. Tooling API’s SOQL capabilities for many metadata types allow you to retrieve smaller pieces of metadata.") objects to retrieve
  and manage smaller pieces of metadata types through SOQL capabilities such as pricing
  action parameters, pricing procedure output map, and pricing recipe details. Use REST or
  SOAP to access metadata.

## Product Configurator

Customize the components and attributes of a product to meet the business requirement
expectations.

- Use [standard objects](./prod_config_std_objects_parent.htm.md "The Product Configurator data model provides objects and fields to manage the product configurator flow.")
  to manage product-related information.
- Use the [business APIs](./product_configurator_business_api_overview.htm.md "Use the Product Configurator Business APIs to customize a product or a service according to your business-specific requirements.") to
  retrieve and update a product’s configuration from a configurator or to access
  configurator capabilities by integrating with any front-end application.
- Use [constraint modeling language](./cml_what_is_constraint_modeling_language.htm.md "Constraint Modeling Language (CML) is a domain-specific language that defines models for complex systems. For product configuration, constraint models describe real-world entities and their relationships to each other.") to
  enforce business logic declaratively, without the need for extensive code in a
  general-purpose programming language.

## Transaction Management

Manage subscription lifecycles from quotes and orders to contracts, assets, amendments, and
renewals. Get insights into customer assets and see a consolidated list of all assets that
belong to an account.

- Use [standard objects](./quote_and_order_capture_standard_objects.htm.md "The Transaction Management data model provides objects and fields to manage transactions.")
  and fields to manage transactions and details of a customer asset. Use the QuoteSaveEvent
  [platform event](./quote_and_order_capture_platform_event.htm.md "Use the QuoteSaveEvent event to notify subscribers after saving of a quote is processed.") to
  notify subscribers after saving of a quote is processed.
- Use [business APIs](./qoc_business_apis.htm.md "Use the Transaction Management Business APIs to fetch instant pricing data on a quote or an order, to create a quote, or to create an order.") to place, clone,
  or supplement a sales transaction. You can also initiate amendment, renewal, or
  cancellation of assets by using APIs.
- Use [invocable actions](./qoc_invocable_actions_parent.htm.md "Learn more about the standard invocable actions available with Transaction Management.")
  to create and activate an order from a quote, or to initiate amendment, renewal, or
  cancellation of assets through invocable actions.
- Use [metadata API](./qoc_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types
  to work with the metadata associated with Flows.
- Use built-in [Apex classes and
  interfaces](./qoc_apex_reference.htm.md "Use built-in Apex classes and interfaces grouped by namespace.") grouped by namespace.

## Usage Management

Ensure transparent, accurate, and efficient management of usage data and estimated usage
amount.

- Use [standard objects](./usage_management_std_objects_parent.htm.md "The Usage Management data model provides objects and fields to set up and manage consumption of usage-based products.")
  and fields to set up and manage consumption of usage-based products.
- Use [metadata API](./usage_management_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types
  to work with the metadata associated with Usage Management.
- Use [business APIs](./usage_management_business_apis.htm.md "Use the Usage Management Business APIs to get details of a usage-based product that’s associated with an asset, an order item, or a quote line item.") to
  get details of a usage-based product that’s associated with an asset, an order item, or a
  quote line item.
- Use [invocable actions](./usage_management_invocable_actions_parent.htm.md "Learn more about the standard invocable actions available with Usage Management.")
  to invoke usage summaries, process consumption overages, and refresh usage
  entitlements.

## Rate Management

Quote and price products based on predefined rates for future use of the product or
service.

- Use [standard objects](./rate_management_std_objects_parent.htm.md "The Rate Management data model provides objects and fields to manage rates and discounts for a product's resource consumption.")
  and fields to manage rates and discounts for a product's resource consumption.
- Use [metadata API](./rate_management_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types
  to work with the metadata associated with Rate Management settings.
- Use [business APIs](./rate_management_business_api_overview.htm.md "Use the Rate Management Business APIs to get rate plan and persisted rating waterfall details.") to
  get details of a rate plan and persisted rating waterfall.
- Use [invocable action](./rate_management_invocable_actions_parent.htm.md "Learn more about the standard invocable actions available with Rate Management.")
  to invoke the rating service to rate the usage records.

## Dynamic Revenue Orchestrator

Get visibility into a product’s fulfillment journey. Also, get a view of the entire
fulfillment design processes.

- Use [standard objects](./dynamic_revenue_orchestrator_std_objects_parent.htm.md "The Dynamic Revenue Orchestrator data model provides objects and fields to manage details of a product’s fulfillment.")
  to manage details of a product’s fulfillment.
- Use [invocable actions](./dynamic_revenue_orchestrator_invocable_actions_parent.htm.md "Use standard invocable actions to submit an order or a sales transaction to Dynamic Revenue Orchestrator (DRO) for fulfillment.")
  to submit an order or a sales transaction to Dynamic Revenue Orchestrator for
  fulfillment.
- Use [metadata API](./dynamic_revenue_orchestrator_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types
  to work with the metadata associated with Flows.
- Use [callout](./dynamic_revenue_orchestrator_callouts_overview.htm.md "Use callout step types to make ‌HTTP calls to an external system. Callout step types use the Data Consumption Framework and Process Type Integration for interface management and communication with external systems.") step types
  to make ‌HTTP calls to an external system.

## Billing

Get an integrated and extensible subscription and usage-based
billing solution. Automate processes such as payment processing, invoice generation, and
usage-based billing.

- Use [standard objects](./billing_std_objects_parent.htm.md "The Billing data model provides objects and fields to manage billing and tax configurations, credit memos, and invoices, and accounting periods for legal entities.") to manage
  billing and tax configurations, credit memos, and invoices.
- Use [platform events](./billing_pfrm_evnt_parent.htm.md "Salesforce publishes standard platform events in response to an action that occurred in the org or to report errors. For example, the InvoiceProcessedEvent platform event sends notification to the customer when the billing invoice activity is complete. You can subscribe to a standard platform event by using the subscription mechanism that the event supports.") types to know
  more about standard platform events.
- Use [invocable actions](./billing_invocable_actions_parent.htm.md "Use standard invocable actions to automate processes such as credit application, billing schedules creation, and invoice management.")
  to manage credit application, billing schedules, and invoices.
- Use [business APIs](./billing_business_api_overview.htm.md "Use the Billing Business APIs to manage credit application and to handle billing scenarios.") to manage credit
  application and to handle billing scenarios.
- Use built-in [Apex classes](./billing_apex_reference.htm.md "Billing provides the ConnectApi namespace (also called Connect in Apex) that contains classes for accessing the same capabilities that are available in the Billing Business APIs. Additionally, you can use other built-in Apex classes and interfaces grouped by namespace.") to
  access the same capabilities that are available in the Billing Business APIs.
- Use [metadata API](./billing_metadata_api_parent.htm.md "Metadata API enables you to access some types and feature settings that you can customize in the user interface.") types to work with
  the metadata associated with Billing settings and Flows.

See the [RevenueManagementSettings](./meta_revenuemanagementsettings.htm.md "Represents the configuration settings to set up Revenue Cloud.") metadata type to set up Revenue Cloud
through configuration settings.

#### See Also

- [Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/business_rules_engine.htm "Business Rules Engine - HTML (New Window)")
- [Context Service](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/context_service_overview.htm "Context Service - HTML (New Window)")
- [Salesforce Contracts](https://developer.salesforce.com/docs/atlas.en-us.262.0.clm_developer_guide.meta/clm_developer_guide/clm_intro.htm "Salesforce Contracts - HTML (New Window)")
