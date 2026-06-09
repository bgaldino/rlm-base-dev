---
page_id: product_configurator_business_api_overview.htm
title: Product Configurator Business APIs
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_configurator_business_api_overview.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: prod_config_overview.htm
fetched_at: 2026-06-09
---

# Product Configurator Business APIs

Use the Product Configurator Business APIs to customize a product or a service
according to your business-specific requirements.

Perform product configuration-related operations by using the Product Configurator Business
APIs. Integrate these APIs with any front-end application to access the configurator
capabilities.

These APIs are stateless and don't recall prior user actions between calls unless state is
explicitly persisted and reloaded.

For example, if a user deselects a child product and later reselects it, the engine treats
the request as adding a new item that doesn't currently exist in the model. It can’t infer
that this request is a re-selection of a previously removed item. As a result, the original
line item isn't restored and a new line item is created.

This table lists the available Product Configurator resources.

| Resource | Description |
| --- | --- |
| [`/connect/cpq/configurator/actions/configure`](./connect_resources_product_configurator_configure.htm.md "Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle.") (POST) | Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle. |
| [`/connect/cpq/configurator/actions/load-instance`](./connect_resources_load_configurator_instance.htm.md "Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management.") (POST) | Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management. |
| [`/connect/cpq/configurator/actions/set-instance`](./connect_resources_set_configurator_instance.htm.md "Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce.") (POST) | Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce. |
| [`/connect/cpq/configurator/actions/get-instance`](./connect_resources_get_configurator_instance.htm.md "Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system.") (POST) | Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system. |
| [`/connect/cpq/configurator/actions/save-instance`](./connect_resources_save_configuration_instance.htm.md "Save a configuration instance after a successful product configuration.") (POST) | Save a configuration instance after a successful product configuration. |
| [`/connect/cpq/configurator/actions/set-product-quantity`](./connect_resources_set_product_quantity.htm.md "Set the quantity of a product through the runtime system.") (POST) | Set the quantity of a product through the runtime system. |
| [`/connect/cpq/configurator/actions/add-nodes`](./connect_resources_add_nodes.htm.md "Add a node to the context through the runtime system without using the Salesforce user interface.") (POST) | Add a node to the context through the runtime system without using the Salesforce user interface. |
| [`/connect/cpq/configurator/actions/update-nodes`](./connect_resources_update_nodes.htm.md "Update nodes in a product configuration.") (POST) | Update nodes in a product configuration. |
| [`/connect/cpq/configurator/actions/delete-nodes`](./connect_resources_delete_nodes.htm.md "Delete nodes from a product configuration.") (POST) | Delete nodes from a product configuration. |
| [`/revenue/product-configurator/rules/actions/execute`](./connect_resources_config_rules.htm.md "Run rules for a specific quote or order based on a context ID or transaction ID.") (POST) | Run rules for a specific quote or order based on a context ID or transaction ID. |

- **[Resources](./product_configurator_business_apis_resources.htm.md)**  
  Learn more about the available Product Configurator API resources.
- **[Request Bodies](./product_configurator_business_apis_requests.htm.md)**  
  Learn more about the available Product Configurator API request bodies.
- **[Response Bodies](./product_configurator_business_apis_responses.htm.md)**  
  Learn more about the available Product Configurator API response bodies.

#### See Also

- [*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm "Connect REST API Developer Guide: Introduction - HTML (New Window)")
- [*Salesforce Help*: Product Configurator Permissions](https://help.salesforce.com/s/articleView?id=ind.product_configurator_product_configurator_permissions.htm&type=5&language=en_US "Salesforce Help: Product Configurator Permissions - HTML (New Window)")
