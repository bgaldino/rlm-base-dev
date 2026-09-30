---
article_id: release-notes.rn_product_configurator_flow_updates.htm
title: Updates in Default Product Configurator Flow
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_flow_updates.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_configurator.htm
fetched_at: 2026-09-30
---

# Updates in Default Product Configurator Flow

The Default Product Configurator flow has new attributes. If you cloned the Default Product Configurator flow before Winter ’27, manually map the new attributes in your customized flow, or clone the default flow and apply your customizations again.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

Why: Update your Configurator flow with the latest attributes so that new features work as expected and you get a seamless configuration experience.

The context definition that determines which context attributes are available for the Configuration API to query
Use the new Context Definition attribute of both Input and Output types on the Product Configurator Data Manager flow component.
The context node within a selected context definition that contains the attributes that are available for the Configuration API to query
Use the new Context Node attribute of both Input and Output types on the Product Configurator Data Manager flow component.
The context attributes that are available in a selected context node for the Configuration API to query
Use the new Context Attributes attribute of both Input and Output types on the Product Configurator Data Manager flow component.
The API name of the transaction record's parent object
Use the new Origin attribute of the Input type on the Product Configurator Option Groups component.
A boolean value that indicates whether instant pricing is turned on by default at runtime
Use the new Instant Pricing attribute of the Input type on the Product Configurator Data Manager flow.
A boolean value that indicates whether the product name field on the option cards is read-only
Use the new Read-Only Product Name attribute of the Input type on the Product Configurator Option Groups flow component.
SEE ALSO
Salesforce Help: Clone and Customize the Default Product Configurator Flow
