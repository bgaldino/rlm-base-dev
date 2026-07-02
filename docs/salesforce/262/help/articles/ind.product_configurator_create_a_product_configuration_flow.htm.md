---
article_id: ind.product_configurator_create_a_product_configuration_flow.htm
title: Define Product Configuration Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_create_a_product_configuration_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Define Product Configuration Flows

The product configuration flow provides a layout for configuring the products and previewing the user experience in real time. The flow provides a simple layout for defining attribute details, ensuring a smooth buying experience for your customers.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To create a product configuration flow, and assign products and product classifications to the flow:	Product Configurator
Create a Product Configuration Flow

Define the flow that's used for configuring products or product classifications.

From the App Launcher, find and select Product Configuration Flows.
Click New.
For Flow Identifier, enter the API name of the flow that you want to use as the product configuration flow.
Select a status.
You can assign only active product configuration flows to products and product classifications.
To set this flow as the default product configuration flow for your org, select Default.
Products and product classifications without an assigned product configuration flow use the default product configuration flow.
Save your changes.
Assign Products to a Product Configuration Flow

Configure the product configuration flow for products. You can assign only one product configuration flow to a product.

From the App Launcher, find and select Product Configuration Flows.
Open the product configuration flow that you want to assign products to.
On the Related tab, in the Product Configuration Flow Assignment related list, click New.
Find and select the product that you want to assign to the product configuration flow.
Save your changes.

Similarly, assign other products to the product configuration flow. To unassign a product from the product configuration flow, delete the corresponding Product Configuration Flow Assignment record.

For products assigned to a flow, verify the product configuration experience seen during run time.

Assign Product Classifications to a Product Configuration Flow

Configure the product configuration flow for product classifications. You can assign only one product configuration flow to a product classification.

From the App Launcher, find and select Product Configuration Flows.
Open the product configuration flow that you want to assign product classifications to.
On the Related tab, in the Product Configuration Flow Assignment related list, click New.
Find and select the product classification that you want to assign to the product configuration flow.
To use the selected product configuration flow as the flow for the primary product or classification, select Primary Configurator Flow. For a multilevel product bundle, the product configuration flow assigned to the bundle root product is used at all levels, even if a child product in the bundle has a different Primary Configurator Flow assigned.
Save your changes.

Similarly, assign other product classifications to the product configuration flow. To unassign a product from the product configuration flow, delete the corresponding Product Configuration Flow Assignment record.

For product classifications assigned to a flow, verify the product configuration experience seen during run time.
