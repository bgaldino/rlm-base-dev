---
page_id: rlm_get_started.htm
title: Get Started with Revenue Management Developer Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Get Started with Revenue Management Developer Resources
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Get Started with Revenue Management Developer Resources

Get a single, unified system to automate your CRM processes. Use the developer sources
    of Revenue Management to automate the backend work to support the end-to-end revenue
    solution.

    

Revenue Cloud is now Revenue Management. You may see references to Revenue Cloud in our
      application and documentation.

    

        
          
            

          

          
            

          

        

      
| Available in: Lightning Experience |
| --- |
| Available in: **Enterprise**, **Unlimited**, and **Developer** Editions |

  

    

Revenue Management provides extensible and API-first business components of the product-to-cash
      processes. Learn more about the developer resources that are available for these
      components.

    

## Product Catalog Management

      
      

Create and manage an entire product portfolio with components such as attributes, product
        classifications, simple and bundled products, and rules.

      
        
- Use [standard objects](./pcm_std_objects_parent.htm.md)
          and fields to manage products, rules, and catalogs.

        
- Use [business APIs](./product_catalog_management_business_api.htm.md) to
          serve catalog definitions to users or applications.

        
- Use [metadata API](./pcm_metadata_api_parent.htm.md) types
          to access and manage the metadata types, such as product specification type and product
          specification record types.

        
- Use [tooling API](./pcm_tooling_api_parent.htm.md)
          objects to retrieve and manage smaller pieces of metadata types through SOQL capabilities.
          Use REST or SOAP to access metadata.

        
- Use [Product Discovery
            business APIs](./product_discovery_business_apis.htm.md), which are composite APIs, to search products or to discover
          catalogs, products, and categories.

      

    

    

## Salesforce Pricing

      
      

Create a reliable pricing solution for your users through customized price adjustment
        schedules. Get accurate pricing for your entire product portfolio.

      
        
- Use [standard objects](./pricing_std_objects_parent.htm.md) and fields to
          manage pricing processes such as product management, and the calculation and application
          of discounts.

        
- Use [business APIs](./pricing_business_apis.htm.md) to get unified pricing
          experiences across product lines.

        
- Use [invocable actions](./pricing_invocable_actions_parent.htm.md)
          to invoke the pricing Connect API by providing the pricing, context, and price waterfall
          details.

        
- Use [metadata API](./pricing_metadata_api_parent.htm.md) types to work with
          the metadata associated with Flows and Salesforce Pricing settings.

        
- Use [tooling API](./pricing_tooling_api_parent.htm.md) objects to retrieve
          and manage smaller pieces of metadata types through SOQL capabilities such as pricing
          action parameters, pricing procedure output map, and pricing recipe details. Use REST or
          SOAP to access metadata.

      

    

    

## Product Configurator

      
      

Customize the components and attributes of a product to meet the business requirement
        expectations.

      
        
- Use [standard objects](./prod_config_std_objects_parent.htm.md)
          to manage product-related information.

        
- Use the [business APIs](./product_configurator_business_api_overview.htm.md) to
          retrieve and update a product’s configuration from a configurator or to access
          configurator capabilities by integrating with any front-end application.

        
- Use [constraint modeling language](./cml_what_is_constraint_modeling_language.htm.md) to
          enforce business logic declaratively, without the need for extensive code in a
          general-purpose programming language.

      

    

    

## Transaction Management

      
      

Manage subscription lifecycles from quotes and orders to contracts, assets, amendments, and
        renewals. Get insights into customer assets and see a consolidated list of all assets that
        belong to an account.

      
        
- Use [standard objects](./quote_and_order_capture_standard_objects.htm.md)
          and fields to manage transactions and details of a customer asset. Use the QuoteSaveEvent
            [platform event](./quote_and_order_capture_platform_event.htm.md) to
          notify subscribers after saving of a quote is processed.

        
- Use [business APIs](./qoc_business_apis.htm.md) to place, clone,
          or supplement a sales transaction. You can also initiate amendment, renewal, or
          cancellation of assets by using APIs.

        
