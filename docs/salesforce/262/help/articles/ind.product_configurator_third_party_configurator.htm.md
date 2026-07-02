---
article_id: ind.product_configurator_third_party_configurator.htm
title: Third-Party Configurator
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_third_party_configurator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Third-Party Configurator

Agentforce Revenue Management provides extensibility options to third-party users seeking to build integrations with the Agentforce Revenue Management product. Agentforce Revenue Management supports various third-party use cases. The support includes replacing the first-party configurator with the third-party configurator, integrating third-party UI components into the first-party configurator, and creating custom configurator UI using headless configurator APIs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

Product catalog admin uses the product configuration flows to link different configurators (first-party or third-party) to specific products and product classifications. By integrating third-party configurators, the product catalog admins can determine the appropriate configurator for each product, whether it's a first-party or a specialized third-party configurator. The product catalog admin can set the third-party configurator as the default configurator for all the products.

EXAMPLE

Within the same organization, a Product Catalog admin can make these assignments:

Assign the Laptop Pro Bundle product to use the ABC third-party configurator.
Assign the Excavator 3000 product to use the xyz third-party three-dimensional configurator.
Set all products in the Cellphone product classification to use a customized lightning flow configurator, based on the standard Agentforce Revenue Management configurator components.
All other products to use the first-party configurator.
Create a Third-Party Configurator UI Component
Create a Lighting web component (LWC) to use as a custom third-party configurator UI component and add the custom component to the product configuration flow.
Third-Party Configurator UI Component Files
A Lightning web component that renders UI must include an HTML file, a JavaScript file, and a metadata configuration file.
Third-Party Configurator Lightning Flows
Third-party users can build a third-party configurator as a replacement to the first-party configurator using the screen-based lightning flows. The screen-based lightning flow is either included in the managed package or custom built in the org.
Third-Party Configurator UI Component Integration into First-Party Configurator
As a third-party user, apart from replacing the first-party configurator, you can also create a custom Lightning Flow UI configurator component and integrate the UI component to the first-party configurator UI. This approach provides a functional enhancement to the existing first-party configurator UI.
Custom Configurator Development with First-Party Configurator APIs
As a third-party user, build a custom configurator UI by using the public Configurator APIs. Incorporate the existing first-party configurator UI components for a familiar look and feel, and deliver a personalized experience by using the configurator API functionalities.
Use Third-Party Configurator for Specific Products or Classifications
Configure product or classifications by using the third-party configurator instead of the default configurator.
Use Place Sales Transaction API for Data Transfer
Transfer data from a custom configurator to a quote or order in Agentforce Revenue Management by using the Place Sales Transaction API.
Data Types for Configurator User Interface
The Apex classes contain data accessible through the user interface. The Configurator’s Data Manager acts as the primary user interface component that exports data to other components. As a third-party user you can pass the data into your own user interface component without the need for separate queries to fetch data.
