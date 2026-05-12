---
article_id: ind.pricing_configure_pricing_procedure.htm
title: Configure Your Pricing Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_pricing_procedure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Configure Your Pricing Procedure

Assemble a pricing procedure using pricing elements and ensure accurate pricing for your products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User
To use pricing procedures:	Salesforce Pricing Run Time User
NOTE Before building pricing procedures, ensure that you have added decision tables, enabled context definitions on your Salesforce org, set up a product selling model, and added products to a price book.
Create a Pricing Procedure

When you create a pricing procedure, the initial version is a blank and ready-to-use template. To perform pricing calculations, you must add pricing elements and call the appropriate decision tables.

From App Launcher, find and select Pricing Procedures.
Click New.
Specify these details.
Enter a name and then press Tab to autopopulate the API Name.
Select Pricing as the usage type.
Associate the pricing procedure with a context definition.
For the purposes of all our examples, we've used the SalesTransactionContext context definition.
Save your changes.
On the Details tab, in the Pricing Procedure Versions section, click the pricing procedure version that you want to work on.
The Pricing Procedure Builder opens as a new tab.
Click , and select a pricing element from the list.
In the Lookup Table Details field, select the decision table and enter the values.
Depending on whether you want to show or hide the pricing information in the Waterfall view, select or deselect the price waterfall view for your element.
IMPORTANT

The Exclude Price Waterfall option isn't supported by Quotes in Agentforce Revenue Management.

You can't exclude price waterfall for the Pricing Setting, Aggregate Price, Price Tracking, Stop Pricing, and Discovery Procedure elements.

Select the profiles that can see the pricing information in Waterfall view after simulation.
Click , and enter 1 as the rank number.
NOTE When more than one enabled version matches a pricing procedure, choose the version with the highest rank. For example, if two enabled versions have rank values set to 1 and 2, choose the version with rank 2.
Click , select Include in Output.
Save your procedure.
Key Configuration Considerations
The Include in Output checkbox controls whether the procedure includes an element's variables in the final response. You must select this for at least one element to ensure the procedure returns data for downstream processing.
Users map both Effective From and Effective To variables to the same EffectiveFrom tag for one-time products like laptops. Conversely, subscription-based products require distinct mappings to account for specific service durations.
The Pricing Setting element automatically maps standard variables like Net Unit Price and Subtotal by default. You only need to map these variables manually when you intend to override the system’s default values.
Refresh Your Decision Tables

We recommend refreshing your decision tables to ensure that the latest pricing data is available.

To refresh your decision table, from Setup, in the Quick Find box, search for and select Decision Tables.
Select the appropriate decision table. For example, select the Volume Discount Entries decision table if you’ve made changes to price adjustment tier records.
Click Refresh.
Validate Your Decision Tables

Next, verify if the decision able has been refreshed and has the latest pricing data.

From the App Launcher, search for and open Lookup Tables.
Find and select Volume Discount Entries.
You can either check the Last Refreshed Date or you can search for the newly created price adjustment tier records.
