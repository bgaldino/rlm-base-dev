---
article_id: ind.rm_element_add_rounding_values.htm
title: Add the Rounding Values Element
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_element_add_rounding_values.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_element_rounding_values.htm
fetched_at: 2026-09-07
---

# Add the Rounding Values Element

Use the Rounding Values element to ensure that all rating elements added to the rating procedure work for different currencies in a single currency org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS
NEEDED
To create, update, and delete rating procedures:	Rate Management Design Time User
IMPORTANT Create a rating procedure to calculate the rate of a product by using the Manual Rate Discount or Volume-Based Rate Discount elements.
From the App Launcher, find and select Rating Procedures.
To open the rating procedure record, click the procedure name.
To open the rating procedure in the Rating Procedure builder, click the rating procedure version.
Define the Rating Setting element and the base rate of the usage resource.
See Rating Setting and Base Rate.
Click , and then select the Rounding Values element from the list.
If you’re on a single currency org, specify a value for the Precision variable.
If you don’t map the Precision variable to the correct context tag or constant resource, the rounding rule isn't applied to the resource’s final rate.
Assign an input variable, such as TotalAmount, to an output variable and select the rounding rule.
To add more rules and variables, select Add more variables and rules.
Save your procedure and then simulate it.
The rate details in the Waterfall View show the rounded rate for the usage resource.
