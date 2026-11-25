---
page_id: product-configurator-business-apis-resources
title: Resources
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-business-apis-resources.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-api-overview
legacy_page_id: product_configurator_business_apis_resources.htm
fetched_at: 2026-11-25
---

# Resources

Learn more about the available Product Configurator API resources.

- 

**[Configuration (POST)](./connect-resources-product-configurator-configure.md)**

Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle.

- 

**[Saved Configuration (GET, POST)](./connect-resources-save-product-configurations.md)**

Save and reuse a record’s configurations, and get a list of the saved configurations for a record.

- 

**[Saved Configuration (DELETE, PUT)](./connect-resources-saved-configuration.md)**

Update or delete a record’s saved configuration by using the configuration ID.

- 

**[Configuration Get Instance (POST)](./connect-resources-get-configurator-instance.md)**

Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system.

- 

**[Configuration Load Instance (POST)](./connect-resources-load-configurator-instance.md)**

Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management.

- 

**[Configuration Save Instance (POST)](./connect-resources-save-configuration-instance.md)**

Save a configuration instance after a successful product configuration.

- 

**[Configuration Set Instance (POST)](./connect-resources-set-configurator-instance.md)**

Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce.

- 

**[Configurator Add Nodes (POST)](./connect-resources-add-nodes.md)**

Add a node to the context through the runtime system without using the Salesforce user interface.

- 

**[Configurator Delete Nodes (POST)](./connect-resources-delete-nodes.md)**

Delete nodes from a product configuration.

- 

**[Configurator Update Nodes (POST)](./connect-resources-update-nodes.md)**

Update nodes in a product configuration.

- 

**[Product Set Quantity (POST)](./connect-resources-set-product-quantity.md)**

Set the quantity of a product through the runtime system.

- 

**[Config Rules (POST)](./connect-resources-config-rules.md)**

Run rules for a specific quote or order based on a context ID or transaction ID.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-business-apis-resources.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
