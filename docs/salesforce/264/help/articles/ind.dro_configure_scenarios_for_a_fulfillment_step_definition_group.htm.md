---
article_id: ind.dro_configure_scenarios_for_a_fulfillment_step_definition_group.htm
title: Configure a Fulfillment Scenario
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_scenarios_for_a_fulfillment_step_definition_group.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-09-05
---

# Configure a Fulfillment Scenario

Use a fulfillment scenario to define when Dynamic Revenue Orchestrator (DRO) adds a fulfillment step definition group to a fulfillment plan after an order is submitted. Fulfillment scenarios help you add common fulfillment steps automatically instead of creating the steps for each order.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management
USER PERMISSIONS
NEEDED
To set conditions for fulfillment step groups:	

Fulfillment Designer

OR

DRO Admin User

Create scenarios for a specific product, a product classification, or an entire order.

A product-based scenario applies to a specific product.
A product classification-based scenario applies to products in a selected product classification.
An order-based scenario applies to the entire order, regardless of its products.
Fulfillment Scenario Types
CHARACTERISTIC	PRODUCT-BASED SCENARIO	PRODUCT CLASSIFICATION-BASED SCENARIO	ORDER-BASED SCENARIO
Configuration	Select a product.	Select a product classification.	Leave Product and Product Classification blank, and set Dependency Scope to Plan.
Applies To	An order that contains the selected product.	An order that contains a product in the selected product classification.	The entire order, regardless of its products.
Execution Rule Fields	Supports product attributes, order line item fields, and order-level fields.	Supports product attributes, order line item fields, and order-level fields.	Supports only order-level fields. Product-specific and order line item fields aren't available.
Changes After Order Submission	Supported. You can modify steps after the order is submitted.	Supported. You can modify steps after the order is submitted.	Not supported. You can't modify steps after the order is submitted.
Example Usecases	Specialized handling or delivery for a specific product. =	Warehouse processing or other common requirements for a group of products. =	Credit checks, approval workflows, and regional requirements for the entire order.

For example, you have a laptop bundle and fetching the laptop from the warehouse is a common fulfillment step. For this situation, define a fulfillment scenario with the condition that when the laptop bundle is added to an order, DRO adds a step to fetch the laptop from the warehouse.

From the App Launcher, find and select Fulfillment Workspaces.
Select a fulfillment step definition group.
In the Details panel, select Related.
Under Scenarios, click New.
Name the scenario.
Enter the name of the relevant fulfillment step definition group.
Select a product or a product classification the scenario applies to.
To apply the scenario to the entire order regardless of the products, leave the Product and Product Classification fields blank and set the dependency scope to Plan.
Select a Usage Type.
From the Available list, move the actions that trigger adding the group to a fulfillment plan to the Chosen list.
Save your work.
To save the scenario and see the details pane for the scenario, click Save.
To save the scenario and then define when the scenario runs during fulfillment, click Save & Configure Execution Rules.
NOTE To view the details and related scenarios for the step definition group, click the group and check the side panel. You can create a scenario from the side panel.
If you configure a fulfillment scenario between a product class and a step group, and then another scenario between a product belonging to the product class and the same step group, then the scenario configured for the product is applied during plan generation.
Define appropriate conditions to resolve the scenarios when multiple product-based or order-based fulfillment scenarios exist for an order.
EXAMPLE

Let’s say you create two products called HiTech ServerDrive and HiTech ServerDrive - Express under the classification Enterprise Server Components. To pull the units from the warehouse, you create a fulfillment step definition group called Standard Warehouse Processing.

Next, create a fulfillment scenario. Specify that the chosen action is Add, select the Standard Warehouse Processing step definition group, and select the Enterprise Server Components product classification.

Then, create another fulfillment scenario specifically for the HiTech ServerDrive - Express product and use the Express Delivery step group.

When HiTech ServerDrive is added to an order and the order is submitted, the Standard Warehouse Processing step definition group is added to the fulfillment plan. However, when HiTech ServerDrive - Express is added to the order, DRO recognizes the specific Express Delivery scenario defined for the product and uses the Express Delivery step group instead of the Standard Warehouse Processing step group from the product class.

This product-specific fulfillment scenario overrides the more general, class-based scenario, which helps HiTech to handle exceptions or special cases in their fulfillment process.

Define Conditions for a Product Fulfillment Scenario
After you've created a product fulfillment scenario, you can define conditions to determine whether the scenario is used during fulfillment.
