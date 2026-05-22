---
article_id: ind.rm_configure_your_rating_discovery_procedure.htm
title: Configure Your Rating Discovery Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_configure_your_rating_discovery_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Configure Your Rating Discovery Procedure

To retrieve rate cards, rate card entries, and related adjustments based on the filter criteria for the context input, use Rating discovery procedures.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create, update, and delete rating procedures:	Rate Management Design Time User
To use rating procedures:	Rate Management Run Time User
From the App Launcher, find and select Rating Discovery Procedures.
Click New.
Specify these details.
Enter a name and then press Tab to autopopulate the API Name.
Select Rating Discovery as the usage type.
Select a context definition.
Save your changes.
Salesforce shows the record page of the new rating discovery procedure.
On the Details tab, in the Rating Discovery Procedure Versions section, click the rating discovery procedure version that you want to work on.
Salesforce opens the Rating Discovery Procedure builder in a new tab.
Click , and select a rating discovery element from the list in this order.
Get Rate Cards
Get Rate Card Entries
Get Tier-Based Rate Adjustments or Get Attribute-Based Rate Adjustments
Alternatively, you can also drag the rating element from the Elements panel to the builder canvas. To open the Elements panel, click .
In the Lookup Table Details field, select the lookup table.
Enter the values for input and output variables.
Save your procedure.
