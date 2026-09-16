---
article_id: ind.rm_simulate_activate_rating_procedure.htm
title: Simulate and Activate Your Rating Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_simulate_activate_rating_procedure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: rating
parent_article: ind.rm_rate_management_setup.htm
fetched_at: 2026-09-07
---

# Simulate and Activate Your Rating Procedure

Before you activate your rating procedure, run simulations to test if the variables that you entered are accurate. If your rating procedure doesn’t work as expected, edit the values that you entered and try again. When you’re satisfied, activate the rating procedure version.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create, update, and delete rating procedures:	Rate Management Design Time User
To use rating procedures:	Rate Management Run Time User
From the App Launcher, find and select Rating Procedures.
To open the rating procedure record, click the procedure name.
To open the rating procedure in the Rating Procedure builder, click the rating procedure version name.
Add your elements, map them to the appropriate tags, choose a rank, enable the option to include in output, and then save your rating procedure.
Click Simulate.
Salesforce shows the Simulation Details with the input mode selected as Simplified by default.
If necessary, change the input mode.
Simplified	To define values for the variables in the fields corresponding to each variable.
Advanced	To define values for the variables in the JSON format. You can modify the values directly or download the JSON input file, modify its values, and paste the file back in the JSON Input box.
Enter values for the input variables.
To locate the value of a variable, go to the related record. For example, to locate a rate card ID, open the rate card record page. The rate card ID appears in the browser’s URL.
In the Input tab, click Simulate.
The Waterfall View shows every step of the rating calculation that determine the resource's final net rate.
When you’re happy with the simulation result, click Activate.
