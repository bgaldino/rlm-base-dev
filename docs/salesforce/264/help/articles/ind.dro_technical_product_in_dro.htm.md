---
article_id: ind.dro_technical_product_in_dro.htm
title: Build Your Technical Product Catalog for Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_technical_product_in_dro.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_decomposition.htm
fetched_at: 2026-09-05
---

# Build Your Technical Product Catalog for Dynamic Revenue Orchestrator

A technical product represents the items, services, or processes that enable order fulfillment to deliver a complete commercial product to your customer. A technical product lets fulfillment designers decouple front-office entities from mid- and back-office entities. To use Dynamic Revenue Orchestrator, you must configure your technical products using Product Catalog Management.

NOTE If you aren't familiar with creating products and product catalogs, see Product Catalog Management.
Model a Technical Product

Model a technical product when:

The packaged products are decoupled from the services and equipment provided to the customer. In this case, you can model a technical product for services and equipment.
A technical product contains the details of order fulfillment through orchestration that CRM systems don't provide during the order capture.
The technical product's attributes contain necessary data for fulfillment, such as specifications of RAM for a server.
Multiple commercial products use the same fulfillment processes or systems. For example, all products in a portfolio use the same billing system to generate invoices.
Commercial line items decompose into multiple technical products, and each component requires a different fulfillment process or system.
Attributes of a commercial product or order are passed to different fulfillment systems, either directly or after transformation. For example, the start date of a line item is passed to the provisioning system, and the weight is passed to the shipping partner.

Don't model a technical product in these cases:

The technical product duplicates a commercial product.
It has information of commercial significance.
It determines pricing during quoting or ordering.
It changes attributes and fields during quoting or ordering.
Scenarios to Model a Technical Product in Dynamic Revenue Orchestrator
Fulfilling Tangible Products

Consider a scenario for fulfilling orders for servers bundled with RAM and storage as child products. The fulfillment plan can include steps that run in sequence or in parallel. For example, you can model a technical product for:

Managing warehouse-related activities
Managing the shipping of items
Generating the invoice for the customer

In this scenario, you can reuse technical products when new models and variants of servers, RAM, memory, and products in similar categories are added to the commercial catalog.

Fulfilling Non-Tangible Products

Consider a scenario for selling a suite of cloud-based productivity and collaboration tools, including email, cloud storage, word processor, and spreadsheets to businesses. In this scenario, you can model a technical product for:

Account creation and management service
Identity and access management provisioning service for the users
License provisioning for each application that requires activation
Usage-entitlement provisioning
Fulfilling Bundled Tangible and Non-Tangible Products

Consider a scenario of a car dealer providing three years of free annual service along with vehicle insurance. In this case, you can model a technical product for:

Dealer-specific activities such as placing orders with manufacturers, car inspections, registrations, and deliveries.
Non-dealer activities such as providing annual servicing and warranties.
Examples of Technical Products

Consider a scenario for fulfilling orders for office laptops. The customer understands that these laptops have specifications like 16GB RAM, 500 GB SSD storage, and uses operating system version 22.04. However, your fulfillment team needs to keep track of many more details.

When the retail order decomposes for fulfillment, you might use technical products such as:

The physical laptop itself
The operating system license
Corporate user account activation
Office productivity application licenses
Corporate VPN account
Antivirus protection license
IT asset tag registration
Laptop peripherals package
Create a Technical Product
To create technical products in Dynamic Revenue Orchestrator (DRO), follow these instructions.
Decomposition Scope
Set the decomposition scope to limit how many instances of a fulfillment order line item appear in fulfillment.
