---
article_id: ind.pricing_configure_pricing_procedure.htm
title: Configure Your Pricing Procedure
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_pricing_procedure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_procedures.htm
fetched_at: 2026-09-07
---

# Configure Your Pricing Procedure

Assemble a pricing procedure using pricing elements and ensure accurate pricing for your products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User
To use pricing procedures:	Salesforce Pricing Run Time User
NOTE
Before building pricing procedures, ensure that you have added decision tables, enabled context definitions on your Salesforce org, set up a product selling model, and added products to a price book.
For pricing procedures created before Winter '27, Salesforce Pricing assigns Revenue Cloud as the default subtype.
When you create or clone a pricing procedure, the Subtype field shows only the clouds that match your active org licenses.
Create a Pricing Procedure

When you create a pricing procedure, the initial version is a blank and ready-to-use template. To perform pricing calculations, you must add pricing elements and call the appropriate decision tables. The Subtype field identifies which cloud a procedure belongs to - such as Revenue Cloud, Life Sciences Cloud, Commerce, or Insurance. Each cloud can implement its own functionality and validations for procedures of that subtype. Element lookups show decision tables from all pricing recipes assigned to that procedure's subtype.

From App Launcher, find and select Pricing Procedures.
Click New.
Specify these details.
Enter a name and then press Tab to autopopulate the API Name.
Select Pricing as the usage type.
Select a usage subtype.
The dropdown only shows the subtypes available based on your org's licenses. You can change the subtype when cloning the procedure, but not while editing it.
Associate the pricing procedure with a context definition.
For the purposes of all our examples, we've used the SalesTransactionContext context definition.
Save your changes.
On the Details tab, in the Pricing Procedure Versions section, click the pricing procedure version that you want to work on.
The Pricing Procedure Builder opens as a new tab.
Click , and select a pricing element from the list.
In the Lookup Table Details field, select the decision table and enter the values.
Depending on whether you want to show or hide the pricing information in the Waterfall view, select or deselect the price waterfall view for your element.
IMPORTANT

The Exclude Price Waterfall option isn't supported by Quotes in Revenue Management.

You can't exclude price waterfall for the Pricing Setting, Aggregate Price, Price Tracking, Stop Pricing, and Discovery Procedure elements.

Select the profiles that can see the pricing information in Waterfall view after simulation.
Click , and enter 1 as the rank number.
NOTE When more than one enabled version matches a pricing procedure, choose the version with the highest rank. For example, if two enabled versions have rank values set to 1 and 2, choose the version with rank 2.
Click , select Include in Output.
Save your procedure.
Store and Reuse Values with Local List Variables

A local list variable stores a calculated value from one pricing element so you can reuse it in a another element, without creating a context tag or constant. Local list variables are a separate category from context tags, constants, and the older variables resource type. You create it directly inside Pricing Procedure Builder, as you build your procedure.

In Pricing Procedure Builder canvas, click Resource Manager to expand the side panel and click Add Resource.
In the Add New Resource dialog, select Local List Variable as the Resource Type.
Select a variable type:
Node: Restricts the variable's scope to a specific structural node, such as the main Sales Transaction node.
Attribute: Scopes the variable to a specific child field or object attribute, such as a field on a Sales Transaction Item or Sales Transaction Group node beneath your selected parent.
Select a Parent Node, for example - SalesTransactionItem and enter a Resource Name.
Click Done, or Done And New to keep creating more local list variables.
In a pricing element, map the local list variable to an output field. This initializes variable's value during execution.
In a subsequent pricing element, map the same local list variable to an input field to reuse its stored value.
Key Configuration Considerations
The Include in Output checkbox controls whether the procedure includes an element's variables in the final response. You must select this for at least one element to ensure the procedure returns data for downstream processing.
Users map both Effective From and Effective To variables to the same EffectiveFrom tag for one-time products like laptops. Conversely, subscription-based products require distinct mappings to account for specific service durations.
The Pricing Setting element automatically maps standard variables like Net Unit Price and Subtotal by default. You only need to map these variables manually when you intend to override the system’s default values.
Don't activate a pricing procedure immediately after you modify its associated decision tables. To prevent the procedure from deploying with outdated metadata, make a minor change to the pricing procedure, save it again, and then activate it.
Map your local list variable as an output in a preceding element before referencing it as an input in a downstream element. If a pricing element references a variable as an input before an element initializes it, the pricing engine resolves the variable value to null.
The pricing engine does not support passing local list variables as inputs or initializing them externally via JSON payloads. They remain strictly local to the procedure execution context.
Standard actions like renaming and modifying the variable's data type are not supported at any time. Data types can only be deleted. Deleting a local list variable automatically clears all its active mappings throughout the pricing procedure version to prevent reference errors.
The system does not support local list variables within the Map Line Item element or the Propagation element.
Local list variables migrate automatically when you deploy or migrate pricing procedures across Salesforce orgs, eliminating manual recreation steps in target orgs.
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
