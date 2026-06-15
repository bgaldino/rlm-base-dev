---
article_id: ind.product_catalog_simulate_and_activate_a_qualification_rule_procedure.htm
title: Simulate and Activate a Qualification Rule Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_simulate_and_activate_a_qualification_rule_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Simulate and Activate a Qualification Rule Procedure

Before you activate your qualification rule procedure, run simulations to test whether the rules you defined in the decision table are accurate and give you the desired output. If your rule procedure doesn’t work as expected, edit the values and simulate again. When you’re satisfied, activate the rule procedure version.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create a qualification rule procedure:	Manage Product Catalog
To use a decision table:	Rules Engine Runtime
To create a context definition:	Context Service Admin
From the Product Catalog Management app’s home page, click Qualification Rules Procedures.
From the Qualification Procedures list view page, open the qualification rule procedure version in the Expression Set Builder.
Click Simulate.
To pass sample data to the expression set for simulation, select an input mode from the input tab.
Simplified	Enter sample values for the variables defined in the qualification rule procedure in the form. To export the sample data as JSON input, click Export JSON Input (1).
Advanced	Enter sample values for the variables defined in the qualification rule procedure in the JSON Input text box. Alternatively, download the sample JSON Input file (2), modify the file with your input values, and paste the updated JSON in the text box.
 
Add the product ids or product category IDs for the products for which you want to run the simulation. Leave the Is Qualified field blank.
Click Simulate.
The simulation results are visible in a tabular format under the Output tab. To view additional details, click View Details. The simulation results give you the reason for a product or product category disqualification. The qualified column indicates the product or product category qualification status.
If you're happy with the simulation result, you’re ready to activate the qualification rule procedure. Perform these steps before activating your procedure:
In the left pane, click Expression Set Properties , and enter a rank under Advanced Details. The rank can be any positive number.
In the left pane, click Element Details
and select Include in Output.
Save the qualification rule procedure.
Click Activate.

All the pieces are now in place for your qualification rule. As a best practice, check the Product Discovery Settings to ensure that you have the correct Context Definition and Qualification Procedure selected there.

To check these settings, go to Setup | Product Discovery | Product Discovery Settings.