- Use [invocable actions](./qoc_invocable_actions_parent.htm.md)
          to create and activate an order from a quote, or to initiate amendment, renewal, or
          cancellation of assets through invocable actions.

        
- Use [metadata API](./qoc_metadata_api_parent.htm.md) types
          to work with the metadata associated with Flows.

        
- Use built-in [Apex classes and
            interfaces](./qoc_apex_reference.htm.md) grouped by namespace.

      

    

    
    

## Usage Management

      
      

Ensure transparent, accurate, and efficient management of usage data and estimated usage
        amount.

      
        
- Use [standard objects](./usage_management_std_objects_parent.htm.md)
          and fields to set up and manage consumption of usage-based products.

        
- Use [metadata API](./usage_management_metadata_api_parent.htm.md) types
          to work with the metadata associated with Usage Management.

        
- Use [business APIs](./usage_management_business_apis.htm.md) to
          get details of a usage-based product that’s associated with an asset, an order item, or a
          quote line item.

        
- Use [invocable actions](./usage_management_invocable_actions_parent.htm.md)
          to invoke usage summaries, process consumption overages, and refresh usage
          entitlements.

      

    

    

## Rate Management

      
      

Quote and price products based on predefined rates for future use of the product or
        service.

      
        
- Use [standard objects](./rate_management_std_objects_parent.htm.md)
          and fields to manage rates and discounts for a product's resource consumption.

        
- Use [metadata API](./rate_management_metadata_api_parent.htm.md) types
          to work with the metadata associated with Rate Management settings.

        
- Use [business APIs](./rate_management_business_api_overview.htm.md) to
          get details of a rate plan and persisted rating waterfall.

        
- Use [invocable action](./rate_management_invocable_actions_parent.htm.md)
          to invoke the rating service to rate the usage records.

      

    

    

## Dynamic Revenue Orchestrator

      
      

Get visibility into a product’s fulfillment journey. Also, get a view of the entire
        fulfillment design processes.

      
        
- Use [standard objects](./dynamic_revenue_orchestrator_std_objects_parent.htm.md)
          to manage details of a product’s fulfillment.

        
- Use [invocable actions](./dynamic_revenue_orchestrator_invocable_actions_parent.htm.md)
          to submit an order or a sales transaction to Dynamic Revenue Orchestrator for
          fulfillment.

        
- Use [metadata API](./dynamic_revenue_orchestrator_metadata_api_parent.htm.md) types
          to work with the metadata associated with Flows.

        
- Use [callout](./dynamic_revenue_orchestrator_callouts_overview.htm.md) step types
          to make ‌HTTP calls to an external system.

      

    

    

## Billing

Get an integrated and extensible subscription and usage-based
        billing solution. Automate processes such as payment processing, invoice generation, and
        usage-based billing.

        
- Use [standard objects](./billing_std_objects_parent.htm.md) to manage
          billing and tax configurations, credit memos, and invoices.

        
- Use [platform events](./billing_pfrm_evnt_parent.htm.md) types to know
          more about standard platform events.

        
- Use [invocable actions](./billing_invocable_actions_parent.htm.md)
          to manage credit application, billing schedules, and invoices.

        
- Use [business APIs](./billing_business_api_overview.htm.md) to manage credit
          application and to handle billing scenarios.

        
- Use built-in [Apex classes](./billing_apex_reference.htm.md) to
          access the same capabilities that are available in the Billing Business APIs.

        
- Use [metadata API](./billing_metadata_api_parent.htm.md) types to work with
          the metadata associated with Billing settings and Flows.

      

See the [RevenueManagementSettings](./meta_revenuemanagementsettings.htm.md) metadata type to set up Revenue Management
        through configuration settings.

  

#### See Also

- [Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/business_rules_engine.htm)

- [Context Service](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/context_service_overview.htm)

- [Salesforce Contracts](https://developer.salesforce.com/docs/atlas.en-us.264.0.clm_developer_guide.meta/clm_developer_guide/clm_intro.htm)
