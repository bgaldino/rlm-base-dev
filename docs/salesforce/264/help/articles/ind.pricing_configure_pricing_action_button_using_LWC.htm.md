---
article_id: ind.pricing_configure_pricing_action_button_using_LWC.htm
title: Customize the Pricing Action Button by Using Lightning Components
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_pricing_action_button_using_LWC.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_action_parameters.htm
fetched_at: 2026-09-07
---

# Customize the Pricing Action Button by Using Lightning Components

Add the Pricing Calculation standard Lightning component to object record pages to make custom pricing actions available across your org and calculate the price of a product directly from the record page.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To customize an Experience Cloud site:	

Be a member of the site AND Create and Set Up Experiences

OR

Be a member of the site AND an experience admin, publisher, or builder in that site

NOTE

The Calculate Price button is only for pricing Salesforce objects and doesn't support custom data hydration.

The more complex Quotes and Orders logic, which uses custom hydration for bundles and derived products, requires a custom-built pricing button that can act on persisted (saved) data. Therefore, the standard button should not be considered a replacement for Transaction Management's pricing logic.

On any object’s record page, click , and select Edit Page.
On the Builder page, from the Components panel, drag Pricing Calculation to the position where you want it to appear on the Lightning page canvas.
Use the Page panel to give your action a name.
Select the context definition, the context mapping, and the pricing procedure.
Save your changes, and exit Lightning App Builder.
