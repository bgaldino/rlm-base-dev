---
page_id: cml_configure_business_api_pipeline.htm
title: How CML Fits in the Product Configure Business API Pipeline
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_configure_business_api_pipeline.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_cml_core_concepts.htm
fetched_at: 2026-09-29
---

# How CML Fits in the Product Configure Business API Pipeline

When you call the Product Configure Business API, the request runs through a fixed
  sequence of stages. The CML constraint engine is one stage in that sequence, and where it runs
  determines which data it can see. 

  

A single Product Configure Business API call processes the stages in this order.

  
   
- The Product Configure Business API receives the request. 

   
- The CML constraint engine evaluates the configuration and enforces the constraint model. 

   
- Pricing procedures calculate prices. 

   
- Apex triggers run. 

   
- The API returns the response. 

  

  

Because the constraint engine runs before pricing procedures and Apex triggers, CML can't read
   any value that those later stages produce in the same API call. Values calculated by pricing,
   such as `NetUnitPrice`, and rollups or fields populated by
   Apex triggers, aren't available to CML during that call. If a constraint or external variable
   references one of these values, it reads whatever was in the context before the call, which is
   typically a stale value from a previous call or null on the first call.

  

In this example, `GeneratorSet` declares an external
   variable bound to the pricing-computed `NetUnitPrice` line
   item field, and a rule that tries to react to it.

  

```
type GeneratorSet {
    int requiredKW = [101..10000];
    relation Accessories : Accessory[1..99];

    // Binds to the pricing-computed NetUnitPrice line item field.
    @(tagName = "NetUnitPrice")
    extern decimal(2) NetUnitPrice = 0;

    /**
    * @Title Price-Based Accessory Recommendation
    * Attempts to recommend 2 accessories when the net unit price
    * exceeds 5000. This does NOT work as intended.
    */
    setdefault(
        NetUnitPrice > 5000,
        Accessories[Accessory] == 2,
        "2 accessories are recommended for high-value generator sets"
    );
}
```

  

On the first Product Configure Business API call, pricing procedures haven't run yet when the
   constraint engine evaluates the model, so `NetUnitPrice` has
   no calculated value. The `NetUnitPrice` external variable
   falls back to its default of 0 (or is null if no default is set), the condition `NetUnitPrice > 5000` is false, and the rule never fires. On a later
   call, `NetUnitPrice` reflects the price from the previous call
   rather than the current configuration, so the rule reacts to a stale value. In either case, the
   rule can't reliably respond to the current price, because the price for the current configuration
   isn't computed until after the constraint engine finishes.

  

To make calculated values such as `NetUnitPrice` or rollup
   totals available to CML, split the work into two passes and let pricing run in between. The first
   pass produces a configuration, a separate pricing call calculates and stamps the values onto the
   transaction, and the second configuration pass reads those values. 

  
   
- Call the Product Configurator Business API, and capture the product bundle line configuration
    returned in the JSON payload. The payload holds the configuration state, which is the selected
    products, quantities, attribute values, and line item structure. You reuse this payload to
    preserve the configuration in the second call. 

   
- Invoke the Pricing Business API to let pricing run. Make a POST request to the Pricing
    Business API, passing the line items from the configuration you captured. This call runs the
    pricing procedures and any pricing-related Apex triggers to completion, so that final prices,
    taxes, and discounts are computed and committed to the transaction state.

   
- Extract the calculated pricing values, such as `NetUnitPrice`, total amounts, or custom rollup fields, from the Pricing Business API
    response. Map those values into the external variables or context parameters that the CML model
    reads. These values are separate from the configuration payload, so you add them to the state
    yourself. 

   
- Call the Product Configurator Business API a second time. Pass the configuration state
    together with the pricing values. On this pass, CML reads the calculated prices instead of null
    or stale values, so it evaluates your price-dependent constraints and hide or show rules
    correctly. 

  

  

For the `GeneratorSet` example, the `NetUnitPrice` external variable returns 0 on the first pass. After
   the Pricing Business API runs and you map the result back, the second pass with the Product
   Configurator Business API reads the updated `NetUnitPrice`, so
   the `setdefault` rule fires as intended.

  

For more information, see [Product Configurator Business APIs](./product_configurator_business_api_overview.htm.md) and [Salesforce Pricing Business APIs](./pricing_business_apis.htm.md).
