---
article_id: ind.pricing_create_new_pricing_recipe.htm
title: Create a Pricing Recipe
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_new_pricing_recipe.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_recipes.htm
fetched_at: 2026-09-07
---

# Create a Pricing Recipe

Learn how to create a custom pricing recipe to group and associate your custom decision tables, enabling precise control over pricing calculations in your Salesforce org. This task is essential when the predefined recipe doesn't meet your specific business needs. Use the Subtype field to set up the default pricing recipe and decision tables for each cloud, such as Revenue Cloud or Life Sciences Cloud. While building or editing a pricing procedure, element lookups display only the decision tables linked to the default recipe of that procedure's subtype.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To manage pricing recipes:	

Salesforce Pricing Design Time

IMPORTANT
You must set up your decision tables before you use a custom pricing recipes.
For pricing procedures created before Winter '27, Salesforce Pricing assigns Revenue Cloud as the default subtype.
When you create or clone a pricing recipe, the Subtype field shows only the clouds that match your active org licenses.
From Setup, in the Quick Find box, find and select Pricing Recipes.
Enter a name for the new recipe.
Select a subtype from the dropdown.
The Subtype field shows only the subtypes that are available based on your active cloud licenses. Each subtype can have multiple recipes, including one default recipe that you can change. You can change the subtype when cloning a recipe, but not while editing a recipe.
Save your changes.
Select the recipe that you created to open its details page.
On the recipe's detail page, select the Price Adjustment Matrix tab.
To add decision tables, click Modify and then select the decision tables you want to associate with this recipe.
When you create a pricing procedure with the usage type set to Pricing, you will see the predefined decision tables and any custom ones you associated with this recipe.
Save your changes.
