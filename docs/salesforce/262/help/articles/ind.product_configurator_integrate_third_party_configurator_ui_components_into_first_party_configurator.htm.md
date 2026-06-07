---
article_id: ind.product_configurator_integrate_third_party_configurator_ui_components_into_first_party_configurator.htm
title: Third-Party Configurator UI Component Integration into First-Party Configurator
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_integrate_third_party_configurator_ui_components_into_first_party_configurator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Third-Party Configurator UI Component Integration into First-Party Configurator

As a third-party user, apart from replacing the first-party configurator, you can also create a custom Lightning Flow UI configurator component and integrate the UI component to the first-party configurator UI. This approach provides a functional enhancement to the existing first-party configurator UI.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

To add a widget, include the Lightning Web Component (LWC) in the ISV managed package. After the LWC component is available, the product catalog admin modifies the default first-party configurator to add the third-party user’s custom LWC components. The widgets can interact with the first-party configurator data, including:

Product details and bundle configurations.
Product pricing and pricing results.
Product attributes and their specified values.
EXAMPLE Consider a map widget that a third-party user develops by using the LWC platform’s map UI component. When you select a location on the map, the widget automatically updates the latitude and longitude coordinates stored as product attributes. Sales reps can use this widget to configure the location for a specific product.
