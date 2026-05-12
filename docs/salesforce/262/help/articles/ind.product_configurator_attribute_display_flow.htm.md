---
article_id: ind.product_configurator_attribute_display_flow.htm
title: Configure Attribute Display on Product Option Cards
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_attribute_display_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Configure Attribute Display on Product Option Cards

Show product attributes on the product option cards, where sales reps can edit them during bundle configurations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create and edit a product configuration flow:	Product Configurator
From Setup, in the Quick Find box, enter Flow, and then select Flows.
Open your product configurator flow.
Edit the screen element and select the Product Configurator Option Groups component.
To show product attributes on the option cards, for the Display Option Card Attributes attribute, select {!$GlobalConstant.True}.
For the Option Card Attributes Limit attribute, specify the number of product attributes that you want to show on the option cards.
You can show up to 5 attributes.
Save your changes and activate the flow.

The attributes that appear on each option card are determined by the sequence you define for the product attributes. Set the sequence by updating the Sequence field in the Attribute Definition Information section when you edit the product attribute or the product classification attribute. For example, if you set the attributes limit to 5, only the product attributes with sequence numbers 1 through 5 appear on the option card.
