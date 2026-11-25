---
page_id: product-configurator-business-api-overview
title: Product Configurator Business APIs
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-business-api-overview.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: prod-config-overview
legacy_page_id: product_configurator_business_api_overview.htm
fetched_at: 2026-11-25
---

# Product Configurator Business APIs

Use the Product Configurator Business APIs to customize a product or a service according to your business-specific requirements.

Perform product configuration-related operations by using the Product Configurator Business APIs. Integrate these APIs with any front-end application to access the configurator capabilities.

These APIs are stateless and don’t recall prior user actions between calls unless state is explicitly persisted and reloaded.

For example, if a user deselects a child product and later reselects it, the engine treats the request as adding a new item that doesn’t currently exist in the model. It can’t infer that this request is a re-selection of a previously removed item. As a result, the original line item isn’t restored and a new line item is created.

This table lists the available Product Configurator resources.

| Resource | Description |
| --- | --- |
| [`/connect/cpq/configurator/actions/configure`](./connect-resources-product-configurator-configure.md) (POST) | Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle. |
| [`/connect/cpq/configurator/actions/load-instance`](./connect-resources-load-configurator-instance.md) (POST) | Create a session for the product configuration instance using the transaction ID. Get the session ID that includes the results of actions, such as configuration rules, qualification rules, and pricing management. |
| [`/connect/cpq/configurator/actions/set-instance`](./connect-resources-set-configurator-instance.md) (POST) | Set a product configuration instance. This API is used in scenarios where the configuration instance is available in a different database than Salesforce and the product catalog management data is in Salesforce. |
| [`/connect/cpq/configurator/actions/get-instance`](./connect-resources-get-configurator-instance.md) (POST) | Fetch the JSON representation of a product configuration. Use the response to display the details of the product configuration instance on the Salesforce user interface, or save the product configuration instance to an external system. |
| [`/connect/cpq/configurator/actions/save-instance`](./connect-resources-save-configuration-instance.md) (POST) | Save a configuration instance after a successful product configuration. |
| [`/connect/cpq/configurator/actions/set-product-quantity`](./connect-resources-set-product-quantity.md) (POST) | Set the quantity of a product through the runtime system. |
| [`/connect/cpq/configurator/actions/add-nodes`](./connect-resources-add-nodes.md) (POST) | Add a node to the context through the runtime system without using the Salesforce user interface. |
| [`/connect/cpq/configurator/actions/update-nodes`](./connect-resources-update-nodes.md) (POST) | Update nodes in a product configuration. |
| [`/connect/cpq/configurator/actions/delete-nodes`](./connect-resources-delete-nodes.md) (POST) | Delete nodes from a product configuration. |
| [`/revenue/product-configurator/rules/actions/execute`](./connect-resources-config-rules.md) (POST) | Run rules for a specific quote or order based on a context ID or transaction ID. |

- 

**[Resources](./product-configurator-business-apis-resources.md)**

Learn more about the available Product Configurator API resources.

- 

**[Request Bodies](./product-configurator-business-apis-requests.md)**

Learn more about the available Product Configurator API request bodies.

- 

**[Response Bodies](./product-configurator-business-apis-responses.md)**

Learn more about the available Product Configurator API response bodies.

**See Also**

- 

[*Salesforce Help*: Product Configurator Permissions](https://help.salesforce.com/s/articleView?id=ind.product_configurator_product_configurator_permissions.htm&type=5)

- 

[*Connect REST API Developer Guide*: Introduction](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-business-api-overview.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
