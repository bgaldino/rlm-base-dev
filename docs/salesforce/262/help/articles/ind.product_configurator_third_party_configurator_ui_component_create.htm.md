---
article_id: ind.product_configurator_third_party_configurator_ui_component_create.htm
title: Create a Third-Party Configurator UI Component
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator_ui_component_create.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Create a Third-Party Configurator UI Component

Create a Lighting web component (LWC) to use as a custom third-party configurator UI component and add the custom component to the product configuration flow.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To add a custom component to a product configuration flow	Product Configurator
Use Salesforce Developer Experience (Salesforce DX) to create an LWC to use as a custom UI component. See Create Lightning Web Components.
To add the custom component to the product configuration flow and define the logic for sending and receiving data, in the custom component folder add the required HTML, JavaScript, and js-meta.xml files.
To enable the custom component to communicate with the Data Manager component in the product configuration flow, trigger Lightning Message Service (LMS) events. Make sure that the custom component doesn't directly call the configurator API or any Save APIs. See Communicate Across the DOM with Lightning Message Service.
In Flow Builder, drag the custom component from the sidebar to the Product Configurator Flow layout. See Flow Builder Tour.
In the Flow Builder sidebar, open the Data Manager component to view the available outputs, and then link the appropriate data manager outputs to the custom component.
SEE ALSO
Third-Party Configurator UI Component HTML File
Third-Party Configurator UI Component JavaScript File
Third-Party Configurator UI Component Metadata Configuration File
