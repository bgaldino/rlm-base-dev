---
article_id: ind.product_configurator_set_up_flow.htm
title: Set Up Your Product Configuration Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_set_up_flow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_explore_the_product_configurator_flow.htm
fetched_at: 2026-09-04
---

# Set Up Your Product Configuration Flow

Clone the Default Product Configurator Flow and customize it according to your business needs to manage the Product Configurator interface layout and the product information shown on it. Maintain your customized configuration flows and update them with the latest attributes to make sure new features work as expected, and you retain a smooth configuration experience.

Clone and Customize the Default Product Configurator Flow
Use the Default Product Configurator Flow as a template to design a product configurator flow that determines the layout for presenting customizable product-related information in the user interface.
Configure Editable Context Fields for Product Option Cards
Enable sales reps to edit context fields directly from the product option cards during bundle configurations. Context fields are derived from the configured context definition and differ from product attribute fields.
Configure Attribute Display on Product Option Cards
Show product attributes on the product option cards, where sales reps can edit them during bundle configurations.
Make Product Names Editable in Product Option Cards
Give sales reps access to edit product names from the product option cards during bundle configurations.
Select Context Attributes to Improve Configurator Performance
Select specific context attributes that you want the Configuration API to query and return, instead of it returning all of them by default. Your selection narrows the query and the response to the data that your configurations need, so Product Configurator responds faster, even for large transactions.
Enable Non-Blocking Behavior in the Configurator
Enable non-blocking behavior so that configurator users can change multiple attribute and option values on a product asynchronously. The configuration page loads the changes without waiting for the constraint engine to process each setting individually. After processing is complete, the user can save the configuration.
