---
article_id: ind.rm_add_rating_get_rate_cards.htm
title: Add Get Rate Cards Element
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_add_rating_get_rate_cards.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rating_element_get_rate_cards.htm
fetched_at: 2026-09-07
---

# Add Get Rate Cards Element

Here’s how you can add the Get Rate Cards element to your rating procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create, update, and delete rating procedures:	Rate Management Design Time User
From the App Launcher, find and select Rating Procedures.
To open the rating procedure record, click the procedure name.
To open the rating procedure in the Rating Procedure builder, click the rating procedure version.
Define the Rating Setting element. See Rating Element.
Click , and then find and select the Get Rate Cards element from the list.
In the Lookup Table Details field, search for and select your custom made lookup table.
Map your variables to the appropriate context tags.
Click , and enter 1 as the rank number.
Click , select Include in Output, and save your rating procedure.
Click Simulate.
On the Input tab, enter the variables to simulate and verify your calculations,
Enter variable values either in JSON format (Advanced) or in the fields (Simplified).
Click Simulate and verify that the calculations are per your rating settings.
The Waterfall View shows every step of the rating calculation.
When you’re happy with the simulation result, click Activate.
