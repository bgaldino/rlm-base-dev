---
page_id: product_configurator_business_apis_resources.htm
title: Resources
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_configurator_business_apis_resources.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_api_overview.htm
fetched_at: 2026-06-09
---

# Resources

Learn more about the available Product Configurator API resources.

- **[Configuration (POST)](./connect_resources_product_configurator_configure.htm.md)**  
  Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle.
- **[Saved Configuration (GET, POST)](./connect_resources_save_product_configurations.htm.md)**  
  Save and reuse a record's configurations, and get a list of the saved configurations for a record.
- **[Saved Configuration (DELETE, PUT)](./connect_resources_saved_configuration.htm.md)**  
  Update or delete a record's saved configuration by using the configuration ID.
- **[Configuration Get Instance (POST)](./connect_resources_get_configurator_instance.htm.md)**  
  Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system.
- **[Configuration Load Instance (POST)](./connect_resources_load_configurator_instance.htm.md)**  
  Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management.
- **[Configuration Save Instance (POST)](./connect_resources_save_configuration_instance.htm.md)**  
  Save a configuration instance after a successful product configuration.
- **[Configuration Set Instance (POST)](./connect_resources_set_configurator_instance.htm.md)**  
  Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce.
- **[Configurator Add Nodes (POST)](./connect_resources_add_nodes.htm.md)**  
  Add a node to the context through the runtime system without using the Salesforce user interface.
- **[Configurator Delete Nodes (POST)](./connect_resources_delete_nodes.htm.md)**  
  Delete nodes from a product configuration.
- **[Configurator Update Nodes (POST)](./connect_resources_update_nodes.htm.md)**  
  Update nodes in a product configuration.
- **[Product Set Quantity (POST)](./connect_resources_set_product_quantity.htm.md)**  
  Set the quantity of a product through the runtime system.
- **[Config Rules (POST)](./connect_resources_config_rules.htm.md)**  
  Run rules for a specific quote or order based on a context ID or transaction ID.
